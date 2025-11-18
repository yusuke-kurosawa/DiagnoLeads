"""Google Analytics Integration Schemas

Pydantic schemas for GA4 integration API requests and responses.
"""
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
import re


class GoogleAnalyticsIntegrationBase(BaseModel):
    """Base schema for Google Analytics integration"""
    measurement_id: str = Field(..., description="GA4 Measurement ID (G-XXXXXXXXXX)")
    enabled: bool = Field(default=True, description="Enable/disable GA4 tracking")
    track_frontend: bool = Field(default=True, description="Track React admin dashboard events")
    track_embed_widget: bool = Field(default=True, description="Track embedded widget events")
    track_server_events: bool = Field(default=False, description="Track server-side events via Measurement Protocol")
    custom_dimensions: Optional[Dict[str, Any]] = Field(default=None, description="Custom GA4 dimensions configuration")

    @field_validator('measurement_id')
    @classmethod
    def validate_measurement_id(cls, v: str) -> str:
        """Validate GA4 Measurement ID format"""
        pattern = r'^G-[A-Z0-9]{10}$'
        if not re.match(pattern, v):
            raise ValueError(
                'Invalid Measurement ID format. Expected format: G-XXXXXXXXXX '
                '(e.g., G-ABC1234567)'
            )
        return v


class GoogleAnalyticsIntegrationCreate(GoogleAnalyticsIntegrationBase):
    """Schema for creating GA4 integration"""
    measurement_protocol_api_secret: Optional[str] = Field(
        default=None,
        description="GA4 Measurement Protocol API Secret (for server-side tracking)"
    )


class GoogleAnalyticsIntegrationUpdate(BaseModel):
    """Schema for updating GA4 integration"""
    measurement_id: Optional[str] = None
    measurement_protocol_api_secret: Optional[str] = None
    enabled: Optional[bool] = None
    track_frontend: Optional[bool] = None
    track_embed_widget: Optional[bool] = None
    track_server_events: Optional[bool] = None
    custom_dimensions: Optional[Dict[str, Any]] = None

    @field_validator('measurement_id')
    @classmethod
    def validate_measurement_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate GA4 Measurement ID format if provided"""
        if v is None:
            return v
        pattern = r'^G-[A-Z0-9]{10}$'
        if not re.match(pattern, v):
            raise ValueError(
                'Invalid Measurement ID format. Expected format: G-XXXXXXXXXX '
                '(e.g., G-ABC1234567)'
            )
        return v


class GoogleAnalyticsIntegrationResponse(GoogleAnalyticsIntegrationBase):
    """Schema for GA4 integration response"""
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class GoogleAnalyticsIntegrationPublic(BaseModel):
    """Public schema for GA4 integration (used by embed widget)

    Does NOT include API secret for security
    """
    measurement_id: str
    enabled: bool
    track_embed_widget: bool

    class Config:
        from_attributes = True


class GoogleAnalyticsTestResponse(BaseModel):
    """Schema for GA4 connection test response"""
    status: str = Field(..., description="Test status: 'success' or 'failed'")
    message: str = Field(..., description="Human-readable message")
    event_name: Optional[str] = Field(default=None, description="Test event name sent")
    timestamp: Optional[datetime] = Field(default=None, description="Test event timestamp")
    error_details: Optional[str] = Field(default=None, description="Error details if test failed")
