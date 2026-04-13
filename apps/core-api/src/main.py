from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from src.db.database import engine
from src.dependencies.ml_client import ml_client

from src.routers.profile import router as profile_router
from src.routers.health import router as health_router
from src.routers.recommendation import router as recommendation_router


@asynccontextmanager
async def lifespan(app: FastAPI):

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

app.include_router(profile_router)
app.include_router(health_router)
app.include_router(recommendation_router)
