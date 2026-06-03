"""Async Redis client helpers for the ML service."""

import logging
from typing import Optional

import redis.asyncio as aioredis
from fastapi import Request

from src.config import REDIS_HOST, REDIS_PORT

logger = logging.getLogger(__name__)


def create_redis_client() -> Optional[aioredis.Redis]:
    """Create a Redis client, or return None if Redis is not configured."""
    if not REDIS_HOST:
        logger.info("REDIS_HOST not set; Redis caching disabled")
        return None
    return aioredis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
    )


async def close_redis_client(client: Optional[aioredis.Redis]) -> None:
    if client is not None:
        await client.aclose()


def get_redis(request: Request) -> Optional[aioredis.Redis]:
    """FastAPI dependency: Redis client from app state (may be None)."""
    return getattr(request.app.state, "redis", None)
