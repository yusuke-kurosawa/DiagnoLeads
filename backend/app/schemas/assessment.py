"""
Assessment Schemas

Pydantic models for Assessment API request/response validation.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AssessmentBase(BaseModel):
    """Base assessment schema with common fields"""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: str = Field(default="draft")
    topic_name: Optional[str] = Field(None, max_length=255, alias="topic")
    industry_name: Optional[str] = Field(None, max_length=100, alias="industry")
    ai_generated: str = Field(default="manual")
    scoring_logic: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class AssessmentCreate(AssessmentBase):
    """Schema for creating a new assessment"""

    pass


class AssessmentUpdate(BaseModel):
    """Schema for updating an existing assessment"""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    topic_name: Optional[str] = Field(None, max_length=255, alias="topic")
    industry_name: Optional[str] = Field(None, max_length=100, alias="industry")
    ai_generated: Optional[str] = None
    scoring_logic: Optional[Dict[str, Any]] = None

    model_config = {"populate_by_name": True}


class AssessmentResponse(AssessmentBase):
    """Schema for assessment response"""

    id: UUID
    tenant_id: UUID
    created_by: UUID
    updated_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
