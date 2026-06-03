from fastapi import APIRouter, HTTPException, status

from src.dependencies.auth import CurrentUserDep
from src.dependencies.db import SessionDep
from src.schemas.auth import AuthResponse, LoginRequest, MeResponse, RegisterRequest
from src.services.auth import AuthService


router = APIRouter(tags=["auth"], prefix="/auth")


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
)
async def register(body: RegisterRequest, session: SessionDep) -> AuthResponse:
    """
    Register new user by nickname and password.

    Raises:
        HTTPException: 409 if nickname already taken
    """
    auth = AuthService(session)
    user = await auth.register(body.nickname, body.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nickname already taken",
        )

    assert user.jwt_token is not None
    return AuthResponse(
        token=user.jwt_token,
        user_id=user.user_id,
        nickname=user.nickname,
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login (password + jwt)",
)
async def login(body: LoginRequest, session: SessionDep) -> AuthResponse:
    """
    Login user by nickname and password.

    Raises:
        HTTPException: 401 if wrong nickname or password
    """
    auth = AuthService(session)
    user = await auth.login(body.nickname, body.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong nickname or password",
        )

    assert user.jwt_token is not None
    return AuthResponse(
        token=user.jwt_token,
        user_id=user.user_id,
        nickname=user.nickname,
    )


@router.post(
    "/logout",
    summary="Logout (token reset)"
)
async def logout(
    current_user: CurrentUserDep,
    session: SessionDep,
) -> dict[str, str]:
    """Logout user on server"""
    await AuthService(session).logout(current_user.user_id)
    return {"status": "ok"}


@router.get(
    "/me",
    response_model=MeResponse,
    summary="Current user"
)
async def me(current_user: CurrentUserDep) -> MeResponse:
    """Get current user"""
    return MeResponse(
        user_id=current_user.user_id,
        nickname=current_user.nickname,
    )
