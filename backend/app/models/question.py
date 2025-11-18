"""
Question Model

Represents individual questions within assessments.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Question(Base):
    """Question model for assessment questions"""

    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Question content
    text = Column(Text, nullable=False)
    type = Column(
        String(50), nullable=False
    )  # single_choice, multiple_choice, text, slider
    order = Column(Integer, nullable=False)  # Display order within assessment
    points = Column(Integer, default=0, nullable=False)  # Max points for this question
    explanation = Column(Text, nullable=True)  # Optional explanation shown after answer

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    assessment = relationship("Assessment", back_populates="questions")
    options = relationship(
        "QuestionOption",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="QuestionOption.order",
    )
    answers = relationship(
        "Answer", back_populates="question", cascade="all, delete-orphan"
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_questions_assessment_order", "assessment_id", "order"),
        Index("idx_questions_assessment_id", "assessment_id"),
    )

    def __repr__(self):
        return f"<Question(id={self.id}, assessment_id={self.assessment_id}, text={self.text[:50]}...)>"
