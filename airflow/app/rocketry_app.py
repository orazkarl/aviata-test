import json
from datetime import datetime

import aiohttp
import xmltodict
from rocketry import Rocketry
from rocketry.conditions.api import daily, minutely

from core.db import redis


app_rocketry = Rocketry(config={'task_execution': 'async'})


@app_rocketry.task(daily.at('6:00'))
async def update_currency():
    today = datetime.today().strftime("%d.%m.%Y")

    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://www.nationalbank.kz/rss/get_rates.cfm?fdate={today}') as response:
            response.raise_for_status()
            currency_xml = await response.text()

    data = xmltodict.parse(currency_xml)
    currencies = {}
    for item in data['rates']['item']:
        currencies[item['title']] = item['description']
    await redis.set("CURRENCIES", json.dumps(currencies))
    return currencies
