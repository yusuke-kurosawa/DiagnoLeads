"""
Report Model

Represents custom report definitions for analytics data.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Report(Base):
    """
    Custom report definition

    Allows tenants to create, save, and reuse custom reports with specific
    metrics, filters, and visualization settings.
    """

    __tablename__ = "reports"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Report metadata
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(
        String(50),
        nullable=False,
        default="custom",
        comment="custom|lead_analysis|assessment_performance|conversion_funnel|ai_insights",
    )

    # Report configuration (JSON)
    config = Column(
        JSON,
        nullable=False,
        default=dict,
        comment="""
        Report configuration:
        {
            "metrics": ["leads_total", "conversion_rate", "average_score"],
            "filters": {
                "date_range": {"start": "2024-01-01", "end": "2024-12-31"},
                "status": ["new", "qualified"],
                "score_range": {"min": 60, "max": 100}
            },
            "group_by": "status",  # status|industry|date|assessment
            "visualization": "bar_chart",  # bar_chart|line_chart|pie_chart|table
            "sort_by": "leads_total",
            "sort_order": "desc"
        }
        """,
    )

    # Scheduling (optional)
    is_scheduled = Column(Boolean, default=False, nullable=False)
    schedule_config = Column(
        JSON,
        nullable=True,
        comment="""
        Schedule configuration:
        {
            "frequency": "daily|weekly|monthly",
            "day_of_week": 1,  # For weekly (0=Monday)
            "day_of_month": 1,  # For monthly
            "time": "09:00",
            "timezone": "Asia/Tokyo",
            "recipients": ["user@example.com"]
        }
        """,
    )
    last_generated_at = Column(DateTime, nullable=True)

    # Ownership and visibility
    created_by = Column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_public = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="If true, visible to all users in tenant",
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="reports")
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Report {self.name} (tenant={self.tenant_id})>"
