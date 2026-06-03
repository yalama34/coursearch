from src.dependencies.db import SessionDep
from src.db.repositories.user_repository import UserRepository
from src.schemas.profile import ProfileResponse


class ProfileService:
    def __init__(
            self,
            session: SessionDep
    ):
        self.session = session
        self.repository = UserRepository(session)

    async def get_profile_by_id(
            self,
            user_id: int,
    ) -> ProfileResponse | None:
        """
        Get profile info by user ID
        Returns None if profile info not found
        """
        user = await self.repository.get_user(user_id)

        if not user:
            return None

        tags = await self.repository.get_user_tags(user_id)
        courses = await self.repository.get_user_liked_courses(user_id)

        return ProfileResponse(
            user_id=user.user_id,
            nickname=user.nickname,
            description=user.description,
            tags=tags,
            liked_courses=courses,
        )

    async def update_tags(
            self,
            user_id: int,
            tags: list[str]
    ) -> None:
        """
        Update user tags
        """
        await self.repository.set_user_tags(user_id, tags)
        await self.session.commit()

    async def update_description(
            self,
            user_id: int,
            description: str,
    ) -> None:
        """
        Update user description
        """

        description = description.strip()

        await self.repository.set_user_description(
            user_id,
            description if description else None,
        )

        await self.session.commit()
