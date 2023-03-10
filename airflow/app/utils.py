from typing import Dict

import aiohttp


async def make_request(
        url: str
) -> Dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(url) as response:
            response.raise_for_status()
            return await response.json()
