"""
Lead CRUD Service

リードの基本的なCRUD操作を提供します。
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.schemas.lead import LeadUpdate


class LeadCRUDService:
    """リードCRUDサービス"""

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

        Args:
            tenant_id: テナントID
            skip: スキップする件数
            limit: 最大取得件数
            status: ステータスフィルタ
            min_score: 最小スコア
            max_score: 最大スコア
            assigned_to: 担当者ID

        Returns:
            リードのリスト
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
        leads = query.order_by(desc(Lead.score), desc(Lead.created_at)).offset(skip).limit(limit).all()

        return leads

    def get_by_id(self, lead_id: UUID, tenant_id: UUID) -> Optional[Lead]:
        """
        Get lead by ID with tenant isolation

        Args:
            lead_id: リードID
            tenant_id: テナントID

        Returns:
            リード、または存在しない場合はNone
        """
        lead = (
            self.db.query(Lead)
            .filter(
                and_(
                    Lead.id == lead_id,
                    Lead.tenant_id == tenant_id,  # REQUIRED: Tenant filtering
                )
            )
            .first()
        )

        return lead

    def get_by_email(self, email: str, tenant_id: UUID) -> Optional[Lead]:
        """
        Get lead by email with tenant isolation

        Args:
            email: メールアドレス
            tenant_id: テナントID

        Returns:
            リード、または存在しない場合はNone
        """
        lead = (
            self.db.query(Lead)
            .filter(
                and_(
                    Lead.email == email,
                    Lead.tenant_id == tenant_id,  # REQUIRED: Tenant filtering
                )
            )
            .first()
        )

        return lead

    def update(self, lead_id: UUID, data: LeadUpdate, tenant_id: UUID, updated_by: UUID) -> Optional[Lead]:
        """
        Update an existing lead

        Args:
            lead_id: リードID
            data: 更新データ
            tenant_id: テナントID
            updated_by: 更新者ID

        Returns:
            更新後のリード、または存在しない場合はNone

        Raises:
            HTTPException: メールアドレスが重複している場合
        """
        # Get lead with tenant filtering
        lead = self.get_by_id(lead_id=lead_id, tenant_id=tenant_id)

        if not lead:
            return None

        # Check email uniqueness if email is being updated
        update_data = data.model_dump(exclude_unset=True)
        if "email" in update_data and update_data["email"] != lead.email:
            existing_lead = self.get_by_email(email=update_data["email"], tenant_id=tenant_id)
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

    def delete(self, lead_id: UUID, tenant_id: UUID) -> bool:
        """
        Delete a lead (physical delete for GDPR compliance)

        Args:
            lead_id: リードID
            tenant_id: テナントID

        Returns:
            削除成功の場合True、リードが存在しない場合False
        """
        lead = self.get_by_id(lead_id=lead_id, tenant_id=tenant_id)

        if not lead:
            return False

        self.db.delete(lead)
        self.db.commit()

        return True

    def count_by_tenant(self, tenant_id: UUID, status: Optional[str] = None) -> int:
        """
        Count leads for a tenant

        Args:
            tenant_id: テナントID
            status: ステータスフィルタ（オプション）

        Returns:
            リード数
        """
        query = self.db.query(Lead).filter(
            Lead.tenant_id == tenant_id  # REQUIRED: Tenant filtering
        )

        if status:
            query = query.filter(Lead.status == status)

        return query.count()
