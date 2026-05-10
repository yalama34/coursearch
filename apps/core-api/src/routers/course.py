from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.dependencies.db import SessionDep
from src.db.models.course import Course
from src.schemas.course import CourseDetail, TagResponse

router = APIRouter(tags=["courses"], prefix="/courses")

@router.get("/{course_id}", response_model=CourseDetail)
async def get_course(course_id: int, session: SessionDep) -> CourseDetail:
    stmt = select(Course).where(Course.course_id == course_id).options(selectinload(Course.tags))
    result = await session.execute(stmt)
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    return CourseDetail(
        id=course.course_id,
        title=course.name,
        description=course.description,
        difficulty=course.difficulty,
        link=course.link,
        tags=[TagResponse(id=tag.tag_id, label=tag.name) for tag in course.tags]
    )
