import asyncio

from fastapi import FastAPI

from utils import get_file

app = FastAPI()


@app.post('/search')
async def search():
    await asyncio.sleep(30)
    return get_file('response_a.json')
