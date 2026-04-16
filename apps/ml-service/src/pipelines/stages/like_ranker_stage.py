from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.recommendation.pipeline_order import StageName
from src.schemas.recommendations import RecommendationItem


class LikeRankerStage:
    def __init__(self, session: AsyncSession):
        self.__db_session = session

    @property
    def stage_name(self) -> str:
        return StageName.LIKE_RANKER

    async def process(self, user_id: int, candidates: list[RecommendationItem], limit: int):
        return candidates
