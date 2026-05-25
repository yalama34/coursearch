from src.db.models import Action
from src.db.repositories.base_repository import BaseRepository
from src.domain.enum.action_type import ActionType


class ActionRepository(BaseRepository):
    """Repository to work with actions"""

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
