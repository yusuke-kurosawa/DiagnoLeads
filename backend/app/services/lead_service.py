"""
Lead Service

Business logic for lead management with multi-tenant support.
"""

from uuid import UUID
from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_
from fastapi import HTTPException, status

from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate, LeadStatusUpdate, LeadScoreUpdate


class LeadService:
    """
    Lead service with strict multi-tenant isolation
    
    **IMPORTANT**: All methods enforce tenant_id filtering
    """

    def __init__(self, db: Session):
        self.db = db

    def list_by_tenant(
        self,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        min_score: Optional[int] = None,
        max_score: Optional[int] = None,
        assigned_to: Optional[UUID] = None,
    ) -> List[Lead]:
        """
        List all leads for a specific tenant with optional filters
        """
        query = self.db.query(Lead).filter(
            Lead.tenant_id == tenant_id  # REQUIRED: Tenant filtering
        )

        # Optional filters
        if status:
            query = query.filter(Lead.status == status)
        
        if min_score is not None:
            query = query.filter(Lead.score >= min_score)
        
        if max_score is not None:
            query = query.filter(Lead.score <= max_score)
        
        if assigned_to:
            query = query.filter(Lead.assigned_to == assigned_to)

        # Sort by score (highest first), then creation date
        leads = (
            query.order_by(desc(Lead.score), desc(Lead.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

        return leads

    def get_by_id(self, lead_id: UUID, tenant_id: UUID) -> Optional[Lead]:
        """
        Get lead by ID with tenant isolation
        """
        lead = self.db.query(Lead).filter(
            and_(
                Lead.id == lead_id,
                Lead.tenant_id == tenant_id,  # REQUIRED: Tenant filtering
            )
        ).first()

        return lead

    def get_by_email(self, email: str, tenant_id: UUID) -> Optional[Lead]:
        """
        Get lead by email with tenant isolation
        """
        lead = self.db.query(Lead).filter(
            and_(
                Lead.email == email,
                Lead.tenant_id == tenant_id,  # REQUIRED: Tenant filtering
            )
        ).first()

        return lead

    def create(
        self, data: LeadCreate, tenant_id: UUID, created_by: UUID
    ) -> Lead:
        """
        Create a new lead
        
        Raises:
            HTTPException: If email already exists in tenant
        """
        # Check for duplicate email within tenant
        existing_lead = self.get_by_email(email=data.email, tenant_id=tenant_id)
        if existing_lead:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Lead with email {data.email} already exists in this tenant",
            )

        lead = Lead(
            **data.model_dump(),
            tenant_id=tenant_id,  # REQUIRED: Set tenant_id
            created_by=created_by,
            score=0,  # Initialize score
            last_activity_at=datetime.utcnow(),
        )

        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)

        return lead

    def update(
        self, lead_id: UUID, data: LeadUpdate, tenant_id: UUID, updated_by: UUID
    ) -> Optional[Lead]:
        """
        Update an existing lead
        """
        # Get lead with tenant filtering
        lead = self.get_by_id(lead_id=lead_id, tenant_id=tenant_id)

        if not lead:
            return None

        # Check email uniqueness if email is being updated
        update_data = data.model_dump(exclude_unset=True)
        if "email" in update_data and update_data["email"] != lead.email:
            existing_lead = self.get_by_email(
                email=update_data["email"], tenant_id=tenant_id
            )
            if existing_lead:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Lead with email {update_data['email']} already exists in this tenant",
                )

        # Update fields
        for field, value in update_data.items():
            setattr(lead, field, value)

        lead.updated_by = updated_by
        lead.last_activity_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(lead)

        return lead

    def update_status(
        self, lead_id: UUID, data: LeadStatusUpdate, tenant_id: UUID, updated_by: UUID
    ) -> Optional[Lead]:
        """
        Update lead status with validation
        """
        lead = self.get_by_id(lead_id=lead_id, tenant_id=tenant_id)

        if not lead:
            return None

        # Status transition validation
        old_status = lead.status
        new_status = data.status

        # Cannot change from 'converted'
        if old_status == "converted" and new_status != "converted":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change status from 'converted'",
            )

        lead.status = new_status
        lead.updated_by = updated_by
        lead.last_activity_at = datetime.utcnow()

        # Update last_contacted_at if status is 'contacted'
        if new_status == "contacted" and old_status == "new":
            lead.last_contacted_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(lead)

        return lead

    def update_score(
        self, lead_id: UUID, data: LeadScoreUpdate, tenant_id: UUID
    ) -> Optional[Lead]:
        """
        Update lead score
        """
        lead = self.get_by_id(lead_id=lead_id, tenant_id=tenant_id)

        if not lead:
            return None

        lead.score = data.score
        lead.last_activity_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(lead)

        return lead

    def delete(self, lead_id: UUID, tenant_id: UUID) -> bool:
        """
        Delete a lead (physical delete for GDPR compliance)
        """
        lead = self.get_by_id(lead_id=lead_id, tenant_id=tenant_id)

        if not lead:
            return False

        self.db.delete(lead)
        self.db.commit()

        return True

    def count_by_tenant(
        self, tenant_id: UUID, status: Optional[str] = None
    ) -> int:
        """
        Count leads for a tenant
        """
        query = self.db.query(Lead).filter(
            Lead.tenant_id == tenant_id  # REQUIRED: Tenant filtering
        )

        if status:
            query = query.filter(Lead.status == status)

        return query.count()

    def search(
        self, tenant_id: UUID, query: str, limit: int = 10
    ) -> List[Lead]:
        """
        Search leads by name, email, or company
        """
        search_pattern = f"%{query}%"

        leads = (
            self.db.query(Lead)
            .filter(
                and_(
                    Lead.tenant_id == tenant_id,  # REQUIRED: Tenant filtering
                    or_(
                        Lead.name.ilike(search_pattern),
                        Lead.email.ilike(search_pattern),
                        Lead.company.ilike(search_pattern),
                    ),
                )
            )
            .limit(limit)
            .all()
        )

        return leads

    def get_hot_leads(self, tenant_id: UUID, threshold: int = 61) -> List[Lead]:
        """
        Get hot leads (score >= threshold) for a tenant
        """
        leads = (
            self.db.query(Lead)
            .filter(
                and_(
                    Lead.tenant_id == tenant_id,  # REQUIRED: Tenant filtering
                    Lead.score >= threshold,
                    Lead.status.in_(["new", "contacted", "qualified"]),
                )
            )
            .order_by(desc(Lead.score))
            .all()
        )

        return leads
