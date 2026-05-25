from redis.asyncio import Redis


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


    async def add_engagement(
        self,
        user_id: int,
        course_id: int,
        value: int,
    ) -> None:
        """Increment engagement seconds"""
        key = self._build_key(
            user_id,
            course_id,
        )

        await self.redis.incrby(
            key,
            value,
        )

        await self.redis.expire(
            key,
            60 * 60 * 24,
        )
