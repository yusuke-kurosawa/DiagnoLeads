"""
Taxonomy Schemas

Pydantic models for topics and industries.
"""

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class TopicBase(BaseModel):
    """Base topic model"""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, max_length=7)  # Hex color
    icon: Optional[str] = Field(None, max_length=100)


class TopicCreate(TopicBase):
    """Topic creation request"""

    pass


class TopicUpdate(BaseModel):
    """Topic update request - partial update"""

    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None


class TopicResponse(TopicBase):
    """Topic response model"""

    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IndustryBase(BaseModel):
    """Base industry model"""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, max_length=7)  # Hex color
    icon: Optional[str] = Field(None, max_length=100)


class IndustryCreate(IndustryBase):
    """Industry creation request"""

    pass


class IndustryUpdate(BaseModel):
    """Industry update request - partial update"""

    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None


class IndustryResponse(IndustryBase):
    """Industry response model"""

    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
