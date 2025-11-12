"""
AI API Endpoints

Provides AI-powered features including assessment generation, lead analysis, and content rephrasing.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.ai import (
    AssessmentGenerationRequest,
    AssessmentGenerationResponse,
    LeadAnalysisRequest,
    LeadAnalysisResponse,
    RephraseRequest,
    RephraseResponse,
)
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()


@router.post(
    "/tenants/{tenant_id}/ai/assessments",
    response_model=AssessmentGenerationResponse,
    summary="Generate assessment using AI",
)
async def generate_assessment(
    tenant_id: UUID,
    request: AssessmentGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate an assessment structure using Claude AI.

    Takes a topic and industry, generates questions and scoring rules.
    
    **Security**: Only accessible by authenticated users within their tenant.
    """
    # Verify user belongs to this tenant
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden",
        )

    try:
        # Call AI service to generate assessment
        result = await ai_service.generate_assessment(
            topic=request.topic,
            industry=request.industry,
            num_questions=request.num_questions,
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"],
            )

        return AssessmentGenerationResponse(
            success=True,
            data=result["data"],
            usage=result.get("usage"),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Assessment generation failed: {str(e)}",
        )


@router.post(
    "/tenants/{tenant_id}/ai/insights",
    response_model=LeadAnalysisResponse,
    summary="Analyze lead responses and generate insights",
)
async def analyze_lead_responses(
    tenant_id: UUID,
    request: LeadAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analyze lead assessment responses and generate sales insights.

    Provides lead scoring, identified needs, and sales recommendations.
    
    **Security**: Only accessible by authenticated users within their tenant.
    """
    # Verify user belongs to this tenant
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden",
        )

    try:
        # Call AI service to analyze responses
        result = await ai_service.analyze_lead_insights(
            assessment_responses=request.assessment_responses,
            assessment_title=request.assessment_title,
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"],
            )

        return LeadAnalysisResponse(
            success=True,
            data=result["data"],
            usage=result.get("usage"),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lead analysis failed: {str(e)}",
        )


@router.post(
    "/tenants/{tenant_id}/ai/rephrase",
    response_model=RephraseResponse,
    summary="Rephrase content with different style",
)
async def rephrase_content(
    tenant_id: UUID,
    request: RephraseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Rephrase content with different style or for different audience.

    Useful for improving question wording, descriptions, etc.
    
    **Security**: Only accessible by authenticated users within their tenant.
    """
    # Verify user belongs to this tenant
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden",
        )

    try:
        # Call AI service to rephrase content
        result = await ai_service.rephrase_content(
            text=request.text,
            style=request.style,
            target_audience=request.target_audience,
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"],
            )

        return RephraseResponse(
            success=True,
            data=result["data"],
            usage=result.get("usage"),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rephrasing failed: {str(e)}",
        )
