from pydantic import BaseModel
from typing import List, Optional


class CourseShort(BaseModel):
    course_id: int
    name: str

class TagResponse(BaseModel):
    id: int
    label: str

class CourseDetail(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    difficulty: Optional[str] = None
    link: Optional[str] = None
    tags: List[TagResponse]
