from pydemy.models import Course as UdemyCourse

from src.schemas.course import Course

def map_udemy_course(udemy_course: UdemyCourse) -> Course:
    tags: list[str] = []

    if udemy_course.locale and udemy_course.locale.title:
        tags.append(udemy_course.locale.title)
    if udemy_course.instructor_name:
        tags.append(udemy_course.instructor_name)

    return Course(
        course_id=udemy_course.id,
        name=udemy_course.title or "Unknown Course",
        description=udemy_course.headline,
        difficulty=None,
        link=f"https://www.udemy.com{udemy_course.url}" if udemy_course.url else None,
        source="udemy",
        tags=list(set(filter(None, tags))),
    )
