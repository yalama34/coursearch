from src.quality.spam import is_spammy_course
from src.quality.text import strip_html
from src.schemas.course import Course


def normalize_course(course: Course) -> Course:
    return course.model_copy(
        update={
            "name": (strip_html(course.name) or "").strip(),
            "description": strip_html(course.description),
        }
    )


def is_valid_course(course: Course) -> bool:
    if not course.course_id:
        return False
    if not course.name or not course.name.strip():
        return False
    if is_spammy_course(course.name, course.description):
        return False
    return True


def validate_course(course: Course) -> Course | None:
    normalized = normalize_course(course)
    if not is_valid_course(normalized):
        return None
    return normalized


def filter_valid_courses(courses: list[Course]) -> list[Course]:
    result: list[Course] = []
    for course in courses:
        validated = validate_course(course)
        if validated is not None:
            result.append(validated)
    return result
