"""
Question and QuestionOption Schemas

Pydantic models for Question and QuestionOption API request/response validation.
"""

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class QuestionOptionBase(BaseModel):
    """Base question option schema"""

    text: str = Field(..., min_length=1, max_length=255)
    points: int = Field(default=0)
    order: int = Field(..., ge=0)


class QuestionOptionCreate(QuestionOptionBase):
    """Schema for creating a new question option"""

    pass


class QuestionOptionUpdate(BaseModel):
    """Schema for updating a question option"""

    text: Optional[str] = Field(None, min_length=1, max_length=255)
    points: Optional[int] = None
    order: Optional[int] = Field(None, ge=0)


class QuestionOptionResponse(QuestionOptionBase):
    """Schema for question option response"""

    id: UUID
    question_id: UUID

    class Config:
        from_attributes = True


class QuestionBase(BaseModel):
    """Base question schema"""

    text: str = Field(..., min_length=1)
    type: str = Field(...)  # single_choice, multiple_choice, text, slider
    order: int = Field(..., ge=0)
    points: int = Field(default=0, ge=0)
    explanation: Optional[str] = None


class QuestionCreate(QuestionBase):
    """Schema for creating a new question"""

    options: List[QuestionOptionCreate] = Field(default_factory=list)


class QuestionUpdate(BaseModel):
    """Schema for updating a question"""

    text: Optional[str] = Field(None, min_length=1)
    type: Optional[str] = None
    order: Optional[int] = Field(None, ge=0)
    points: Optional[int] = Field(None, ge=0)
    explanation: Optional[str] = None
    options: Optional[List[QuestionOptionCreate]] = None


class QuestionResponse(QuestionBase):
    """Schema for question response"""

    id: UUID
    assessment_id: UUID
    created_at: datetime
    options: List[QuestionOptionResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class QuestionWithOptionsCreate(BaseModel):
    """Schema for creating question with options in bulk"""

    questions: List[QuestionCreate]


class QuestionWithOptionsResponse(BaseModel):
    """Schema for questions with options response"""

    questions: List[QuestionResponse]
