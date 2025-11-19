"""
AI Usage Log Model

Tracks AI API usage for billing, monitoring, and cost optimization.
"""

import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AIUsageLog(Base):
    """Log of AI API usage for monitoring and billing"""

    __tablename__ = "ai_usage_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Operation details
    operation = Column(
        String(100), nullable=False, index=True
    )  # generate_assessment, analyze_lead_insights, rephrase_content
    model = Column(String(100), nullable=False)  # claude-3-5-sonnet-20241022

    # Token usage
    input_tokens = Column(Integer, nullable=False, default=0)
    output_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)

    # Cost tracking (calculated based on model pricing)
    cost_usd = Column(Float, nullable=True)  # Estimated cost in USD

    # Request metadata
    assessment_id = Column(
        UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="SET NULL"), nullable=True
    )
    lead_id = Column(
        UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True
    )

    # Performance metrics
    duration_ms = Column(Integer, nullable=True)  # Request duration in milliseconds
    success = Column(String(20), nullable=False, default="success")  # success, failure

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="ai_usage_logs")
    user = relationship("User")
    assessment = relationship("Assessment")
    lead = relationship("Lead")

    def __repr__(self):
        return (
            f"<AIUsageLog(id={self.id}, operation={self.operation}, "
            f"total_tokens={self.total_tokens}, tenant_id={self.tenant_id})>"
        )

    @property
    def cost_per_1k_input(self) -> float:
        """
        Get cost per 1K input tokens based on model.

        Returns:
            Cost in USD per 1K input tokens
        """
        # Claude 3.5 Sonnet pricing (as of 2024)
        if "sonnet" in self.model.lower():
            return 0.003  # $3 per million = $0.003 per 1K
        return 0.003  # Default

    @property
    def cost_per_1k_output(self) -> float:
        """
        Get cost per 1K output tokens based on model.

        Returns:
            Cost in USD per 1K output tokens
        """
        # Claude 3.5 Sonnet pricing (as of 2024)
        if "sonnet" in self.model.lower():
            return 0.015  # $15 per million = $0.015 per 1K
        return 0.015  # Default

    def calculate_cost(self) -> float:
        """
        Calculate the estimated cost for this API call.

        Returns:
            Cost in USD
        """
        input_cost = (self.input_tokens / 1000) * self.cost_per_1k_input
        output_cost = (self.output_tokens / 1000) * self.cost_per_1k_output
        return round(input_cost + output_cost, 6)

    def update_cost(self):
        """Update the cost_usd field based on token usage"""
        self.cost_usd = self.calculate_cost()
