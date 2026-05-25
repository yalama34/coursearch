from pydantic import BaseModel

from src.domain.enum.action_type import ActionType


class CreateActionRequest(BaseModel):
    course_id: int
    action_type: ActionType
    value: int | None = None
