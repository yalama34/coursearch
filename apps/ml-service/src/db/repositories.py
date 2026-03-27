from typing import List, Optional, Any, Tuple

import pandas as pd
from sqlalchemy import select, insert, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Course, Tag, Action, User, course_tags


async def save_df(
    session: AsyncSession,
    df: pd.DataFrame,
    target: Any,
    batch_size: int = 1000
) -> None:
    """
    Save DataFrame to DB in batches.
    
    target:    ORM model OR Table
    """

    if df is None or df.empty:
        return

    records = df.to_dict(orient="records")

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]

        if not batch:
            continue

        stmt = insert(target).values(batch)
        stmt = stmt.on_conflict_do_nothing()

        await session.execute(stmt)


async def get_user_by_id(
    session: AsyncSession,
    user_id: int
) -> Optional[User]:
    """Fetch a user by ID."""

    stmt = select(User).where(User.user_id == user_id)

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_course_by_id(
    session: AsyncSession,
    course_id: int
) -> Optional[Course]:
    """Fetch a course by its ID."""

    stmt = select(Course).where(Course.course_id == course_id)

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_courses(
    session: AsyncSession,
    limit: int = 100,
    offset: int = 0
) -> List[Course]:
    """Fetch a list of courses with pagination."""

    stmt = (
        select(Course)
        .order_by(Course.course_id)
        .limit(limit)
        .offset(offset)
    )

    result = await session.execute(stmt)
    return result.scalars().all()


async def get_all_tags(session: AsyncSession) -> List[Tag]:
    """Fetch all tags from the database."""

    stmt = select(Tag)

    result = await session.execute(stmt)
    return result.scalars().all()


async def get_tags_by_course(
    session: AsyncSession,
    course_id: int
) -> List[str]:
    """Fetch all tag names associated with a specific course."""

    stmt = (
        select(Tag.name)
        .join(course_tags, Tag.tag_id == course_tags.c.tag_id)
        .where(course_tags.c.course_id == course_id)
    )

    result = await session.execute(stmt)
    return [row[0] for row in result.fetchall()]


async def get_courses_with_tags_raw(
    session: AsyncSession, 
    limit: int = 100, 
    offset: int = 0
) -> List[Tuple]:
    """Fetch courses with tags from the database."""

    stmt = (
        select(
            Course.course_id,
            Course.name,
            Course.description,
            Course.difficulty,
            func.array_agg(Tag.name).label("tags")
        )
        .outerjoin(course_tags, Course.course_id == course_tags.c.course_id)
        .outerjoin(Tag, Tag.tag_id == course_tags.c.tag_id)
        .group_by(Course.course_id)
        .order_by(Course.course_id)
        .limit(limit)
        .offset(offset)
    )

    result = await session.execute(stmt)
    return result.fetchall()


async def get_actions_by_user(
    session: AsyncSession,
    user_id: int
) -> List[Action]:
    """Fetch all actions performed by a specific user."""

    stmt = select(Action).where(Action.user_id == user_id)

    result = await session.execute(stmt)
    return result.scalars().all()


async def get_actions_by_course(
    session: AsyncSession,
    course_id: int
) -> List[Action]:
    """Fetch all actions associated with a specific course."""

    stmt = select(Action).where(Action.course_id == course_id)

    result = await session.execute(stmt)
    return result.scalars().all()
