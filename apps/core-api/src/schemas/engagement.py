from pydantic import BaseModel, Field


class UpdateEngagementRequest(BaseModel):
    course_id: int

    value: int = Field(
        gt=0,
        description="Engagement delta in seconds",
    )
