"""
Lead API Endpoints

REST API for lead CRUD operations with multi-tenant support.
"""

from uuid import UUID
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.lead import (
    LeadCreate,
    LeadUpdate,
    LeadStatusUpdate,
    LeadScoreUpdate,
    LeadResponse,
)
from app.services.lead_service import LeadService

router = APIRouter()


@router.get(
    "/tenants/{tenant_id}/leads/search",
    response_model=List[LeadResponse],
    summary="Search leads",
    operation_id="searchLeads",
)
async def search_leads(
    tenant_id: UUID,
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search leads by name, email, or company"""
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden"
        )

    service = LeadService(db)
    leads = service.search(tenant_id=tenant_id, query=q, limit=limit)

    return leads


@router.get(
    "/tenants/{tenant_id}/leads/hot",
    response_model=List[LeadResponse],
    summary="Get hot leads",
    operation_id="getHotLeads",
)
async def get_hot_leads(
    tenant_id: UUID,
    threshold: int = Query(61, ge=0, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get leads with high scores (hot leads)"""
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden"
        )

    service = LeadService(db)
    leads = service.get_hot_leads(tenant_id=tenant_id, threshold=threshold)

    return leads


@router.get(
    "/tenants/{tenant_id}/leads",
    response_model=List[LeadResponse],
    summary="List all leads",
    operation_id="listLeads",
)
async def list_leads(
    tenant_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None),
    min_score: Optional[int] = Query(None, ge=0, le=100),
    max_score: Optional[int] = Query(None, ge=0, le=100),
    assigned_to: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all leads for a specific tenant with filters"""
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this tenant's leads is forbidden",
        )

    service = LeadService(db)
    leads = service.list_by_tenant(
        tenant_id=tenant_id,
        skip=skip,
        limit=limit,
        status=status,
        min_score=min_score,
        max_score=max_score,
        assigned_to=assigned_to,
    )

    return leads


@router.get(
    "/tenants/{tenant_id}/leads/{lead_id}",
    response_model=LeadResponse,
    summary="Get lead by ID",
    operation_id="getLeadById",
)
async def get_lead(
    tenant_id: UUID,
    lead_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific lead by ID"""
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden"
        )

    service = LeadService(db)
    lead = service.get_by_id(lead_id=lead_id, tenant_id=tenant_id)

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )

    return lead


@router.post(
    "/tenants/{tenant_id}/leads",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new lead",
    operation_id="createLead",
)
async def create_lead(
    tenant_id: UUID,
    lead_data: LeadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new lead"""
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden"
        )

    service = LeadService(db)
    lead = service.create(
        data=lead_data, tenant_id=tenant_id, created_by=current_user.id
    )

    return lead


@router.put(
    "/tenants/{tenant_id}/leads/{lead_id}",
    response_model=LeadResponse,
    summary="Update a lead",
    operation_id="updateLead",
)
async def update_lead(
    tenant_id: UUID,
    lead_id: UUID,
    lead_data: LeadUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing lead"""
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden"
        )

    service = LeadService(db)

    # Check if lead exists
    existing_lead = service.get_by_id(lead_id=lead_id, tenant_id=tenant_id)
    if not existing_lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )

    # Update lead
    lead = service.update(
        lead_id=lead_id,
        data=lead_data,
        tenant_id=tenant_id,
        updated_by=current_user.id,
    )

    return lead


@router.patch(
    "/tenants/{tenant_id}/leads/{lead_id}/status",
    response_model=LeadResponse,
    summary="Update lead status",
    operation_id="updateLeadStatus",
)
async def update_lead_status(
    tenant_id: UUID,
    lead_id: UUID,
    status_data: LeadStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update lead status with validation"""
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden"
        )

    service = LeadService(db)

    # Check if lead exists
    existing_lead = service.get_by_id(lead_id=lead_id, tenant_id=tenant_id)
    if not existing_lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )

    # Update status
    lead = service.update_status(
        lead_id=lead_id,
        data=status_data,
        tenant_id=tenant_id,
        updated_by=current_user.id,
    )

    return lead


@router.patch(
    "/tenants/{tenant_id}/leads/{lead_id}/score",
    response_model=LeadResponse,
    summary="Update lead score",
    operation_id="updateLeadScore",
)
async def update_lead_score(
    tenant_id: UUID,
    lead_id: UUID,
    score_data: LeadScoreUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update lead score"""
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden"
        )

    service = LeadService(db)

    # Check if lead exists
    existing_lead = service.get_by_id(lead_id=lead_id, tenant_id=tenant_id)
    if not existing_lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )

    # Update score
    lead = service.update_score(
        lead_id=lead_id, data=score_data, tenant_id=tenant_id
    )

    return lead


@router.delete(
    "/tenants/{tenant_id}/leads/{lead_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a lead",
    operation_id="deleteLead",
)
async def delete_lead(
    tenant_id: UUID,
    lead_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a lead (physical delete for GDPR compliance)"""
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden"
        )

    service = LeadService(db)

    # Check if lead exists
    existing_lead = service.get_by_id(lead_id=lead_id, tenant_id=tenant_id)
    if not existing_lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )

    # Delete lead
    service.delete(lead_id=lead_id, tenant_id=tenant_id)

    return None
