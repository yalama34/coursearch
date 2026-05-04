import os
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_USER"] = "test"
os.environ["DB_PASSWORD"] = "test"
os.environ["DB_NAME"] = "test"
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6379"

@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    return session

@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    return redis

@pytest.fixture
def mock_chroma():
    chroma = AsyncMock()
    return chroma

@pytest.fixture(scope="session")
def event_loop_policy():
    import asyncio
    return asyncio.DefaultEventLoopPolicy()
