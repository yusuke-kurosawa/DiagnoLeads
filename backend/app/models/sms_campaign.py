"""
SMS Campaign Model

Tracks SMS campaigns for assessment distribution.
"""

from datetime import datetime
from uuid import uuid4
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class SMSStatus(str, enum.Enum):
    """SMS delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    UNDELIVERED = "undelivered"


class SMSCampaign(Base):
    """
    SMS Campaign model for assessment distribution.

    Allows tenants to send assessment links via SMS using Twilio.
    Tracks sending history and delivery status.
    """

    __tablename__ = "sms_campaigns"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Foreign Keys
    tenant_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    assessment_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    qr_code_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("qr_codes.id", ondelete="SET NULL"),
        nullable=True,
        comment="Optional: Use QR code's short URL"
    )
    created_by: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Campaign Info
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Campaign name (e.g., '展示会フォローアップ')"
    )
    message_template: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="SMS message template with {url} placeholder"
    )

    # Recipient Info (JSONB for flexibility)
    recipients: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="List of recipients with phone numbers"
    )
    # Example:
    # {
    #   "total": 100,
    #   "numbers": ["+819012345678", ...]
    # }

    # Sending Stats
    total_recipients: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    sent_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    delivered_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    failed_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    # Status
    status: Mapped[SMSStatus] = mapped_column(
        Enum(SMSStatus),
        nullable=False,
        default=SMSStatus.PENDING
    )

    # Metadata
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Scheduled send time (null = send immediately)"
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    messages: Mapped[list["SMSMessage"]] = relationship(
        "SMSMessage",
        back_populates="campaign",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SMSCampaign(id={self.id}, name='{self.name}', status='{self.status}')>"


class SMSMessage(Base):
    """
    Individual SMS message within a campaign.

    Tracks each SMS sent, including delivery status and Twilio SID.
    """

    __tablename__ = "sms_messages"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Foreign Keys
    campaign_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sms_campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    tenant_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Recipient
    phone_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="E.164 format: +819012345678"
    )

    # Message Content
    message_body: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    short_url: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Short URL included in message"
    )

    # Twilio Info
    twilio_sid: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        index=True,
        comment="Twilio message SID"
    )

    # Status
    status: Mapped[SMSStatus] = mapped_column(
        Enum(SMSStatus),
        nullable=False,
        default=SMSStatus.PENDING,
        index=True
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Tracking
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )
    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    # Engagement (tracked via QR code scans)
    clicked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether recipient clicked the link"
    )
    clicked_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    campaign: Mapped["SMSCampaign"] = relationship(
        "SMSCampaign",
        back_populates="messages"
    )

    def __repr__(self) -> str:
        return f"<SMSMessage(id={self.id}, phone='{self.phone_number}', status='{self.status}')>"
