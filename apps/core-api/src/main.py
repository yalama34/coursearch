from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from .db.database import engine


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


@app.get("/health")
async def health():

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "service": "core-api"
        }

    except Exception:

        return {
            "status": "error"
        }
