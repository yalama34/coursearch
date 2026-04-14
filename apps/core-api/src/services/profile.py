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
        user = await self.repository.get_user(user_id)

        if not user:
            return None

        tags = await self.repository.get_user_tags(user_id)
        courses = await self.repository.get_user_liked_courses(user_id)

        return ProfileResponse(
            user_id=user.user_id,
            tags=tags,
            liked_courses=courses,
        )
