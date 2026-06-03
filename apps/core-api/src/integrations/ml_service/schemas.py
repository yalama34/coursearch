from pydantic import BaseModel


class RecommendationExplanation(BaseModel):
    text: str
    confidence: float | None = None


class RecommendationItem(BaseModel):
    item_id: int
    explanation: RecommendationExplanation | None = None


class RecommendationResponse(BaseModel):
    user_id: int
    items: list[RecommendationItem]


class ExplanationItem(BaseModel):
    course_id: int
    text: str


class ExplanationsResponse(BaseModel):
    user_id: int
    explanations: list[ExplanationItem]
