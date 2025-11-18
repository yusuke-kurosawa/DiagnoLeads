"""
Response Model

Represents a user's response session to an assessment.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Response(Base):
    """Response model for assessment response sessions"""

    __tablename__ = "responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Session tracking
    session_id = Column(
        String(255), nullable=False, unique=True
    )  # Unique session identifier

    # Respondent information (optional - collected at end for lead generation)
    email = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)

    # Response status
    status = Column(
        String(50), default="in_progress", nullable=False
    )  # in_progress, completed, abandoned

    # Scoring
    total_score = Column(Integer, default=0, nullable=False)

    # Analytics and tracking
    ip_address = Column(String(100), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Timestamps
    started_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    assessment = relationship("Assessment", back_populates="responses")
    answers = relationship(
        "Answer",
        back_populates="response",
        cascade="all, delete-orphan",
        order_by="Answer.answered_at",
    )
    leads = relationship("Lead", back_populates="response")

    # Indexes for performance
    __table_args__ = (
        Index("idx_responses_assessment_completed", "assessment_id", "completed_at"),
        Index("idx_responses_session_id", "session_id"),
        Index("idx_responses_assessment_id", "assessment_id"),
        Index("idx_responses_status", "status"),
    )

    def __repr__(self):
        return f"<Response(id={self.id}, assessment_id={self.assessment_id}, session_id={self.session_id}, status={self.status})>"
