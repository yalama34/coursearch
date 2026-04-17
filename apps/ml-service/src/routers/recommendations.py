from fastapi import APIRouter, Depends

from src.config import RECOMMENDATIONS_CACHE_TTL_SECONDS
from src.schemas.recommendations import RecommendationResponse
from src.pipelines.recommendation_pipeline import RecommendationPipeline
from src.db.database import get_session
from src.db.redis import get_redis

router = APIRouter()


def _recommendations_cache_key(user_id: int, limit: int) -> str:
    return f"recs:user:{user_id}:limit:{limit}"


@router.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    user_id: int,
    limit: int = 10,
    redis=Depends(get_redis),
):
    """
    Return specific recommendations for user using ``RecommendationPipeline``.
    Cached in Redis when configured (key ``recs:user:{user_id}:limit:{limit}``).
    """
    cache_key = _recommendations_cache_key(user_id, limit)
    if redis is not None:
        cached = await redis.get(cache_key)
        if cached is not None:
            return RecommendationResponse.model_validate_json(cached)

    async for session in get_session():
        pipeline = RecommendationPipeline(session=session, redis=redis)
        await pipeline.register_pipeline()
        results = await pipeline.execute(user_id=user_id, limit=limit)

        response = RecommendationResponse(user_id=user_id, items=results)
        if redis is not None:
            await redis.set(
                cache_key,
                response.model_dump_json(),
                ex=RECOMMENDATIONS_CACHE_TTL_SECONDS,
            )
        return response
