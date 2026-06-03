import pytest
from unittest.mock import AsyncMock, patch

from sqlalchemy.exc import IntegrityError

from src.services.auth import AuthService


@pytest.fixture
def auth_service(session_mock, repository_mock):
    service = AuthService(session=session_mock)

    service.repository = repository_mock

    return service


@pytest.mark.asyncio
async def test_register_returns_none_when_nickname_exists(
    auth_service,
    repository_mock,
    session_mock,
):
    repository_mock.get_by_nickname.return_value = object()

    result = await auth_service.register(
        nickname="test",
        password="password",
    )

    assert result is None

    repository_mock.create_user.assert_not_awaited()

    session_mock.commit.assert_not_awaited()


@pytest.mark.asyncio
@patch("src.services.auth.new_session_token")
@patch("src.services.auth.pwd_context.hash")
async def test_register_creates_user(
    hash_mock,
    token_mock,
    auth_service,
    repository_mock,
    session_mock,
):
    token_mock.return_value = "token"
    hash_mock.return_value = "hashed_password"

    user = object()

    repository_mock.get_by_nickname.return_value = None
    repository_mock.create_user.return_value = user

    result = await auth_service.register(
        nickname="test",
        password="password",
    )

    assert result == user

    repository_mock.create_user.assert_awaited_once_with(
        "test",
        "hashed_password",
        "token",
    )

    session_mock.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_rollbacks_on_integrity_error(
    auth_service,
    repository_mock,
    session_mock,
):
    repository_mock.get_by_nickname.return_value = None

    repository_mock.create_user.side_effect = IntegrityError(
        statement=None,
        params=None,
        orig=None,
    )

    result = await auth_service.register(
        nickname="test",
        password="password",
    )

    assert result is None

    session_mock.rollback.assert_awaited_once()

    session_mock.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_login_returns_none_when_user_not_found(
    auth_service,
    repository_mock,
):
    repository_mock.get_by_nickname.return_value = None

    result = await auth_service.login(
        nickname="test",
        password="password",
    )

    assert result is None

    repository_mock.set_jwt_token.assert_not_awaited()


@pytest.mark.asyncio
@patch("src.services.auth.pwd_context.verify")
async def test_login_returns_none_when_password_invalid(
    verify_mock,
    auth_service,
    repository_mock,
):
    user = AsyncMock()

    repository_mock.get_by_nickname.return_value = user

    verify_mock.return_value = False

    result = await auth_service.login(
        nickname="test",
        password="wrong_password",
    )

    assert result is None

    repository_mock.set_jwt_token.assert_not_awaited()


@pytest.mark.asyncio
@patch("src.services.auth.new_session_token")
@patch("src.services.auth.pwd_context.verify")
async def test_login_success(
    verify_mock,
    token_mock,
    auth_service,
    repository_mock,
    session_mock,
):
    user = AsyncMock()
    user.user_id = 1
    user.password = "hashed"

    repository_mock.get_by_nickname.return_value = user

    verify_mock.return_value = True
    token_mock.return_value = "new_token"

    result = await auth_service.login(
        nickname="test",
        password="password",
    )

    assert result == user

    repository_mock.set_jwt_token.assert_awaited_once_with(
        1,
        "new_token",
    )

    session_mock.commit.assert_awaited_once()

    session_mock.refresh.assert_awaited_once_with(user)


@pytest.mark.asyncio
async def test_logout(
    auth_service,
    repository_mock,
    session_mock,
):
    await auth_service.logout(user_id=1)

    repository_mock.set_jwt_token.assert_awaited_once_with(
        1,
        None,
    )

    session_mock.commit.assert_awaited_once()
