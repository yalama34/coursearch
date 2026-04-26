from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from src.db.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

    except Exception as e:
        raise RuntimeError(f"Database connection failed: {e}")

    yield

    await engine.dispose()


app = FastAPI(
    title="RecSys API",
    lifespan=lifespan
)
