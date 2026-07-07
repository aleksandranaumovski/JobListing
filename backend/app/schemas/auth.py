from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class RegisterRequest(BaseModel):
    email: str = Field(pattern=EMAIL_PATTERN, max_length=320)
    full_name: str = Field(min_length=2, max_length=200)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(pattern=EMAIL_PATTERN, max_length=320)
    password: str = Field(min_length=1, max_length=128)


class UserRead(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
