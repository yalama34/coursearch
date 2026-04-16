from fastapi import APIRouter, HTTPException

from src.dependencies.db import SessionDep
from src.services.profile import ProfileService
from src.schemas.profile import ProfileResponse


router = APIRouter(tags=["profile"], prefix="/profile")


@router.get(
        "/{user_id}",
        response_model=ProfileResponse,
        summary="Get user profile by ID",
)
async def get_user_profile(
        user_id: int,
        session: SessionDep,
) -> ProfileResponse:
    """
    Get user profile by ID.

    Raises:
        HTTPException: 404 if user not found
    """
    profile_service = ProfileService(session)

    user = await profile_service.get_profile_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
