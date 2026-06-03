from src.dependencies.db import SessionDep

from src.db.repositories.action_repository import (
    ActionRepository,
)

from src.domain.enum.action_type import ActionType
from src.schemas.action import (
    CreateActionRequest,
)


class ActionService:
    def __init__(
        self,
        session: SessionDep
    ):
        self.session = session
        self.repository = (ActionRepository(session))

    async def create_action(
            self,
            user_id: int,
            request: CreateActionRequest,
    ) -> str:
        """Create user action. Returns status: ok | liked | already_liked."""
        if request.action_type == ActionType.LIKE:
            if await self.repository.has_like(user_id, request.course_id):
                return "already_liked"

            await self.repository.create_action(
                user_id=user_id,
                course_id=request.course_id,
                action_type=request.action_type,
                value=request.value,
            )
            await self.session.commit()
            return "liked"

        await self.repository.create_action(
            user_id=user_id,
            course_id=request.course_id,
            action_type=request.action_type,
            value=request.value,
        )

        await self.session.commit()
        return "ok"
