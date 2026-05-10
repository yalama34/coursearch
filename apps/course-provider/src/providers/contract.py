from typing import Protocol, runtime_checkable

from src.schemas.course import Course


@runtime_checkable
class CourseProvider(Protocol):
    def __init__(self, client):
        ...
    async def get_courses(self, pages_limit: int | None = None) -> list[Course]:
        """Get, format and return courses from provider's API"""
        ...