import json
import uuid

from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.background import BackgroundTasks
from starlette.responses import JSONResponse

from api.services import search_task, get_currency_rates, calculate_currency
from core.db import redis

router = APIRouter()


@router.post('/search')
async def search(
        background_tasks: BackgroundTasks
) -> JSONResponse:
    search_id = str(uuid.uuid4())
    background_tasks.add_task(search_task, search_id)
    print('asdasdasd')
    return JSONResponse(content={"search_id": search_id}, status_code=status.HTTP_200_OK)


@router.get('/results/{search_id}/{currency}')
async def search(
        search_id: str,
        currency: str
) -> JSONResponse:
    search_results = await redis.get(search_id)
    if not search_results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    search_results = json.loads(search_results)
    currency_rates = await get_currency_rates()
    search_results['items'] = list(map(
        lambda x: calculate_currency(x, currency_rates, currency), search_results['items']
    ))
    return JSONResponse(content=search_results, status_code=status.HTTP_200_OK)
