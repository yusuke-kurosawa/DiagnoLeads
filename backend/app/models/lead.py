"""
Lead Model

Represents a lead (prospect) in the sales funnel.
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Lead(Base):
    """Lead model with tenant association and scoring"""

    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    response_id = Column(
        UUID(as_uuid=True), ForeignKey("responses.id", ondelete="SET NULL"), nullable=True
    )

    # Core Fields
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    job_title = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)

    # Status & Score
    status = Column(
        String(50), default="new", nullable=False
    )  # new, contacted, qualified, converted, disqualified
    score = Column(Integer, default=0, nullable=False)  # 0-100

    # Engagement Tracking
    last_contacted_at = Column(DateTime(timezone=True), nullable=True)
    last_activity_at = Column(DateTime(timezone=True), nullable=True)

    # Additional Info
    notes = Column(Text, nullable=True)
    tags = Column(JSON, default=list, nullable=False)
    custom_fields = Column(JSON, default=dict, nullable=False)

    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    response = relationship("Response", back_populates="leads")
    qr_code_scans = relationship("QRCodeScan", back_populates="lead")

    # Indexes for performance
    __table_args__ = (
        Index("idx_leads_tenant_status", "tenant_id", "status"),
        Index("idx_leads_tenant_score", "tenant_id", "score"),
        Index("idx_leads_assigned_to", "assigned_to"),
        UniqueConstraint("tenant_id", "email", name="uq_leads_tenant_email"),
    )

    def __repr__(self):
        return f"<Lead(id={self.id}, name={self.name}, email={self.email}, tenant_id={self.tenant_id}, status={self.status}, score={self.score})>"
