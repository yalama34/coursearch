import pytest
from unittest.mock import AsyncMock

from src.services.action import ActionService


@pytest.fixture
def session_mock():
    session = AsyncMock()
    return session


@pytest.fixture
def repository_mock():
    repo = AsyncMock()
    return repo
