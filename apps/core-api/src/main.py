from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from .db.database import engine
from .routers.profile import router as profile_router
from .routers.health import router as health_router


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


app = FastAPI(
    title="RecSys API",
    lifespan=lifespan
)

app.include_router(profile_router)
app.include_router(health_router)
