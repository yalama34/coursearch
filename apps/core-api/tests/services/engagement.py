import pytest
from unittest.mock import AsyncMock

from src.schemas.engagement import UpdateEngagementRequest
from src.services.engagement import EngagementService


@pytest.fixture
def engagement_service(repository_mock):
    service = EngagementService(redis_client=AsyncMock())

    service.repository = repository_mock

    return service


@pytest.mark.asyncio
async def test_add_engagement(
    engagement_service,
    repository_mock,
):
    request = UpdateEngagementRequest(
        course_id=1,
        value=15,
    )

    await engagement_service.add_engagement(
        user_id=123,
        request=request,
    )

    repository_mock.add_engagement.assert_awaited_once_with(
        user_id=123,
        course_id=1,
        value=15,
    )
