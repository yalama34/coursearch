import logging
import sys
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from ..common.logging_config import configure_logging

from ..db.database import get_session, engine
from ..pipelines.course_embeddings_pipeline import CourseEmbeddingPipeline

logger = logging.getLogger(__name__)


async def main():
    try:
        session: AsyncSession = get_session()
        pipeline: CourseEmbeddingPipeline = CourseEmbeddingPipeline(session=session)

        logger.info("Starting course index")
        await pipeline.index_all_courses()
        logger.info("Course index finished")

    except Exception:
        logger.exception("Course index failed")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    configure_logging()
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
