from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.course import Course
from src.db.models.tag import Tag
from src.db.models.association_tables import course_tags
from src.db.repositories.base_repository import BaseRepository
from src.schemas.course import Course as CourseSchema


class CourseRepository(BaseRepository):
    async def upsert_courses(self, courses: list[CourseSchema]) -> None:
        """
        Bulk save courses into the database.
        If a course with the same course_id already exists, it will be skipped (ignored).
        """
        if not courses:
            return

        course_dicts = []
        for course in courses:
            course_dicts.append({
                "course_id": course.course_id,
                "name": course.name,
                "description": course.description,
                "difficulty": course.difficulty,
                "link": course.link,
            })

        stmt = insert(Course).values(course_dicts)

        stmt = stmt.on_conflict_do_nothing(
            index_elements=["course_id"]
        )

        await self.session.execute(stmt)
        await self.session.commit()

    async def upsert_tags(self, tag_names: list[str]) -> dict[str, int]:
        """
        Saves unique tags to the database (ignoring duplicates)
        and returns a dictionary {tag_name: tag_id} for linking with courses.
        """
        if not tag_names:
            return {}

        tag_dicts = [{"name": name} for name in tag_names]
        stmt = insert(Tag).values(tag_dicts).on_conflict_do_nothing(index_elements=["name"])
        await self.session.execute(stmt)

        select_stmt = select(Tag.tag_id, Tag.name).where(Tag.name.in_(tag_names))
        result = await self.session.execute(select_stmt)
        
        return {name: tag_id for tag_id, name in result.all()}

    async def link_courses_with_tags(self, course_tags_data: list[dict[str, int]]) -> None:
        """
        Links courses and tags in the association table (course_tags).
        Expects a list of dicts: [{"course_id": 1, "tag_id": 2}, ...]
        """
        if not course_tags_data:
            return

        stmt = insert(course_tags).values(course_tags_data)
        stmt = stmt.on_conflict_do_nothing(index_elements=["course_id", "tag_id"])
        
        await self.session.execute(stmt)
        await self.session.commit()
