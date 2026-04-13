from fastapi import APIRouter, HTTPException

from src.dependencies.db import SessionDep
from src.services.profile import ProfileService


router = APIRouter(tags=["profile"], prefix="/profile")


@router.get("/{user_id}")
async def get_user_profile(
        user_id: int,
        session: SessionDep,
):
    profile_service = ProfileService(session)

    user = await profile_service.get_profile_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
