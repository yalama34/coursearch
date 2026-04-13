from fastapi import APIRouter, HTTPException

from src.integrations.ml_service.client import MLServiceClient
from src.integrations.ml_service.schemas import RecommendationResponse
from src.dependencies.ml_client import get_ml_client, MLClientDep
from src.services.recommendation import RecommendationService

router = APIRouter(tags=["recommendations"], prefix="/recommendations")


@router.get("", response_model=RecommendationResponse)
async def get_recommendations(
        user_id: int,
        limit: int = 10,
        ml_client: MLClientDep = None,
):
    service = RecommendationService(ml_client)

    try:
        return await service.get_recommendations(user_id, limit, True)

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="ML service unavailable",
        )
