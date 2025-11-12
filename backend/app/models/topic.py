"""
Topic Model

Represents a topic/category for organizing assessments.
Each topic belongs to a specific tenant for multi-tenancy support.
"""

from sqlalchemy import String, Integer, Boolean, ForeignKey, DateTime, UniqueConstraint, Column
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from uuid import uuid4

from app.core.database import Base


class Topic(Base):
    """Topic model for assessment categorization"""

    __tablename__ = "topics"

    # Primary key and foreign keys
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Core attributes
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    color = Column(String(7), nullable=True)  # HEX color code #RRGGBB
    icon = Column(String(50), nullable=True)  # lucide-react icon name

    # Management attributes
    sort_order = Column(Integer, default=999, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="topics")
    assessments = relationship("Assessment", back_populates="topic")

    # Constraints
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_topics_tenant_name"),
    )

    def __repr__(self):
        return f"<Topic(id={self.id}, tenant_id={self.tenant_id}, name={self.name})>"
