import pytest

from src.domain.enum.action_type import ActionType
from src.schemas.action import CreateActionRequest
from src.services.action import ActionService


@pytest.fixture
def action_service(session_mock, repository_mock):
    service = ActionService(session=session_mock)

    service.repository = repository_mock

    return service


@pytest.mark.asyncio
async def test_create_action_returns_already_liked(
    action_service,
    repository_mock,
    session_mock,
):
    repository_mock.has_like.return_value = True

    request = CreateActionRequest(
        course_id=1,
        action_type=ActionType.LIKE,
        value=1,
    )

    result = await action_service.create_action(
        user_id=123,
        request=request,
    )

    assert result == "already_liked"

    repository_mock.has_like.assert_awaited_once_with(
        123,
        1,
    )

    repository_mock.create_action.assert_not_awaited()

    session_mock.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_action_creates_like(
    action_service,
    repository_mock,
    session_mock,
):
    repository_mock.has_like.return_value = False

    request = CreateActionRequest(
        course_id=1,
        action_type=ActionType.LIKE,
        value=1,
    )

    result = await action_service.create_action(
        user_id=123,
        request=request,
    )

    assert result == "liked"

    repository_mock.has_like.assert_awaited_once_with(
        123,
        1,
    )

    repository_mock.create_action.assert_awaited_once_with(
        user_id=123,
        course_id=1,
        action_type=ActionType.LIKE,
        value=1,
    )

    session_mock.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_action_creates_non_like_action(
    action_service,
    repository_mock,
    session_mock,
):
    request = CreateActionRequest(
        course_id=1,
        action_type=ActionType.VIEW,
        value=1,
    )

    result = await action_service.create_action(
        user_id=123,
        request=request,
    )

    assert result == "ok"

    repository_mock.has_like.assert_not_awaited()

    repository_mock.create_action.assert_awaited_once_with(
        user_id=123,
        course_id=1,
        action_type=ActionType.VIEW,
        value=1,
    )

    session_mock.commit.assert_awaited_once()
