"""
Assessment API Endpoints

REST API for assessment CRUD operations with multi-tenant support.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentResponse,
    AssessmentUpdate,
)
from app.services.assessment_service import AssessmentService

router = APIRouter()


@router.get(
    "/tenants/{tenant_id}/assessments",
    response_model=List[AssessmentResponse],
    summary="List all assessments for a tenant",
)
async def list_assessments(
    tenant_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: str = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all assessments for a specific tenant

    **Security**: Verifies user belongs to the requested tenant
    """
    # Verify user belongs to this tenant
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this tenant's assessments is forbidden",
        )

    service = AssessmentService(db)
    assessments = service.list_by_tenant(tenant_id=tenant_id, skip=skip, limit=limit, status=status_filter)

    return assessments


@router.get(
    "/tenants/{tenant_id}/assessments/search",
    response_model=List[AssessmentResponse],
    summary="Search assessments by title",
)
async def search_assessments(
    tenant_id: UUID,
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search assessments by title

    **Security**: Only searches within the user's tenant
    """
    # Verify user belongs to this tenant
    if current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")

    service = AssessmentService(db)
    assessments = service.search_by_title(tenant_id=tenant_id, title_query=q, limit=limit)

    return assessments


@router.get(
    "/tenants/{tenant_id}/assessments/{assessment_id}",
    response_model=AssessmentResponse,
    summary="Get assessment by ID",
)
async def get_assessment(
    tenant_id: UUID,
    assessment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific assessment by ID

    **Security**: Verifies user belongs to the tenant and assessment exists
    """
    # Verify user belongs to this tenant
    if current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")

    service = AssessmentService(db)
    assessment = service.get_by_id(assessment_id=assessment_id, tenant_id=tenant_id)

    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    return assessment


@router.post(
    "/tenants/{tenant_id}/assessments",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new assessment",
)
async def create_assessment(
    tenant_id: UUID,
    assessment_data: AssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new assessment

    **Security**: Automatically sets tenant_id and created_by
    """
    # Verify user belongs to this tenant
    if current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")

    service = AssessmentService(db)
    assessment = service.create(data=assessment_data, tenant_id=tenant_id, created_by=current_user.id)

    return assessment


@router.put(
    "/tenants/{tenant_id}/assessments/{assessment_id}",
    response_model=AssessmentResponse,
    summary="Update an assessment",
)
async def update_assessment(
    tenant_id: UUID,
    assessment_id: UUID,
    assessment_data: AssessmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an existing assessment

    **Security**: Verifies tenant ownership before update
    """
    # Verify user belongs to this tenant
    if current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")

    service = AssessmentService(db)

    # Check if assessment exists and belongs to tenant
    existing_assessment = service.get_by_id(assessment_id=assessment_id, tenant_id=tenant_id)

    if not existing_assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    # Update assessment
    assessment = service.update(assessment_id=assessment_id, data=assessment_data, tenant_id=tenant_id)

    return assessment


@router.delete(
    "/tenants/{tenant_id}/assessments/{assessment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an assessment",
)
async def delete_assessment(
    tenant_id: UUID,
    assessment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete an assessment

    **Security**: Verifies tenant ownership before deletion
    """
    # Verify user belongs to this tenant
    if current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")

    service = AssessmentService(db)

    # Check if assessment exists and belongs to tenant
    existing_assessment = service.get_by_id(assessment_id=assessment_id, tenant_id=tenant_id)

    if not existing_assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    # Delete assessment
    service.delete(assessment_id=assessment_id, tenant_id=tenant_id)

    return None
