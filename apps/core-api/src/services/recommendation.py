from src.integrations.ml_service.schemas import ExplanationsResponse, RecommendationResponse
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
            placeholder: bool = False,
    ) -> RecommendationResponse:
        """
        Get user recommendations by user ID
        Return empty recommendations if placeholder is True
        """
        if placeholder:
            return RecommendationResponse(
                user_id=user_id,
                items=[]
            )

        return await self.ml_client.get_recommendations(user_id, limit)

    async def get_explanations(
            self,
            user_id: int,
            course_ids: list[int],
    ) -> ExplanationsResponse:
        return await self.ml_client.get_explanations(user_id, course_ids)
