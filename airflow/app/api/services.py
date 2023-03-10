import asyncio
import json
from decimal import Decimal

from core.config import settings
from core.db import redis
from models import SearchStatusEnum, SearchModel
from rocketry_app import update_currency
from utils import make_request


async def commit_search_obj(search_obj: SearchModel) -> None:
    search_obj_dump = json.dumps(search_obj.dict())
    await redis.set(search_obj.search_id, search_obj_dump)


async def search_task(search_id: str):
    search_obj = SearchModel(
        search_id=search_id,
        status=SearchStatusEnum.PENDING,
        items=[],
    )
    search_obj_dump = json.dumps(search_obj.dict())
    if await redis.setnx(search_id, search_obj_dump):
        data_a = asyncio.create_task(
            make_request(settings.PROVIDER_A_URL),
        )
        data_b = asyncio.create_task(
            make_request(settings.PROVIDER_B_URL),
        )
        search_obj.items += await data_a
        await commit_search_obj(search_obj)
        search_obj.items += await data_b
        search_obj.status = SearchStatusEnum.COMPLETED
        await commit_search_obj(search_obj)
    else:
        raise KeyError(f"Key {search_id} is already busy")


async def get_currency_rates() -> dict:
    currency_rates = await redis.get("CURRENCIES")
    if not currency_rates:
        currency_rates = await update_currency()
    else:
        currency_rates = json.loads(currency_rates)
    return {
        key: Decimal(value) for key, value in currency_rates.items()
    }


def calculate_currency(item: dict, currency_rates: dict, new_currency: str):
    item['price'] = {'currency': new_currency}
    item_currency = item['pricing']['currency']
    item_total = Decimal(item['pricing']['total'])
    item_base = Decimal(item['pricing']['base'])
    item_taxes = Decimal(item['pricing']['taxes'])
    if item_currency == 'KZT':
        total_in_kzt = item_total
        base_in_kzt = item_base
        taxes_in_kzt = item_taxes
    elif currency_rate := currency_rates.get(item_currency):
        total_in_kzt = item_total * currency_rate
        base_in_kzt = item_base * currency_rate
        taxes_in_kzt = item_taxes * currency_rate
    else:
        raise ValueError(400, f"Currency {item_currency!r} not found")

    if new_currency == 'KZT':
        item['price']['amount'] = "%.2f" % Decimal(total_in_kzt)
        item['price']['base'] = "%.2f" % Decimal(base_in_kzt)
        item['price']['taxes'] = "%.2f" % Decimal(taxes_in_kzt)
    elif new_currency_rate := currency_rates.get(new_currency):
        item['price']['amount'] = "%.2f" % Decimal(total_in_kzt / new_currency_rate)
        item['price']['base'] = "%.2f" % Decimal(base_in_kzt / new_currency_rate)
        item['price']['taxes'] = "%.2f" % Decimal(taxes_in_kzt / new_currency_rate)
    else:
        raise ValueError(400, f"Currency {new_currency!r} not found")
    return item