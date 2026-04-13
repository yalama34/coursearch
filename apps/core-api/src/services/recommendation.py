from src.integrations.ml_service.schemas import RecommendationResponse
from src.dependencies.ml_client import MLClientDep


class RecommendationService:
    def __init__(
            self,
            ml_client: MLClientDep
    ):
        self.ml_client = ml_client

    async def get_recommendations(
        self,
        user_id: int,
        limit: int = 10,
    ) -> RecommendationResponse:
        return await self.ml_client.get_recommendations(user_id, limit)
