"""
QuestionOption Model

Represents answer choices for multiple choice questions.
"""

from sqlalchemy import Column, String, ForeignKey, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class QuestionOption(Base):
    """QuestionOption model for multiple choice answer options"""

    __tablename__ = "question_options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Option content
    text = Column(String(255), nullable=False)  # Option text displayed to user
    points = Column(
        Integer, default=0, nullable=False
    )  # Points awarded for selecting this option
    order = Column(Integer, nullable=False)  # Display order within question

    # Relationships
    question = relationship("Question", back_populates="options")

    # Indexes for performance
    __table_args__ = (
        Index("idx_question_options_question_order", "question_id", "order"),
        Index("idx_question_options_question_id", "question_id"),
    )

    def __repr__(self):
        return f"<QuestionOption(id={self.id}, question_id={self.question_id}, text={self.text})>"
