from typing import Protocol, runtime_checkable


from src.schemas.course import Course

class CourseProvider(Protocol):
    async def get_courses(self) -> list[Course]:
        """Get, format and return courses from provider's API"""