from sqlalchemy import select

from src.db.models import Action
from src.db.repositories.base_repository import BaseRepository
from src.domain.enum.action_type import ActionType


class ActionRepository(BaseRepository):
    """Repository to work with actions"""

    async def has_like(self, user_id: int, course_id: int) -> bool:
        stmt = (
            select(Action.action_id)
            .where(
                Action.user_id == user_id,
                Action.course_id == course_id,
                Action.action_type == ActionType.LIKE,
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create_action(
        self,
        user_id: int,
        course_id: int,
        action_type: ActionType,
        value: int | None = None,
    ) -> Action:
        """Create new action"""

        action = Action(
            user_id=user_id,
            course_id=course_id,
            action_type=action_type,
            value=value,
        )

        self.session.add(action)

        await self.session.flush()
        await self.session.refresh(action)

        return action
