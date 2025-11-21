"""
Response and Answer Schemas

Pydantic models for Response and Answer API request/response validation.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AnswerBase(BaseModel):
    """Base answer schema"""

    question_id: UUID
    answer_text: Optional[str] = None
    points_awarded: int = Field(default=0, ge=0)


class AnswerCreate(AnswerBase):
    """Schema for creating a new answer"""

    pass


class AnswerResponse(AnswerBase):
    """Schema for answer response"""

    id: UUID
    response_id: UUID
    answered_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResponseBase(BaseModel):
    """Base response schema"""

    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, max_length=255)


class ResponseCreate(ResponseBase):
    """Schema for creating a new response session"""

    pass


class ResponseUpdate(BaseModel):
    """Schema for updating a response"""

    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = None  # in_progress, completed, abandoned
    total_score: Optional[int] = Field(None, ge=0)


class ResponseSubmit(BaseModel):
    """Schema for submitting answers to a response"""

    answers: List[AnswerCreate]
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, max_length=255)


class ResponseResponse(ResponseBase):
    """Schema for response response"""

    id: UUID
    assessment_id: UUID
    session_id: str
    status: str
    total_score: int
    ip_address: Optional[str]
    user_agent: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    answers: List[AnswerResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ResponseWithLeadData(ResponseSubmit):
    """Schema for completing assessment and creating lead"""

    company: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


class ResponseSummary(BaseModel):
    """Schema for response summary (analytics)"""

    total_responses: int
    completed_responses: int
    abandoned_responses: int
    average_score: float
    completion_rate: float


class PublicAssessmentResponse(BaseModel):
    """Schema for public assessment data (for embed widget)"""

    id: UUID
    title: str
    description: Optional[str]
    questions: List[dict]  # Simplified question structure for frontend
