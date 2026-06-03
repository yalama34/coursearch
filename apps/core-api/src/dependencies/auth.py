from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from src.dependencies.db import SessionDep
from src.db.models import User
from src.db.repositories.user_repository import UserRepository


async def get_current_user(
    session: SessionDep,
    x_session_token: Annotated[str | None, Header(alias="X-Session-Token")] = None,
) -> User:
    if not x_session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Session-Token header",
        )

    repo = UserRepository(session)
    user = await repo.get_by_jwt_token(x_session_token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
