"""Google Analytics Integration Model

Manages GA4 integration settings per tenant.
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base


class GoogleAnalyticsIntegration(Base):
    """Google Analytics 4 Integration Model

    Stores GA4 configuration per tenant for:
    - Frontend (React admin) tracking
    - Embed widget tracking
    - Server-side event tracking via Measurement Protocol
    """
    __tablename__ = "google_analytics_integrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )

    # GA4 Configuration
    measurement_id = Column(String(20), nullable=False)  # Format: G-XXXXXXXXXX
    measurement_protocol_api_secret = Column(String(255), nullable=True)  # Encrypted storage recommended

    # Feature Flags
    enabled = Column(Boolean, default=True, nullable=False, index=True)
    track_frontend = Column(Boolean, default=True, nullable=False)  # React admin dashboard
    track_embed_widget = Column(Boolean, default=True, nullable=False)  # Embedded assessment widget
    track_server_events = Column(Boolean, default=False, nullable=False)  # Server-side Measurement Protocol

    # Custom Configuration
    custom_dimensions = Column(JSONB, nullable=True)  # Store custom GA4 dimensions/metrics config

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="google_analytics_integration")

    def __repr__(self):
        return f"<GoogleAnalyticsIntegration(id={self.id}, tenant_id={self.tenant_id}, measurement_id={self.measurement_id})>"

    def to_dict(self, include_secret: bool = False):
        """Convert to dictionary

        Args:
            include_secret: Include API secret in output (default: False for security)
        """
        data = {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id),
            "measurement_id": self.measurement_id,
            "enabled": self.enabled,
            "track_frontend": self.track_frontend,
            "track_embed_widget": self.track_embed_widget,
            "track_server_events": self.track_server_events,
            "custom_dimensions": self.custom_dimensions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_secret:
            data["measurement_protocol_api_secret"] = self.measurement_protocol_api_secret

        return data

    @staticmethod
    def validate_measurement_id(measurement_id: str) -> bool:
        """Validate GA4 Measurement ID format

        Args:
            measurement_id: GA4 Measurement ID (e.g., G-XXXXXXXXXX)

        Returns:
            True if valid format, False otherwise
        """
        import re
        pattern = r'^G-[A-Z0-9]{10}$'
        return bool(re.match(pattern, measurement_id))
