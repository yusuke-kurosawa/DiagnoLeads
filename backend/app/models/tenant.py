"""
Tenant Model

Represents a tenant (organization/company) in the multi-tenant system.
"""

from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Tenant(Base):
    """Tenant model for multi-tenant architecture"""

    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    plan = Column(String(50), default="free", nullable=False)  # free, pro, enterprise
    settings = Column(JSON, default={}, nullable=False)

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
    qr_codes = relationship("QRCode", back_populates="tenant", cascade="all, delete-orphan")
    topics = relationship("Topic", back_populates="tenant", cascade="all, delete-orphan")
    industries = relationship("Industry", back_populates="tenant", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="tenant", cascade="all, delete-orphan")
    google_analytics_integration = relationship(
        "GoogleAnalyticsIntegration",
        back_populates="tenant",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Tenant(id={self.id}, name={self.name}, plan={self.plan})>"
