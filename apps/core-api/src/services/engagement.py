from redis.asyncio import Redis

from src.db.repositories.engagement_repository import EngagementRepository
from src.schemas.engagement import UpdateEngagementRequest


class EngagementService:
    def __init__(
        self,
        redis_client: Redis,
    ):
        self.repository = EngagementRepository(redis_client)

    async def add_engagement(
        self,
        user_id: int,
        request: UpdateEngagementRequest,
    ) -> None:
        """Add user engagement"""
        await self.repository.add_engagement(
            user_id=user_id,
            course_id=request.course_id,
            value=request.value,
        )
