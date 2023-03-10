import asyncio

from fastapi import FastAPI

from utils import get_file

app = FastAPI()


@app.post('/search')
async def search():
    await asyncio.sleep(60)
    return get_file('response_b.json')
