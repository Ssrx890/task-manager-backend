from typing import Optional
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    full_name: str
    role: str = "SELLER"


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(SQLModel):
    email: Optional[str] = None
    role: Optional[str] = None