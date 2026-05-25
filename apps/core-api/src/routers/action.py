from fastapi import APIRouter

from src.dependencies.auth import CurrentUserDep
from src.dependencies.db import SessionDep

from src.schemas.action import CreateActionRequest
from src.services.action import ActionService


router = APIRouter(
    tags=["actions"],
    prefix="/actions",
)


@router.post(
    "",
    summary="Create user action",
)
async def create_action(
    request: CreateActionRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> dict[str, str]:
    """Create user action."""
    action_service = ActionService(session)

    await action_service.create_action(
        current_user.user_id,
        request,
    )

    return {"status": "ok"}
