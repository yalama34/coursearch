from fastapi import APIRouter

from src.dependencies.auth import CurrentUserDep
from src.dependencies.redis import RedisDep

from src.schemas.engagement import UpdateEngagementRequest
from src.services.engagement import EngagementService


router = APIRouter(
    tags=["engagement"],
    prefix="/engagement",
)


@router.post(
    "",
    summary="Update user engagement",
)
async def update_engagement(
    request: UpdateEngagementRequest,
    current_user: CurrentUserDep,
    redis_client: RedisDep,
) -> dict[str, str]:
    """Update user engagement."""
    engagement_service = EngagementService(redis_client)

    await engagement_service.add_engagement(
        current_user.user_id,
        request,
    )

    return {"status": "ok"}
