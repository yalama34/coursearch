from pydantic import BaseModel


class Course(BaseModel):
    course_id: int
    name: str
    description: str | None
    difficulty: str | None
    link: str | None
    source: str
