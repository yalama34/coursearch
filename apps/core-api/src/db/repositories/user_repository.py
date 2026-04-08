from sqlalchemy import select

from .base_repository import BaseRepository
from ...domain.enum.action_type import ActionType
from ..models import (
    User,
    Tag,
    Course,
    Action,
    user_tags
)


class UserRepository(BaseRepository):
    async def get_user(
            self,
            user_id: int
    ) -> User:

        stmt = (
            select(User)
            .where(User.user_id == user_id)
        )
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()


    async def get_user_tags(
            self,
            user_id: int
    ) -> list[str]:

        stmt = (
            select(Tag.name)
            .join(user_tags, Tag.tag_id == user_tags.c.tag_id)
            .where(user_tags.c.user_id == user_id)
        )
        result = await self.session.execute(stmt)

        return [row[0] for row in result.fetchall()]


    async def get_user_liked_courses(
            self,
            user_id: int
    ) -> list[dict]:

        stmt = (
            select(
                Course.course_id,
                Course.name
            )
            .join(Action, Course.course_id == Action.course_id)
            .where(
                Action.user_id == user_id,
                Action.type == ActionType.LIKE,
            )
        )

        result = await self.session.execute(stmt)

        return [
            {
                "course_id": row.course_id,
                "name": row.name
            }
            for row in result.fetchall()
        ]
