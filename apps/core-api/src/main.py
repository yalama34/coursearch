from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from src.db.database import engine
from src.dependencies.ml_client import ml_client

from src.routers.profile import router as profile_router
from src.routers.health import router as health_router
from src.routers.recommendation import router as recommendation_router
from src.routers.auth import router as auth_router
from src.routers.course import router as course_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage startup and shutdown events for the FastAPI application.
    """
    # startup
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

    except Exception as e:
        raise RuntimeError(f"Database connection failed: {e}")

    yield

    # shotdown
    await engine.dispose()
    await ml_client.close()


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
