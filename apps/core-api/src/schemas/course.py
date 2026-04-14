from pydantic import BaseModel


class CourseShort(BaseModel):
    course_id: int
    name: str
