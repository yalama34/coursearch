import logging

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.engagement_repository import EngagementRepository
from src.db.repositories.stats_repository import StatsRepository

logger = logging.getLogger(__name__)


class EngagementFlushService:
    def __init__(
        self,
        redis_client: Redis,
        session: AsyncSession,
    ):
        self.engagement_repository = EngagementRepository(redis_client)
        self.stats_repository = StatsRepository(session)

    async def flush_all(self) -> int:
        flushed_total = 0

        async for user_id, course_id, key in self.engagement_repository.iter_engagement_keys():
            pending = await self.engagement_repository.drain_pending(key)
            if pending <= 0:
                continue

            await self.stats_repository.increment_watch_seconds(
                user_id=user_id,
                course_id=course_id,
                delta=pending,
            )
            flushed_total += pending

        return flushed_total
