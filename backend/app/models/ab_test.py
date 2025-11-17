"""
A/B Test Models

AI-powered A/B testing with Thompson Sampling for automatic optimization.
"""

from datetime import datetime
from uuid import uuid4
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Float, Enum, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class ABTestStatus(str, enum.Enum):
    """A/B test status"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ABTestType(str, enum.Enum):
    """Type of A/B test"""
    QUESTION_ORDER = "question_order"
    CTA_TEXT = "cta_text"
    CTA_COLOR = "cta_color"
    INTRO_TEXT = "intro_text"
    CUSTOM = "custom"


class ABTest(Base):
    """
    A/B Test model for automatic conversion optimization.

    Uses Thompson Sampling (Bayesian bandit algorithm) to automatically
    allocate traffic to the best-performing variant.
    """

    __tablename__ = "ab_tests"

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
    created_by: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Test Info
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Test name (e.g., 'CTA Button Color Test')"
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    test_type: Mapped[ABTestType] = mapped_column(
        Enum(ABTestType),
        nullable=False,
        default=ABTestType.CUSTOM
    )

    # Configuration
    traffic_allocation: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
        comment="Percentage of traffic to include in test (0.0-1.0)"
    )
    min_sample_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
        comment="Minimum impressions per variant before optimization"
    )
    confidence_threshold: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.95,
        comment="Statistical confidence threshold (0.90-0.99)"
    )

    # Thompson Sampling Parameters
    exploration_rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.1,
        comment="Exploration vs exploitation balance (0.0-1.0)"
    )

    # Status
    status: Mapped[ABTestStatus] = mapped_column(
        Enum(ABTestStatus),
        nullable=False,
        default=ABTestStatus.DRAFT,
        index=True
    )

    # Statistics (aggregated from variants)
    total_impressions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    total_conversions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    overall_conversion_rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0
    )

    # Winner
    winner_variant_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="Winning variant (if test is completed)"
    )

    # Metadata
    started_at: Mapped[datetime | None] = mapped_column(
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
    variants: Mapped[list["ABTestVariant"]] = relationship(
        "ABTestVariant",
        back_populates="ab_test",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ABTest(id={self.id}, name='{self.name}', status='{self.status}')>"


class ABTestVariant(Base):
    """
    A/B Test Variant (A, B, C, etc.)

    Tracks performance metrics for each variant using Bayesian statistics.
    """

    __tablename__ = "ab_test_variants"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    # Foreign Keys
    ab_test_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ab_tests.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    tenant_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Variant Info
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Variant name (A, B, C, Control, etc.)"
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )
    is_control: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this is the control variant"
    )

    # Variant Configuration (JSONB for flexibility)
    config: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Variant-specific configuration"
    )
    # Example config:
    # {
    #   "cta_text": "今すぐ診断を始める",
    #   "cta_color": "#FF5722",
    #   "question_order": [1, 3, 2, 4, 5]
    # }

    # Performance Metrics
    impressions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of times this variant was shown"
    )
    conversions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of successful conversions"
    )
    conversion_rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Conversion rate (conversions / impressions)"
    )

    # Thompson Sampling (Bayesian Statistics)
    alpha: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
        comment="Beta distribution alpha parameter (successes + 1)"
    )
    beta: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
        comment="Beta distribution beta parameter (failures + 1)"
    )
    thompson_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Latest Thompson Sampling score"
    )

    # Traffic Allocation
    current_traffic_allocation: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Current traffic allocation ratio (0.0-1.0)"
    )

    # Statistical Confidence
    confidence_interval_lower: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0
    )
    confidence_interval_upper: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0
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
    ab_test: Mapped["ABTest"] = relationship(
        "ABTest",
        back_populates="variants"
    )

    def __repr__(self) -> str:
        return f"<ABTestVariant(id={self.id}, name='{self.name}', conversion_rate={self.conversion_rate:.2%})>"

    def update_statistics(self):
        """Update conversion rate and Bayesian parameters"""
        if self.impressions > 0:
            self.conversion_rate = self.conversions / self.impressions
        else:
            self.conversion_rate = 0.0

        # Update Beta distribution parameters
        # Alpha = successes + 1 (prior of 1)
        # Beta = failures + 1 (prior of 1)
        self.alpha = float(self.conversions + 1)
        self.beta = float(self.impressions - self.conversions + 1)
