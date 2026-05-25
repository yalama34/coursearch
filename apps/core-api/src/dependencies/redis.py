from typing import Annotated

from fastapi import Depends
import redis.asyncio as redis

from src.settings import REDIS_HOST, REDIS_PORT


redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
)

async def get_redis() -> redis.Redis:
    return redis_client

RedisDep = Annotated[redis.Redis, Depends(get_redis)]
