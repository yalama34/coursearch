from fastapi import APIRouter, HTTPException

from src.dependencies.db import SessionDep
from src.dependencies.auth import CurrentUserDep
from src.services.profile import ProfileService
from src.schemas.profile import (
    UpdateDescriptionRequest,
    ProfileResponse,
    UpdateTagsRequest,
)


router = APIRouter(tags=["profile"], prefix="/profile")


@router.post(
        "/tags",
        summary="Update user tags",
)
async def update_user_tags(
        request: UpdateTagsRequest,
        current_user: CurrentUserDep,
        session: SessionDep,
) -> dict[str, str]:
    """
    Update tags (interests) for the current user.
    """
    profile_service = ProfileService(session)
    await profile_service.update_tags(current_user.user_id, request.tags)
    return {"status": "ok"}


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

@router.post(
        "/description",
        summary="Update user description",
)
async def update_user_description(
        request: UpdateDescriptionRequest,
        current_user: CurrentUserDep,
        session: SessionDep,
) -> dict[str, str]:
    """
    Update description for the current user.
    """
    profile_service = ProfileService(session)

    await profile_service.update_description(
        current_user.user_id,
        request.description,
    )

    return {"status": "ok"}
