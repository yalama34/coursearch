from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from sqlalchemy import text

from src.db.database import engine
from src.providers.sync import run_course_sync


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

@app.post("/sync")
async def trigger_sync(
    background_tasks: BackgroundTasks,
    pages: int = Query(default=50, ge=1, description="Number of pages to sync from provider")
):
    """Trigger course synchronization manually"""
    background_tasks.add_task(run_course_sync, pages)
    return {"status": "sync_started", "pages_limit": pages}

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
