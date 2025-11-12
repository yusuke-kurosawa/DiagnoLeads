"""
User Schemas

Pydantic models for user-related API requests and responses.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    tenant_id: UUID
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=255)
    role: Optional[str] = Field(default="user")


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response"""
    id: UUID
    tenant_id: UUID
    email: str
    name: str
    role: str
    tenant_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserAdmin(BaseModel):
    """Schema for admin user view"""
    id: UUID
    tenant_id: UUID
    email: str
    name: str
    role: str
    tenant_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None

    class Config:
        from_attributes = True
