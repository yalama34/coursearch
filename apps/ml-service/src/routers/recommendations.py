from fastapi import APIRouter

from src.schemas.recommendations import RecommendationResponse
from src.pipelines.recommendation_pipeline import RecommendationPipeline
from src.db.database import get_session

router = APIRouter()

@router.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
        user_id: int,
        limit: int = 10
):
    """
    Return specific recommendations for user using ``RecommendationPipeline``
    :param user_id:
    :param limit:
    :return:
    """
    async for session in get_session():
        pipeline = RecommendationPipeline(session=session)
        pipeline.register_pipeline()
        results = await pipeline.execute(user_id=user_id, limit=limit)

        return RecommendationResponse(user_id=user_id, items=results)
