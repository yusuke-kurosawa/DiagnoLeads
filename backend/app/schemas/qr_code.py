"""Pydantic schemas for QR Code feature."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

# QR Code Schemas


class QRCodeStyleBase(BaseModel):
    """QR Code style configuration."""

    color: str = Field(
        default="#1E40AF",
        description="QR code color in hex format",
        pattern="^#[0-9A-Fa-f]{6}$",
    )
    logo_url: Optional[HttpUrl] = Field(None, description="URL of logo to embed in QR code center")
    frame: str = Field(
        default="none",
        description="Frame style: none, rounded, square",
        pattern="^(none|rounded|square)$",
    )
    size: int = Field(default=512, description="QR code size in pixels", ge=256, le=2048)


class QRCodeCreate(BaseModel):
    """Schema for creating a new QR code."""

    name: str = Field(
        ...,
        description="Human-readable name",
        min_length=1,
        max_length=255,
        examples=["展示会2025", "名刺用QRコード"],
    )
    utm_source: Optional[str] = Field(
        None,
        description="UTM source parameter",
        max_length=100,
        examples=["booth", "business_card"],
    )
    utm_medium: Optional[str] = Field(
        None,
        description="UTM medium parameter",
        max_length=100,
        examples=["qr", "offline"],
    )
    utm_campaign: Optional[str] = Field(
        None,
        description="UTM campaign parameter",
        max_length=100,
        examples=["tech_expo_2025", "winter_campaign"],
    )
    utm_term: Optional[str] = Field(None, description="UTM term parameter", max_length=100)
    utm_content: Optional[str] = Field(None, description="UTM content parameter", max_length=100)
    style: QRCodeStyleBase = Field(
        default_factory=QRCodeStyleBase,
        description="QR code visual style configuration",
    )


class QRCodeUpdate(BaseModel):
    """Schema for updating an existing QR code."""

    name: Optional[str] = Field(None, description="Human-readable name", min_length=1, max_length=255)
    enabled: Optional[bool] = Field(None, description="Whether QR code is active")


class QRCodeResponse(BaseModel):
    """Schema for QR code response."""

    id: UUID
    tenant_id: UUID
    assessment_id: UUID
    name: str
    short_code: str
    short_url: str

    # UTM Parameters
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None

    # Style
    style: dict

    # Storage URLs
    qr_code_image_url: Optional[str] = None
    qr_code_svg_url: Optional[str] = None

    # Metrics
    scan_count: int
    unique_scan_count: int
    last_scanned_at: Optional[datetime] = None

    # Status
    enabled: bool

    # Timestamps
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QRCodeListResponse(BaseModel):
    """Schema for QR code list response with pagination."""

    qr_codes: list[QRCodeResponse]
    total: int
    page: int
    limit: int
    pages: int


# QR Code Scan Schemas


class QRCodeScanCreate(BaseModel):
    """Schema for creating a QR code scan record (internal use)."""

    qr_code_id: UUID
    user_agent: str
    device_type: str
    os: Optional[str] = None
    browser: Optional[str] = None
    ip_address: str
    country: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    session_id: Optional[str] = None


class QRCodeScanResponse(BaseModel):
    """Schema for QR code scan response."""

    id: UUID
    qr_code_id: UUID
    device_type: str
    os: Optional[str] = None
    browser: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    scanned_at: datetime
    assessment_started: bool
    assessment_completed: bool
    lead_created: bool

    model_config = ConfigDict(from_attributes=True)


# Analytics Schemas


class QRCodeAnalyticsSummary(BaseModel):
    """QR code analytics summary."""

    total_scans: int = Field(description="Total number of scans")
    unique_scans: int = Field(description="Number of unique scans")
    assessment_started: int = Field(description="Number who started assessment")
    assessment_completed: int = Field(description="Number who completed assessment")
    leads_created: int = Field(description="Number of leads created")
    conversion_rate: float = Field(description="Conversion rate (completed / scanned)")


class QRCodeScansByDate(BaseModel):
    """Scans grouped by date."""

    date: str = Field(description="Date in YYYY-MM-DD format")
    scans: int = Field(description="Number of scans on this date")


class QRCodeScansByDevice(BaseModel):
    """Scans grouped by device type."""

    mobile: int = 0
    tablet: int = 0
    desktop: int = 0


class QRCodeScansByCountry(BaseModel):
    """Scans grouped by country."""

    country_scans: dict[str, int] = Field(
        description="Country code to scan count mapping",
        examples=[{"JP": 120, "US": 15, "CN": 10}],
    )


class QRCodeFunnel(BaseModel):
    """Conversion funnel metrics."""

    scanned: int = Field(description="Total scans")
    started: int = Field(description="Started assessment")
    completed: int = Field(description="Completed assessment")
    converted: int = Field(description="Became a lead")


class QRCodeAnalyticsResponse(BaseModel):
    """Complete analytics response for a QR code."""

    summary: QRCodeAnalyticsSummary
    scans_by_date: list[QRCodeScansByDate]
    scans_by_device: QRCodeScansByDevice
    scans_by_country: QRCodeScansByCountry
    funnel: QRCodeFunnel
