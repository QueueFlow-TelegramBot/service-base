from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    telegram_id: str = Field(..., description="Telegram user ID")
    display_name: str = Field(
        ..., min_length=1, max_length=100, description="User display name"
    )


class UserUpdate(BaseModel):
    display_name: str = Field(
        ..., min_length=1, max_length=100, description="Updated display name"
    )


class UserResponse(BaseModel):
    id: str
    telegram_id: str
    display_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    telegram_id: Optional[str] = None


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
