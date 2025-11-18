"""
Assessment Model

Represents a diagnostic assessment created by a tenant.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Assessment(Base):
    """Assessment model with tenant association"""

    __tablename__ = "assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        String(50), default="draft", nullable=False
    )  # draft, published, archived

    # AI generation metadata
    topic_name = Column(String(255), nullable=True)  # Used for AI generation display
    industry_name = Column(String(100), nullable=True)  # Used for AI generation display
    ai_generated = Column(String(50), default="manual", nullable=False)  # manual, ai, hybrid

    # Scoring configuration
    scoring_logic = Column(JSON, default=dict, nullable=False)  # Scoring rules

    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

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
    questions = relationship(
        "Question",
        back_populates="assessment",
        cascade="all, delete-orphan",
        order_by="Question.order",
    )
    responses = relationship(
        "Response", back_populates="assessment", cascade="all, delete-orphan"
    )
    qr_codes = relationship("QRCode", back_populates="assessment", cascade="all, delete-orphan")

    # Indexes for performance
    __table_args__ = (
        Index("idx_assessments_tenant_status", "tenant_id", "status"),
        Index("idx_assessments_created_by", "created_by"),
    )

    def __repr__(self):
        return f"<Assessment(id={self.id}, title={self.title}, tenant_id={self.tenant_id}, status={self.status})>"
