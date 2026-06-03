import pytest
from unittest.mock import AsyncMock

from src.schemas.profile import ProfileResponse
from src.services.profile import ProfileService


@pytest.fixture
def profile_service(session_mock, repository_mock):
    service = ProfileService(session=session_mock)

    service.repository = repository_mock

    return service


@pytest.mark.asyncio
async def test_get_profile_by_id_returns_none_when_user_not_found(
    profile_service,
    repository_mock,
):
    repository_mock.get_user.return_value = None

    result = await profile_service.get_profile_by_id(1)

    assert result is None

    repository_mock.get_user_tags.assert_not_awaited()

    repository_mock.get_user_liked_courses.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_profile_by_id_returns_profile(
    profile_service,
    repository_mock,
):
    user = AsyncMock()

    user.user_id = 1
    user.nickname = "test"
    user.description = "description"

    repository_mock.get_user.return_value = user

    repository_mock.get_user_tags.return_value = ["python", "backend"]

    repository_mock.get_user_liked_courses.return_value = [1, 2, 3]

    result = await profile_service.get_profile_by_id(1)

    assert result == ProfileResponse(
        user_id=1,
        nickname="test",
        description="description",
        tags=["python", "backend"],
        liked_courses=[1, 2, 3],
    )

    repository_mock.get_user_tags.assert_awaited_once_with(1)

    repository_mock.get_user_liked_courses.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_update_tags(
    profile_service,
    repository_mock,
    session_mock,
):
    tags = ["python", "backend"]

    await profile_service.update_tags(
        user_id=1,
        tags=tags,
    )

    repository_mock.set_user_tags.assert_awaited_once_with(
        1,
        tags,
    )

    session_mock.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_description(
    profile_service,
    repository_mock,
    session_mock,
):
    await profile_service.update_description(
        user_id=1,
        description="  hello world  ",
    )

    repository_mock.set_user_description.assert_awaited_once_with(
        1,
        "hello world",
    )

    session_mock.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_description_sets_none_when_empty(
    profile_service,
    repository_mock,
    session_mock,
):
    await profile_service.update_description(
        user_id=1,
        description="   ",
    )

    repository_mock.set_user_description.assert_awaited_once_with(
        1,
        None,
    )

    session_mock.commit.assert_awaited_once()
