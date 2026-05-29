from typing import Annotated

from fastapi import Depends
import redis.asyncio as redis

from src.settings import settings


redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True,
)

async def get_redis() -> redis.Redis:
    return redis_client

RedisDep = Annotated[redis.Redis, Depends(get_redis)]
