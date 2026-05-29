from fastapi import APIRouter, Depends, HTTPException

from src.config import RECOMMENDATIONS_CACHE_TTL_SECONDS
from src.schemas.recommendations import RecommendationResponse, ExplanationsResponse
from src.pipelines.recommendation_pipeline import RecommendationPipeline
from src.db.database import get_session
from src.db.redis import get_redis
from src.services.explanation_service import get_explanations

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


@router.get("/recommendations/explanations", response_model=ExplanationsResponse)
async def get_recommendations_explanations(
    user_id: int,
    course_ids: str,
    redis=Depends(get_redis),
):
    """
    Get explanations for specific recommended courses for a user.
    `course_ids` should be a comma-separated list of integers (e.g., "1,2,3").
    """
    try:
        parsed_ids = [int(cid.strip()) for cid in course_ids.split(",") if cid.strip()]
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="course_ids must be a comma-separated list of integers"
        )

    if not parsed_ids:
        raise HTTPException(
            status_code=400,
            detail="course_ids cannot be empty"
        )

    async for session in get_session():
        return await get_explanations(
            user_id=user_id,
            course_ids=parsed_ids,
            session=session,
            redis=redis,
        )
