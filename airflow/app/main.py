import asyncio
import logging

import uvicorn
from fastapi import FastAPI

from api.endpoints.search import router as api_router
from rocketry_app import app_rocketry


class Server(uvicorn.Server):
    """Customized uvicorn.Server

    Uvicorn server overrides signals and we need to include
    Rocketry to the signals."""

    def handle_exit(self, sig: int, frame) -> None:
        app_rocketry.session.shut_down()
        return super().handle_exit(sig, frame)


app = FastAPI(
    title='AVIATA TEST',
    docs_url="/docs",
    debug=True
)

app.include_router(api_router)


async def main():
    """Run Rocketry and FastAPI"""
    server = Server(config=uvicorn.Config(
        app,
        host="0.0.0.0",
        workers=1,
        loop="asyncio",
        port=9000,
    ))

    api = asyncio.create_task(server.serve())
    scheduler = asyncio.create_task(app_rocketry.serve())

    await asyncio.wait([scheduler, api])


if __name__ == "__main__":
    # Print Rocketry's logs to terminal
    logger = logging.getLogger("rocketry.task")
    logger.addHandler(logging.StreamHandler())

    # Run both applications
    asyncio.run(main())
