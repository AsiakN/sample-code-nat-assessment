import os
from contextlib import asynccontextmanager

import aioredis
import uvicorn
from fastapi import FastAPI

from src.bootstrap.containers import Container
from src.transaction.api import transaction_route
from src.transaction.services.redis_service import RedisService

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    connect to redis on startup
    :param app:
    :return:
    """
    REDIS_URL = os.getenv("REDIS_URL")
    redis = await aioredis.from_url(REDIS_URL)
    app.state.redis_service = RedisService(redis)  # Store RedisService in app state
    yield
    await redis.close()


def create_app() -> FastAPI:
    container = Container()
    container.wire(modules=[
        transaction_route
    ])

    app = FastAPI(title="Assessment API", lifespan=lifespan)
    app.container = container

    app.include_router(transaction_route.router)

    return app


app = create_app()


@app.get("/")
async def _():
    return {"detail": "API is up and running"}

if __name__ == "__main__":
    if os.getenv('APP_ENV') == 'development':
        uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="debug", reload=True)
    else:
        uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="debug")
