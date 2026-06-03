from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    nickname: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    nickname: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user_id: int
    nickname: str


class MeResponse(BaseModel):
    user_id: int
    nickname: str
