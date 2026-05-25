from src.schemas.course import Course


LEVEL_MAPPING = {
    "Beginner Level": "beginner",
    "Intermediate Level": "intermediate",
    "Expert Level": "advanced",
    "All Levels": "all",
}


def map_udemy_course(raw_course: dict) -> Course:
    category = None

    if raw_course.get("primary_category"):
        category = raw_course["primary_category"].get("title")

    tags: list[str] = []

    if category:
        tags.append(category)

    objectives = raw_course.get("objectives_summary") or []

    for objective in objectives:
        if isinstance(objective, str):
            tags.append(objective[:64])

    difficulty = LEVEL_MAPPING.get(
        raw_course.get("instructional_level"),
        raw_course.get("instructional_level"),
    )

    return Course(
        course_id=raw_course["id"],
        name=raw_course.get("title")
        or "Unknown Course",
        description=(
            raw_course.get("headline")
            or raw_course.get("description")
        ),
        difficulty=difficulty,
        link=(
            f'https://www.udemy.com{raw_course.get("url")}'
            if raw_course.get("url")
            else None
        ),
        source="udemy",
        tags=list(set(filter(None, tags))),
    )
