"""
Authentication Schemas

Pydantic models for authentication requests and responses.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserLogin(BaseModel):
    """User login request"""

    email: EmailStr
    password: str = Field(..., min_length=8)


class UserCreate(BaseModel):
    """User registration request"""

    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=255)
    tenant_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Organization name for new tenant",
    )
    tenant_slug: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern="^[a-z0-9-]+$",
        description="URL-friendly tenant identifier",
    )


class UserResponse(BaseModel):
    """User response model"""

    id: UUID
    tenant_id: UUID
    email: str
    name: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response"""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token payload data"""

    user_id: Optional[UUID] = None
    tenant_id: Optional[UUID] = None
    email: Optional[str] = None
