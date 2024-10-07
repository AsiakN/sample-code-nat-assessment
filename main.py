import os
from contextlib import asynccontextmanager

import aioredis
from fastapi import FastAPI

from src.bootstrap.containers import Container
from src.transaction.api import transaction_route
from src.transaction.services.redis_service import RedisService

LOCAL_REDIS_URL = "redis://127.0.0.1:6379"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    connect to redis on startup
    :param app:
    :return:
    """
    redis = await aioredis.from_url(LOCAL_REDIS_URL)
    app.state.redis_service = RedisService(redis)  # Store RedisService in app state
    yield
    await redis.close()


def create_app() -> FastAPI:
    container = Container()
    container.wire(modules=[
        transaction_route
    ])

    app = FastAPI(title="Fido Assessment API", lifespan=lifespan)
    app.container = container

    app.include_router(transaction_route.router)

    return app


app = create_app()


@app.get("/")
async def _():
    return {"detail": "Fido API is up and running"}
