"""
Answer Model

Represents individual question answers within a response session.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Text, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Answer(Base):
    """Answer model for individual question responses"""

    __tablename__ = "answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    response_id = Column(
        UUID(as_uuid=True),
        ForeignKey("responses.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_id = Column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Answer content
    answer_text = Column(Text, nullable=True)  # Answer text or selected option value
    points_awarded = Column(
        Integer, default=0, nullable=False
    )  # Points awarded for this answer

    # Timestamp
    answered_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    response = relationship("Response", back_populates="answers")
    question = relationship("Question", back_populates="answers")

    # Indexes for performance
    __table_args__ = (
        Index("idx_answers_response_id", "response_id"),
        Index("idx_answers_question_id", "question_id"),
        Index("idx_answers_response_question", "response_id", "question_id"),
    )

    def __repr__(self):
        return f"<Answer(id={self.id}, response_id={self.response_id}, question_id={self.question_id})>"
