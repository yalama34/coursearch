from fastapi import APIRouter, HTTPException

from src.integrations.ml_service.schemas import ExplanationsResponse, RecommendationResponse
from src.dependencies.ml_client import get_ml_client, MLClientDep
from src.services.recommendation import RecommendationService

router = APIRouter(tags=["recommendations"], prefix="/recommendations")


@router.get(
        "", 
        response_model=RecommendationResponse,
        summary="Get recommendations by user ID",
)
async def get_recommendations(
        user_id: int,
        limit: int = 10,
        ml_client: MLClientDep = None,
):
    """
    Get recommendations by user ID.

    Args:
        user_id: int - User ID for whom to get recommendations
        limit: int - Number of recommendations to return (default: 10)

    Raises:
        HTTPException: 503 if ML service unavailable
    """
    service = RecommendationService(ml_client)

    try:
        return await service.get_recommendations(user_id, limit)

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="ML service unavailable",
        )


@router.get(
    "/explanations",
    response_model=ExplanationsResponse,
    summary="Get recommendation explanations by course IDs",
)
async def get_recommendations_explanations(
        user_id: int,
        course_ids: str,
        ml_client: MLClientDep = None,
):
    try:
        parsed_ids = [int(cid.strip()) for cid in course_ids.split(",") if cid.strip()]
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="course_ids must be a comma-separated list of integers",
        )

    if not parsed_ids:
        raise HTTPException(
            status_code=400,
            detail="course_ids cannot be empty",
        )

    service = RecommendationService(ml_client)

    try:
        return await service.get_explanations(user_id, parsed_ids)

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="ML service unavailable",
        )
