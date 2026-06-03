from pydantic import BaseModel, Field

from src.schemas.course import CourseShort


class ProfileResponse(BaseModel):
    user_id: int
    nickname: str
    description: str | None = None
    tags: list[str]
    liked_courses: list[CourseShort]

class UpdateTagsRequest(BaseModel):
    tags: list[str]

class UpdateDescriptionRequest(BaseModel):
    description: str = Field(
        max_length=1000,
    )
