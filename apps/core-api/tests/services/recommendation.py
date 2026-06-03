import pytest
from unittest.mock import AsyncMock

from src.integrations.ml_service.schemas import (
    ExplanationsResponse,
    RecommendationResponse,
)
from src.services.recommendation import RecommendationService


@pytest.fixture
def ml_client_mock():
    return AsyncMock()


@pytest.fixture
def recommendation_service(ml_client_mock):
    return RecommendationService(
        ml_client=ml_client_mock,
    )


@pytest.mark.asyncio
async def test_get_recommendations_returns_placeholder_response(
    recommendation_service,
    ml_client_mock,
):
    result = await recommendation_service.get_recommendations(
        user_id=1,
        placeholder=True,
    )

    assert result == RecommendationResponse(
        user_id=1,
        items=[],
    )

    ml_client_mock.get_recommendations.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_recommendations_returns_ml_response(
    recommendation_service,
    ml_client_mock,
):
    response = RecommendationResponse(
        user_id=1,
        items=[],
    )

    ml_client_mock.get_recommendations.return_value = response

    result = await recommendation_service.get_recommendations(
        user_id=1,
        limit=5,
        force=True,
    )

    assert result == response

    ml_client_mock.get_recommendations.assert_awaited_once_with(
        1,
        5,
        force=True,
    )


@pytest.mark.asyncio
async def test_get_recommendations_uses_default_limit(
    recommendation_service,
    ml_client_mock,
):
    response = RecommendationResponse(
        user_id=1,
        items=[],
    )

    ml_client_mock.get_recommendations.return_value = response

    await recommendation_service.get_recommendations(
        user_id=1,
    )

    ml_client_mock.get_recommendations.assert_awaited_once_with(
        1,
        10,
        force=False,
    )


@pytest.mark.asyncio
async def test_get_explanations(
    recommendation_service,
    ml_client_mock,
):
    response = ExplanationsResponse(
        explanations=[],
    )

    ml_client_mock.get_explanations.return_value = response

    result = await recommendation_service.get_explanations(
        user_id=1,
        course_ids=[1, 2, 3],
        force=True,
    )

    assert result == response

    ml_client_mock.get_explanations.assert_awaited_once_with(
        1,
        [1, 2, 3],
        force=True,
    )
