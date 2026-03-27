from typing import List
from db.models import Course


def course_to_dict(course: Course) -> dict:
    """Convert a Course object to a dictionary."""
    return {
        "course_id": course.course_id,
        "name": course.name,
        "description": course.description,
        "difficulty": course.difficulty,
    }


def courses_to_dict(courses: List[Course]) -> List[dict]:
    """Convert a list of Course objects to a list of dictionaries."""
    return [course_to_dict(c) for c in courses]


def course_with_tags_row_to_dict(row) -> dict:
    """Convert a raw query result row of a course with tags into a dictionary."""
    return {
        "course_id": row.course_id,
        "name": row.name,
        "description": row.description,
        "difficulty": row.difficulty,
        "tags": row.tags or []
    }


def courses_with_tags_to_dict(rows) -> list[dict]:
    """Convert raw query results of courses with tags into a list of dictionaries."""
    return [course_with_tags_row_to_dict(r) for r in rows]
