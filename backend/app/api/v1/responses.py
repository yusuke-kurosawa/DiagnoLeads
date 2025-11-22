"""
Response API Endpoints

Public API for assessment responses (for embed widget).
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.answer import Answer
from app.models.assessment import Assessment
from app.models.lead import Lead
from app.models.question import Question
from app.models.response import Response
from app.schemas.response import (
    PublicAssessmentResponse,
    ResponseResponse,
    ResponseSubmit,
    ResponseWithLeadData,
)

router = APIRouter()


@router.get(
    "/tenants/{tenant_id}/assessments/{assessment_id}/public",
    response_model=PublicAssessmentResponse,
    summary="Get public assessment data (for embed widget)",
)
async def get_public_assessment(
    tenant_id: UUID,
    assessment_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get public assessment data for embedding.

    **No authentication required** - this is a public endpoint.

    Returns assessment with questions and options in a simplified format
    for the embed widget.
    """
    # Find assessment
    assessment = (
        db.query(Assessment)
        .filter(
            Assessment.id == assessment_id,
            Assessment.tenant_id == tenant_id,
            Assessment.status == "published",  # Only published assessments
        )
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found or not published",
        )

    # Get questions with options
    questions = db.query(Question).filter(Question.assessment_id == assessment_id).order_by(Question.order).all()

    # Build simplified question structure for widget
    questions_data = []
    for question in questions:
        question_dict = {
            "id": str(question.id),
            "text": question.text,
            "type": question.type,
            "order": question.order,
            "options": [
                {
                    "id": str(opt.id),
                    "text": opt.text,
                    "points": opt.points,
                    "order": opt.order,
                }
                for opt in question.options
            ],
        }
        questions_data.append(question_dict)

    return PublicAssessmentResponse(
        id=assessment.id,
        title=assessment.title,
        description=assessment.description,
        questions=questions_data,
    )


@router.post(
    "/responses",
    response_model=ResponseResponse,
    summary="Create a new response session",
    status_code=status.HTTP_201_CREATED,
)
async def create_response(
    assessment_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Create a new response session for an assessment.

    **No authentication required** - this is a public endpoint.

    Returns a session ID that should be used for subsequent answer submissions.
    """
    # Verify assessment exists
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    # Generate unique session ID
    session_id = str(uuid4())

    # Create response record
    response = Response(
        assessment_id=assessment_id,
        session_id=session_id,
        status="in_progress",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    db.add(response)
    db.commit()
    db.refresh(response)

    return response


@router.post(
    "/responses/{response_id}/answers",
    response_model=ResponseResponse,
    summary="Submit answers for a response",
)
async def submit_answers(
    response_id: UUID,
    data: ResponseSubmit,
    db: Session = Depends(get_db),
):
    """
    Submit one or more answers to a response session.

    **No authentication required** - this is a public endpoint.

    Updates the response with new answers and calculates total score.
    """
    # Find response
    response = db.query(Response).filter(Response.id == response_id).first()
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response not found",
        )

    # Check if already completed
    if response.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Response already completed",
        )

    # Save each answer
    total_points = 0
    for answer_data in data.answers:
        # Check if answer already exists for this question
        existing_answer = (
            db.query(Answer)
            .filter(
                Answer.response_id == response_id,
                Answer.question_id == answer_data.question_id,
            )
            .first()
        )

        if existing_answer:
            # Update existing answer
            existing_answer.answer_text = answer_data.answer_text
            existing_answer.points_awarded = answer_data.points_awarded
            existing_answer.answered_at = datetime.now(timezone.utc)
        else:
            # Create new answer
            answer = Answer(
                response_id=response_id,
                question_id=answer_data.question_id,
                answer_text=answer_data.answer_text,
                points_awarded=answer_data.points_awarded,
            )
            db.add(answer)

        total_points += answer_data.points_awarded

    # Update response score and user info
    response.total_score = total_points
    if data.email:
        response.email = data.email
    if data.name:
        response.name = data.name

    db.commit()
    db.refresh(response)

    return response


@router.post(
    "/responses/{response_id}/complete",
    response_model=ResponseResponse,
    summary="Complete assessment and create lead",
)
async def complete_response(
    response_id: UUID,
    data: ResponseWithLeadData,
    db: Session = Depends(get_db),
):
    """
    Mark response as completed and optionally create a lead.

    **No authentication required** - this is a public endpoint.

    This finalizes the assessment and creates a lead record
    with the provided contact information.
    """
    # Find response
    response = db.query(Response).filter(Response.id == response_id).first()
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response not found",
        )

    # Check if already completed
    if response.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Response already completed",
        )

    # Save any final answers
    total_points = 0
    for answer_data in data.answers:
        existing_answer = (
            db.query(Answer)
            .filter(
                Answer.response_id == response_id,
                Answer.question_id == answer_data.question_id,
            )
            .first()
        )

        if existing_answer:
            existing_answer.answer_text = answer_data.answer_text
            existing_answer.points_awarded = answer_data.points_awarded
            existing_answer.answered_at = datetime.now(timezone.utc)
        else:
            answer = Answer(
                response_id=response_id,
                question_id=answer_data.question_id,
                answer_text=answer_data.answer_text,
                points_awarded=answer_data.points_awarded,
            )
            db.add(answer)

        total_points += answer_data.points_awarded

    # Update response
    response.total_score = total_points
    response.status = "completed"
    response.completed_at = datetime.now(timezone.utc)

    if data.email:
        response.email = data.email
    if data.name:
        response.name = data.name

    # Create lead if email is provided
    if data.email and data.name:
        # Get assessment to find tenant
        assessment = db.query(Assessment).filter(Assessment.id == response.assessment_id).first()

        if assessment:
            # Check if lead already exists
            existing_lead = (
                db.query(Lead)
                .filter(
                    Lead.tenant_id == assessment.tenant_id,
                    Lead.email == data.email,
                )
                .first()
            )

            if existing_lead:
                # Update existing lead
                existing_lead.score = max(existing_lead.score, total_points)
                existing_lead.response_id = response_id
                if data.company:
                    existing_lead.company = data.company
                if data.job_title:
                    existing_lead.job_title = data.job_title
                if data.phone:
                    existing_lead.phone = data.phone
            else:
                # Create new lead
                lead = Lead(
                    tenant_id=assessment.tenant_id,
                    response_id=response_id,
                    email=data.email,
                    name=data.name,
                    company=data.company,
                    job_title=data.job_title,
                    phone=data.phone,
                    score=total_points,
                    status="new",
                    created_by=assessment.created_by,
                )
                db.add(lead)

    db.commit()
    db.refresh(response)

    return response
