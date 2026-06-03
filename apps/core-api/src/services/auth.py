import secrets

from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

from src.dependencies.db import SessionDep
from src.db.models import User
from src.db.repositories.user_repository import UserRepository


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def new_session_token() -> str:
    return secrets.token_urlsafe(32)


class AuthService:
    def __init__(self, session: SessionDep):
        self.session = session
        self.repository = UserRepository(session)


    async def register(
            self,
            nickname: str,
            password: str
    ) -> User | None:
        """Register a new user by nickname and password."""
        if await self.repository.get_by_nickname(nickname):
            return None

        token = new_session_token()
        password_hash = pwd_context.hash(password)

        try:
            user = await self.repository.create_user(nickname, password_hash, token)
            await self.session.commit()
            return user

        except IntegrityError:
            await self.session.rollback()
            return None


    async def login(
            self,
            nickname: str,
            password: str
    ) -> User | None:
        """Login a user by nickname and password."""
        user = await self.repository.get_by_nickname(nickname)

        if not user or not pwd_context.verify(password, user.password):
            return None

        token = new_session_token()
        await self.repository.set_jwt_token(user.user_id, token)
        await self.session.commit()
        await self.session.refresh(user)

        return user


    async def logout(self, user_id: int) -> None:
        """Logout a user by user id."""
        await self.repository.set_jwt_token(user_id, None)
        await self.session.commit()
