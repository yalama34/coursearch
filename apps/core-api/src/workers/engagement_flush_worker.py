import asyncio
import logging

from src.db.database import async_session_maker
from src.dependencies.redis import redis_client
from src.domain.constants.engagement import FLUSH_INTERVAL_SECONDS
from src.services.engagement_flush import EngagementFlushService

logger = logging.getLogger(__name__)


async def _flush_once() -> int:
    async with async_session_maker() as session:
        flush_service = EngagementFlushService(
            redis_client,
            session,
        )
        flushed = await flush_service.flush_all()
        await session.commit()
    return flushed


async def run_engagement_flush_loop() -> None:
    while True:
        try:
            flushed = await _flush_once()
            if flushed > 0:
                logger.info(
                    "Flushed %s engagement seconds to stats",
                    flushed,
                )
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Engagement flush failed")

        await asyncio.sleep(FLUSH_INTERVAL_SECONDS)


def start_engagement_flush_worker() -> asyncio.Task:
    return asyncio.create_task(
        run_engagement_flush_loop(),
        name="engagement-flush",
    )
