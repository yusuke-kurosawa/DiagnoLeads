"""
Error Log Model

Records all application errors, API failures, and exceptions for debugging and monitoring.
"""

import enum
import uuid

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ErrorType(str, enum.Enum):
    """Error type categories"""

    API_ERROR = "API_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    AI_SERVICE_ERROR = "AI_SERVICE_ERROR"
    INTEGRATION_ERROR = "INTEGRATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    CICD_ERROR = "CICD_ERROR"
    FRONTEND_ERROR = "FRONTEND_ERROR"


class ErrorSeverity(str, enum.Enum):
    """Error severity levels"""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Environment(str, enum.Enum):
    """Environment types"""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"
    CICD = "cicd"


class ErrorLog(Base):
    """Error log for tracking all application errors"""

    __tablename__ = "error_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Error classification
    error_type = Column(String(100), nullable=False, index=True)
    error_code = Column(String(20), nullable=True)
    severity = Column(String(20), nullable=False, default=ErrorSeverity.MEDIUM.value)

    # Error details
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)

    # Request context
    endpoint = Column(String(200), nullable=True, index=True)
    method = Column(String(10), nullable=True)  # GET, POST, PUT, DELETE, PATCH
    status_code = Column(Integer, nullable=True)

    # Request/Response data
    request_body = Column(JSON, nullable=True)
    request_headers = Column(JSON, nullable=True)
    response_body = Column(JSON, nullable=True)

    # Performance metrics
    duration_ms = Column(Integer, nullable=True)

    # Environment & metadata
    environment = Column(String(20), nullable=False, default=Environment.DEVELOPMENT.value)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)

    # Additional context
    context = Column(JSON, nullable=True)  # Flexible field for extra data
    correlation_id = Column(String(100), nullable=True, index=True)  # For tracing related errors

    # CICD specific
    workflow_name = Column(String(200), nullable=True)  # GitHub Actions workflow
    job_name = Column(String(200), nullable=True)
    run_id = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    tenant = relationship("Tenant")
    user = relationship("User")

    def __repr__(self):
        return f"<ErrorLog(id={self.id}, type={self.error_type}, message={self.error_message[:50]})>"
