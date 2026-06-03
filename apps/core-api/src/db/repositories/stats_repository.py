from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from src.db.models.stats import Stats
from src.db.repositories.base_repository import BaseRepository


class StatsRepository(BaseRepository):
    async def increment_watch_seconds(
        self,
        user_id: int,
        course_id: int,
        delta: int,
    ) -> None:
        if delta <= 0:
            return

        now = datetime.now(timezone.utc)
        insert_stmt = insert(Stats).values(
            user_id=user_id,
            course_id=course_id,
            total_watch_seconds=delta,
            created_at=now,
            updated_at=now,
        )
        upsert_stmt = insert_stmt.on_conflict_do_update(
            constraint="uq_stats_user_course",
            set_={
                "total_watch_seconds": (
                    Stats.total_watch_seconds
                    + insert_stmt.excluded.total_watch_seconds
                ),
                "updated_at": now,
            },
        )
        await self.session.execute(upsert_stmt)

    async def get_stats(
        self,
        user_id: int,
        course_id: int,
    ) -> Stats | None:
        stmt = (
            select(Stats)
            .where(
                Stats.user_id == user_id,
                Stats.course_id == course_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
