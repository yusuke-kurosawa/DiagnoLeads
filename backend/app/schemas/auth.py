"""
Authentication Schemas

Pydantic models for authentication requests and responses.
"""

import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


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

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password meets security requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        """
        if len(v) < 8:
            raise ValueError("パスワードは8文字以上である必要があります")
        if not re.search(r"[A-Z]", v):
            raise ValueError("パスワードには英大文字を含む必要があります")
        if not re.search(r"[a-z]", v):
            raise ValueError("パスワードには英小文字を含む必要があります")
        if not re.search(r"\d", v):
            raise ValueError("パスワードには数字を含む必要があります")
        return v


class UserResponse(BaseModel):
    """User response model"""

    id: UUID
    tenant_id: UUID
    email: str
    name: str
    role: str
    tenant_name: Optional[str] = None
    tenant_slug: Optional[str] = None
    tenant_plan: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RegistrationResponse(BaseModel):
    """Registration response (spec-compliant)"""

    user_id: UUID
    tenant_id: UUID
    message: str = "登録が完了しました。ログインしてください。"


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


class PasswordResetRequest(BaseModel):
    """Password reset request"""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""

    token: str
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate new password meets security requirements"""
        if len(v) < 8:
            raise ValueError("パスワードは8文字以上である必要があります")
        if not re.search(r"[A-Z]", v):
            raise ValueError("パスワードには英大文字を含む必要があります")
        if not re.search(r"[a-z]", v):
            raise ValueError("パスワードには英小文字を含む必要があります")
        if not re.search(r"\d", v):
            raise ValueError("パスワードには数字を含む必要があります")
        return v


class TokenRefresh(BaseModel):
    """Token refresh request"""

    refresh_token: str


class TokenResponse(BaseModel):
    """Token response with both access and refresh tokens"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours in seconds
    user: UserResponse
