"""
Assessment Service

Business logic for assessment management with multi-tenant support.
"""

from uuid import UUID
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models.assessment import Assessment
from app.schemas.assessment import AssessmentCreate, AssessmentUpdate


class AssessmentService:
    """
    Assessment service with strict multi-tenant isolation

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
    ) -> List[Assessment]:
        """
        List all assessments for a specific tenant

        Args:
            tenant_id: Tenant ID (REQUIRED for isolation)
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status (optional)

        Returns:
            List of assessments
        """
        query = self.db.query(Assessment).filter(
            Assessment.tenant_id == tenant_id  # REQUIRED: Tenant filtering
        )

        # Optional status filter
        if status:
            query = query.filter(Assessment.status == status)

        # Sort by creation date (newest first) and paginate
        assessments = (
            query.order_by(desc(Assessment.created_at)).offset(skip).limit(limit).all()
        )

        return assessments

    def get_by_id(self, assessment_id: UUID, tenant_id: UUID) -> Optional[Assessment]:
        """
        Get assessment by ID with tenant isolation

        Args:
            assessment_id: Assessment ID
            tenant_id: Tenant ID (REQUIRED for isolation)

        Returns:
            Assessment or None if not found
        """
        assessment = (
            self.db.query(Assessment)
            .filter(
                and_(
                    Assessment.id == assessment_id,
                    Assessment.tenant_id == tenant_id,  # REQUIRED: Tenant filtering
                )
            )
            .first()
        )

        return assessment

    def create(
        self, data: AssessmentCreate, tenant_id: UUID, created_by: UUID
    ) -> Assessment:
        """
        Create a new assessment

        Args:
            data: Assessment creation data
            tenant_id: Tenant ID (REQUIRED for isolation)
            created_by: User ID who created the assessment

        Returns:
            Created assessment
        """
        assessment = Assessment(
            **data.model_dump(),
            tenant_id=tenant_id,  # REQUIRED: Set tenant_id
            created_by=created_by,
        )

        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)

        return assessment

    def update(
        self, assessment_id: UUID, data: AssessmentUpdate, tenant_id: UUID
    ) -> Optional[Assessment]:
        """
        Update an existing assessment

        Args:
            assessment_id: Assessment ID
            data: Update data
            tenant_id: Tenant ID (REQUIRED for isolation)

        Returns:
            Updated assessment or None if not found
        """
        # Get assessment with tenant filtering
        assessment = self.get_by_id(assessment_id=assessment_id, tenant_id=tenant_id)

        if not assessment:
            return None

        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(assessment, field, value)

        self.db.commit()
        self.db.refresh(assessment)

        return assessment

    def delete(self, assessment_id: UUID, tenant_id: UUID) -> bool:
        """
        Delete an assessment

        Args:
            assessment_id: Assessment ID
            tenant_id: Tenant ID (REQUIRED for isolation)

        Returns:
            True if deleted, False if not found
        """
        # Get assessment with tenant filtering
        assessment = self.get_by_id(assessment_id=assessment_id, tenant_id=tenant_id)

        if not assessment:
            return False

        self.db.delete(assessment)
        self.db.commit()

        return True

    def count_by_tenant(self, tenant_id: UUID, status: Optional[str] = None) -> int:
        """
        Count assessments for a tenant

        Args:
            tenant_id: Tenant ID (REQUIRED for isolation)
            status: Filter by status (optional)

        Returns:
            Number of assessments
        """
        query = self.db.query(Assessment).filter(
            Assessment.tenant_id == tenant_id  # REQUIRED: Tenant filtering
        )

        if status:
            query = query.filter(Assessment.status == status)

        return query.count()

    def search_by_title(
        self, tenant_id: UUID, title_query: str, limit: int = 10
    ) -> List[Assessment]:
        """
        Search assessments by title

        Args:
            tenant_id: Tenant ID (REQUIRED for isolation)
            title_query: Search query
            limit: Maximum number of results

        Returns:
            List of matching assessments
        """
        assessments = (
            self.db.query(Assessment)
            .filter(
                and_(
                    Assessment.tenant_id == tenant_id,  # REQUIRED: Tenant filtering
                    Assessment.title.ilike(
                        f"%{title_query}%"
                    ),  # Case-insensitive search
                )
            )
            .limit(limit)
            .all()
        )

        return assessments
