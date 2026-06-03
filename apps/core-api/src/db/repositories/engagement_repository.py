import time

from redis.asyncio import Redis

from src.domain.constants.engagement import (
    MAX_HEARTBEAT_SECONDS,
    REDIS_TTL_SECONDS,
)


class EngagementRepository:
    def __init__(
        self,
        redis_client: Redis,
    ):
        self.redis = redis_client

    @staticmethod
    def _build_key(
        user_id: int,
        course_id: int,
    ) -> str:
        return (
            f"engagement:"
            f"user:{user_id}:"
            f"course:{course_id}"
        )

    def _normalize_delta(
        self,
        value: int,
        last_tick_at: str | None,
        now: float,
    ) -> int:
        accepted = value

        if last_tick_at is not None:
            gap = now - float(last_tick_at)
            if gap < 0:
                gap = 0
            if gap > MAX_HEARTBEAT_SECONDS:
                gap = MAX_HEARTBEAT_SECONDS
            if accepted > gap:
                accepted = int(gap)
        elif accepted > MAX_HEARTBEAT_SECONDS:
            accepted = MAX_HEARTBEAT_SECONDS

        return max(accepted, 0)

    async def add_engagement(
        self,
        user_id: int,
        course_id: int,
        value: int,
    ) -> None:
        """Increment engagement seconds"""
        key = self._build_key(user_id, course_id)
        key_type = await self.redis.type(key)

        if key_type == "string":
            accepted = min(value, MAX_HEARTBEAT_SECONDS)
            if accepted > 0:
                await self.redis.incrby(key, accepted)
            await self.redis.expire(key, REDIS_TTL_SECONDS)
            return

        now = time.time()
        last_tick_at = await self.redis.hget(key, "last_tick_at")
        accepted = self._normalize_delta(value, last_tick_at, now)

        if accepted > 0:
            await self.redis.hincrby(key, "pending_seconds", accepted)

        await self.redis.hset(key, "last_tick_at", now)
        await self.redis.expire(key, REDIS_TTL_SECONDS)

    async def drain_pending(self, key: str) -> int:
        key_type = await self.redis.type(key)

        if key_type == "string":
            value = await self.redis.getdel(key)
            return int(value or 0)

        if key_type != "hash":
            return 0

        pending = await self.redis.hget(key, "pending_seconds")
        if not pending:
            return 0

        pending = int(pending)
        if pending <= 0:
            return 0

        await self.redis.hset(key, "pending_seconds", 0)
        return pending

    async def iter_engagement_keys(self):
        async for key in self.redis.scan_iter(
            match="engagement:user:*:course:*",
            count=100,
        ):
            parts = key.split(":")
            if len(parts) != 5:
                continue

            yield int(parts[2]), int(parts[4]), key
