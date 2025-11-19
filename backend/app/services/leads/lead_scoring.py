"""
Lead Scoring Service

リードスコアリング機能を提供します。
"""

from typing import List
from uuid import UUID

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from app.models.lead import Lead


class LeadScoringService:
    """リードスコアリングサービス"""

    def __init__(self, db: Session):
        self.db = db

    def get_hot_leads(self, tenant_id: UUID, threshold: int = 61) -> List[Lead]:
        """
        Get hot leads (score >= threshold) for a tenant

        Args:
            tenant_id: テナントID
            threshold: ホットリードのスコア閾値（デフォルト: 61）

        Returns:
            ホットリードのリスト（スコアの高い順）
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
