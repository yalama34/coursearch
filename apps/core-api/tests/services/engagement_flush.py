import pytest
from unittest.mock import AsyncMock

from src.services.engagement_flush import EngagementFlushService


@pytest.fixture
def engagement_repository_mock():
    return AsyncMock()


@pytest.fixture
def stats_repository_mock():
    return AsyncMock()


@pytest.fixture
def engagement_flush_service(
    engagement_repository_mock,
    stats_repository_mock,
):
    service = EngagementFlushService(
        redis_client=AsyncMock(),
        session=AsyncMock(),
    )

    service.engagement_repository = engagement_repository_mock
    service.stats_repository = stats_repository_mock

    return service


@pytest.mark.asyncio
async def test_flush_all_returns_zero_when_no_keys(
    engagement_flush_service,
    engagement_repository_mock,
    stats_repository_mock,
):
    async def empty_generator():
        if False:
            yield

    engagement_repository_mock.iter_engagement_keys.return_value = empty_generator()

    result = await engagement_flush_service.flush_all()

    assert result == 0

    stats_repository_mock.increment_watch_seconds.assert_not_awaited()


@pytest.mark.asyncio
async def test_flush_all_skips_empty_pending(
    engagement_flush_service,
    engagement_repository_mock,
    stats_repository_mock,
):
    async def generator():
        yield 1, 10, "key"

    engagement_repository_mock.iter_engagement_keys.return_value = generator()

    engagement_repository_mock.drain_pending.return_value = 0

    result = await engagement_flush_service.flush_all()

    assert result == 0

    stats_repository_mock.increment_watch_seconds.assert_not_awaited()


@pytest.mark.asyncio
async def test_flush_all_flushes_pending_engagement(
    engagement_flush_service,
    engagement_repository_mock,
    stats_repository_mock,
):
    async def generator():
        yield 1, 10, "key"

    engagement_repository_mock.iter_engagement_keys.return_value = generator()

    engagement_repository_mock.drain_pending.return_value = 25

    result = await engagement_flush_service.flush_all()

    assert result == 25

    engagement_repository_mock.drain_pending.assert_awaited_once_with(
        "key",
    )

    stats_repository_mock.increment_watch_seconds.assert_awaited_once_with(
        user_id=1,
        course_id=10,
        delta=25,
    )


@pytest.mark.asyncio
async def test_flush_all_flushes_multiple_keys(
    engagement_flush_service,
    engagement_repository_mock,
    stats_repository_mock,
):
    async def generator():
        yield 1, 10, "key1"
        yield 2, 20, "key2"

    engagement_repository_mock.iter_engagement_keys.return_value = generator()

    engagement_repository_mock.drain_pending.side_effect = [15, 30]

    result = await engagement_flush_service.flush_all()

    assert result == 45

    assert stats_repository_mock.increment_watch_seconds.await_count == 2
