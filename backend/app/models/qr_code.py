"""QRCode model for QR code distribution feature."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.tenant import Tenant
    from app.models.assessment import Assessment
    from app.models.qr_code_scan import QRCodeScan


class QRCode(Base):
    """QR Code model for assessment distribution.

    Generates unique QR codes for each assessment that can be used in
    offline marketing materials (business cards, posters, booth displays).
    Tracks scan counts and provides analytics.
    """

    __tablename__ = "qr_codes"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    # Foreign Keys
    tenant_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assessment_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic Info
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Human-readable name (e.g., '展示会2025')"
    )
    short_code: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        index=True,
        nullable=False,
        comment="Unique 7-character code for short URL",
    )
    short_url: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Short URL (e.g., https://dgnl.ds/abc123)"
    )

    # UTM Parameters for tracking
    utm_source: Mapped[str | None] = mapped_column(String(100))
    utm_medium: Mapped[str | None] = mapped_column(String(100))
    utm_campaign: Mapped[str | None] = mapped_column(String(100))
    utm_term: Mapped[str | None] = mapped_column(String(100))
    utm_content: Mapped[str | None] = mapped_column(String(100))

    # Style configuration (JSONB)
    style: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Style settings: color, logo_url, frame, size",
    )
    # Example style:
    # {
    #   "color": "#1E40AF",
    #   "logo_url": "https://example.com/logo.png",
    #   "frame": "rounded",
    #   "size": 512
    # }

    # Storage URLs
    qr_code_image_url: Mapped[str | None] = mapped_column(
        String(500), comment="S3/R2 URL for PNG image"
    )
    qr_code_svg_url: Mapped[str | None] = mapped_column(
        String(500), comment="S3/R2 URL for SVG image"
    )

    # Tracking metrics
    scan_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="Total number of scans"
    )
    unique_scan_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of unique scans (by session)",
    )
    last_scanned_at: Mapped[datetime | None] = mapped_column(
        DateTime, comment="Timestamp of last scan"
    )

    # Status
    enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, comment="Whether QR code is active"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="qr_codes")
    assessment: Mapped["Assessment"] = relationship(
        "Assessment", back_populates="qr_codes"
    )
    scans: Mapped[list["QRCodeScan"]] = relationship(
        "QRCodeScan", back_populates="qr_code", cascade="all, delete-orphan"
    )

    # Table indexes
    __table_args__ = (
        Index("idx_qr_codes_short_code", "short_code", unique=True),
        Index("idx_qr_codes_tenant_id", "tenant_id"),
        Index("idx_qr_codes_assessment_id", "assessment_id"),
        Index("idx_qr_codes_enabled", "enabled"),
    )

    def __repr__(self) -> str:
        return f"<QRCode(id={self.id}, name='{self.name}', short_code='{self.short_code}')>"
