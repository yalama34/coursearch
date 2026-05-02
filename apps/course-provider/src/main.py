from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.db.database import engine
from src.providers.sync import run_course_sync

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

        scheduler.add_job(run_course_sync, "interval", hours=1)
        scheduler.start()

    except Exception as e:
        raise RuntimeError(f"Database connection failed: {e}")

    yield

    scheduler.shutdown(wait=False)

    await engine.dispose()

app = FastAPI(
    title="RecSys API",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )
