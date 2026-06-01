import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text

from src.db.database import async_session_maker, engine
from src.services.engagement_flush import EngagementFlushService

from src.dependencies.ml_client import ml_client
from src.dependencies.redis import redis_client

from src.routers.profile import router as profile_router
from src.routers.health import router as health_router
from src.routers.recommendation import router as recommendation_router
from src.routers.auth import router as auth_router
from src.routers.course import router as course_router
from src.routers.action import router as action_router
from src.routers.engagement import router as engagement_router
from src.workers.engagement_flush_worker import start_engagement_flush_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage startup and shutdown events for the FastAPI application.
    """

    # startup
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

        await redis_client.ping()

    except Exception as e:
        raise RuntimeError(
            f"Startup connection failed: {e}"
        )

    flush_task = start_engagement_flush_worker()

    yield

    # shutdown
    flush_task.cancel()
    try:
        await flush_task
    except asyncio.CancelledError:
        pass

    try:
        async with async_session_maker() as session:
            await EngagementFlushService(
                redis_client,
                session,
            ).flush_all()
            await session.commit()
    except Exception:
        pass

    await engine.dispose()

    await ml_client.close()
    await redis_client.aclose()


app = FastAPI(
    title="RecSys API",
    lifespan=lifespan
)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(health_router)
app.include_router(recommendation_router)
app.include_router(course_router)
app.include_router(action_router)
app.include_router(engagement_router)
