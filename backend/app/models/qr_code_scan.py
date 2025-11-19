"""QRCodeScan model for tracking QR code scans."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.lead import Lead
    from app.models.qr_code import QRCode


class QRCodeScan(Base):
    """QR Code Scan tracking model.

    Records each scan of a QR code with device information, location,
    and user behavior through the assessment funnel.
    """

    __tablename__ = "qr_code_scans"

    # Primary Key
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Foreign Key
    qr_code_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("qr_codes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # User Agent Information
    user_agent: Mapped[str] = mapped_column(Text, nullable=False, comment="Full user agent string")
    device_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="Device type: mobile, tablet, desktop")
    os: Mapped[str | None] = mapped_column(String(100), comment="Operating system: iOS, Android, Windows, etc.")
    browser: Mapped[str | None] = mapped_column(String(100), comment="Browser: Safari, Chrome, Firefox, etc.")

    # Location Information (GeoIP)
    ip_address: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
        comment="IPv4/IPv6 address (should be hashed for privacy)",
    )
    country: Mapped[str | None] = mapped_column(String(2), comment="ISO 3166-1 alpha-2 country code")
    city: Mapped[str | None] = mapped_column(String(255), comment="City name")
    latitude: Mapped[float | None] = mapped_column(Float, comment="Approximate latitude")
    longitude: Mapped[float | None] = mapped_column(Float, comment="Approximate longitude")

    # Behavior Tracking (Funnel)
    scanned_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="Timestamp when QR code was scanned",
    )
    assessment_started: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether user started the assessment",
    )
    assessment_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether user completed the assessment",
    )
    lead_created: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="Whether a lead was created")
    lead_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("leads.id", ondelete="SET NULL"),
        comment="Associated lead if created",
    )

    # Session Tracking
    session_id: Mapped[str | None] = mapped_column(String(255), comment="Session ID from cookie/localStorage")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    qr_code: Mapped["QRCode"] = relationship("QRCode", back_populates="scans")
    lead: Mapped["Lead | None"] = relationship("Lead", back_populates="qr_code_scans")

    # Table indexes
    __table_args__ = (
        Index("idx_qr_code_scans_qr_code_id", "qr_code_id"),
        Index("idx_qr_code_scans_scanned_at", "scanned_at"),
        Index("idx_qr_code_scans_lead_id", "lead_id"),
        Index("idx_qr_code_scans_session_id", "session_id"),
        # Composite index for analytics queries
        Index("idx_qr_code_scans_analytics", "qr_code_id", "scanned_at"),
    )

    def __repr__(self) -> str:
        return f"<QRCodeScan(id={self.id}, qr_code_id={self.qr_code_id}, device={self.device_type})>"
