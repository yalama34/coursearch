from sqlalchemy import select

from src.db.repositories.base_repository import BaseRepository
from src.domain.enum.action_type import ActionType
from src.schemas.course import CourseShort
from src.db.models import (
    User,
    Tag,
    Course,
    Action,
    user_tags
)


class UserRepository(BaseRepository):
    """
    Repository to make selects from user table
    """
    async def get_user(
            self,
            user_id: int
    ) -> User | None:
        """
        Get all user info by user ID
        """
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
        """
        Get all user tags by user ID
        """
        stmt = (
            select(Tag.name)
            .join(user_tags, Tag.tag_id == user_tags.c.tag_id)
            .where(user_tags.c.user_id == user_id)
        )
        result = await self.session.execute(stmt)

        return [row[0] for row in result.all()]


    async def get_user_liked_courses(
            self,
            user_id: int
    ) -> list[CourseShort]:
        """
        Get all user liked courses by user ID
        """
        stmt = (
            select(
                Course.course_id,
                Course.name
            )
            .join(Action, Course.course_id == Action.course_id)
            .where(
                Action.user_id == user_id,
                Action.action_type == ActionType.LIKE.value,
            )
        )

        result = await self.session.execute(stmt)

        return [
            CourseShort(
                course_id=row.course_id,
                name=row.name
            )
            for row in result.all()
        ]
