from pydantic import BaseModel

from src.schemas.course import CourseShort


class ProfileResponse(BaseModel):
    user_id: int
    tags: list[str]
    liked_courses: list[CourseShort]
