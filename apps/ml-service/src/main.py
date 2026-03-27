import logging

from fastapi import FastAPI, BackgroundTasks
from sqlalchemy import text

from src.db.database import get_session, engine
from src.pipelines.load_csv_pipeline import load_csv_pipeline
from src.pipelines.course_embeddings_pipeline import CourseEmbeddingPipeline

logger = logging.getLogger(__name__)

app = FastAPI(title="ML Service")


# Healthcheck
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


# Load data pipeline
@app.post("/pipelines/load-data")
async def run_load_data(background_tasks: BackgroundTasks):
    logger.info("Received request: load-data")

    background_tasks.add_task(load_csv_pipeline)

    return {"status": "started"}


# Index courses (embeddings)
async def run_index_pipeline():
    """Index all courses in the database"""
    async for session in get_session():
        pipeline = CourseEmbeddingPipeline(session=session)
        await pipeline.index_all_courses()


@app.post("/pipelines/index-courses")
async def run_index(background_tasks: BackgroundTasks):
    logger.info("Received request: index-courses")

    background_tasks.add_task(run_index_pipeline)

    return {"status": "started"}
