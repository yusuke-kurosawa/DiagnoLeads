"""
Lead Schemas

Pydantic models for Lead API request/response validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LeadBase(BaseModel):
    """Base lead schema with common fields"""

    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    company: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    status: str = Field(default="new")
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class LeadCreate(LeadBase):
    """Schema for creating a new lead"""

    assigned_to: Optional[UUID] = None


class LeadUpdate(BaseModel):
    """Schema for updating an existing lead"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    company: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    assigned_to: Optional[UUID] = None


class LeadStatusUpdate(BaseModel):
    """Schema for updating lead status"""

    status: str = Field(..., pattern="^(new|contacted|qualified|converted|disqualified)$")


class LeadScoreUpdate(BaseModel):
    """Schema for updating lead score"""

    score: int = Field(..., ge=0, le=100)
    reason: Optional[str] = Field(None, max_length=255)


class LeadResponse(LeadBase):
    """Schema for lead response"""

    id: UUID
    tenant_id: UUID
    score: int
    last_contacted_at: Optional[datetime]
    last_activity_at: Optional[datetime]
    created_by: UUID
    updated_by: Optional[UUID]
    assigned_to: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
