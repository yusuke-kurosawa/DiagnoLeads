"""
AI Schemas

Pydantic models for AI-related requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class AssessmentGenerationRequest(BaseModel):
    """Request to generate an assessment using AI"""

    topic: str = Field(
        ..., min_length=1, max_length=255, description="Topic for the assessment"
    )
    industry: str = Field(
        ..., min_length=1, max_length=255, description="Target industry"
    )
    num_questions: int = Field(
        default=5, ge=3, le=20, description="Number of questions to generate"
    )


class QuestionOption(BaseModel):
    """Option for a question"""

    id: str
    text: str
    score: int = Field(ge=0, le=100)


class Question(BaseModel):
    """Assessment question"""

    id: int
    text: str
    type: str = Field(description="single_choice|multiple_choice|text|slider")
    options: List[QuestionOption]
    explanation: Optional[str] = None


class GeneratedAssessment(BaseModel):
    """Generated assessment structure"""

    title: str
    description: str
    questions: List[Question]


class AssessmentGenerationResponse(BaseModel):
    """Response from assessment generation"""

    success: bool
    data: Optional[GeneratedAssessment] = None
    error: Optional[str] = None
    usage: Optional[Dict[str, int]] = None  # Token usage


class IdentifiedNeed(BaseModel):
    """Identified need from lead analysis"""

    area: str
    description: str
    priority: str = Field(description="high|medium|low")


class LeadInsights(BaseModel):
    """Lead insights analysis result"""

    overall_score: int = Field(ge=0, le=100)
    hot_lead: bool
    identified_needs: List[IdentifiedNeed]
    recommendation: str
    key_talking_points: List[str]
    recommended_action: Optional[str] = Field(
        None, description="Industry-specific recommended next action"
    )
    priority_level: Optional[str] = Field(
        None, description="Automatic priority level: critical|high|medium|low"
    )
    follow_up_timing: Optional[str] = Field(
        None, description="Recommended follow-up timing"
    )


class LeadAnalysisRequest(BaseModel):
    """Request to analyze lead responses"""

    assessment_responses: Dict[str, Any] = Field(
        ..., description="Question ID to response mapping"
    )
    assessment_title: Optional[str] = Field(
        default="Assessment", description="Name of the assessment"
    )
    industry: Optional[str] = Field(
        default="general", description="Target industry for analysis context"
    )


class LeadAnalysisResponse(BaseModel):
    """Response from lead analysis"""

    success: bool
    data: Optional[LeadInsights] = None
    error: Optional[str] = None
    usage: Optional[Dict[str, int]] = None


class RephraseRequest(BaseModel):
    """Request to rephrase content"""

    text: str = Field(
        ..., min_length=1, max_length=2000, description="Text to rephrase"
    )
    style: str = Field(
        default="professional",
        description="Style: professional|casual|technical|simple",
    )
    target_audience: str = Field(
        default="general", description="Target audience (executives, developers, etc.)"
    )


class RephraseResponse(BaseModel):
    """Response from rephrase request"""

    success: bool
    data: Optional[Dict[str, Any]] = None  # Contains original, rephrased, alternatives
    error: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
