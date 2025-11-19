"""
Audit Log Model

Records all changes to master data for audit trail and compliance.
"""

import enum
import uuid

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AuditAction(str, enum.Enum):
    """Audit log action types"""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class AuditLogEntity(str, enum.Enum):
    """Entity types that can be audited"""

    TENANT = "TENANT"
    USER = "USER"
    TOPIC = "TOPIC"
    INDUSTRY = "INDUSTRY"


class AuditLog(Base):
    """Audit log for tracking master data changes"""

    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # What changed
    entity_type = Column(String(50), nullable=False)  # TENANT, USER, TOPIC, INDUSTRY
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String(20), nullable=False)  # CREATE, UPDATE, DELETE

    # Details
    entity_name = Column(String(255), nullable=True)  # User name, tenant name, etc.
    old_values = Column(JSON, nullable=True)  # Previous values for UPDATE/DELETE
    new_values = Column(JSON, nullable=True)  # New values for CREATE/UPDATE
    reason = Column(Text, nullable=True)  # Optional reason for change

    # Metadata
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    tenant = relationship("Tenant")
    user = relationship("User")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, entity_type={self.entity_type}, action={self.action})>"
