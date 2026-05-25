from sqlalchemy import select
from sqlalchemy.orm import selectinload

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
    """Repository to make selects from user table"""
    async def get_user(self, user_id: int) -> User | None:
        """Get all user info by user ID"""
        stmt = (
            select(User)
            .where(User.user_id == user_id)
            .options(selectinload(User.tags))
        )
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_nickname(self, nickname: str) -> User | None:
        """Get all user info by nickname"""
        stmt = (
            select(User)
            .where(User.nickname == nickname)
        )
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_by_jwt_token(self, token: str) -> User | None:
        """Get all user info by jwt token"""
        stmt = (
            select(User)
            .where(User.jwt_token == token)
        )
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def create_user(
        self,
        nickname: str,
        password_hash: str,
        jwt_token: str,
    ) -> User:
        """Create new user by password hash and jwt token"""
        user = User(
            nickname=nickname,
            password=password_hash,
            jwt_token=jwt_token,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def set_jwt_token(
            self,
            user_id: int,
            jwt_token: str | None,
    ) -> None:
        """Set new jwt token"""
        user = await self.get_user(user_id)
        if user:
            user.jwt_token = jwt_token
            await self.session.flush()

    async def get_user_tags(
            self,
            user_id: int
    ) -> list[str]:
        """Get all user tags by user ID"""
        stmt = (
            select(Tag.name)
            .join(user_tags, Tag.tag_id == user_tags.c.tag_id)
            .where(user_tags.c.user_id == user_id)
        )
        result = await self.session.execute(stmt)

        return [row[0] for row in result.all()]

    async def set_user_tags(self, user_id: int, tag_names: list[str]) -> None:
        """Set user tags by names"""
        user = await self.get_user(user_id)
        if not user:
            return

        if not tag_names:
            user.tags = []
        else:
            stmt = select(Tag).where(Tag.name.in_(tag_names))
            result = await self.session.execute(stmt)
            existing_tags = list(result.scalars().all())
            existing_names = {t.name for t in existing_tags}
            
            # Create missing tags
            for name in tag_names:
                if name not in existing_names:
                    new_tag = Tag(name=name)
                    self.session.add(new_tag)
                    existing_tags.append(new_tag)
                    
            user.tags = existing_tags

        await self.session.flush()


    async def get_user_liked_courses(
            self,
            user_id: int
    ) -> list[CourseShort]:
        """Get all user liked courses by user ID"""
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
