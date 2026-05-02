from pydantic import BaseModel, Field


class Course(BaseModel):
    course_id: int
    name: str
    description: str | None
    difficulty: str | None
    link: str | None
    source: str
    tags: list[str] = Field(default_factory=list)
