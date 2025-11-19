"""
Lead Search Service

検索・フィルタリング機能を提供します。
"""

from typing import List
from uuid import UUID

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.lead import Lead


class LeadSearchService:
    """リード検索サービス"""

    def __init__(self, db: Session):
        self.db = db

    def search(self, tenant_id: UUID, query: str, limit: int = 10) -> List[Lead]:
        """
        Search leads by name, email, or company

        Args:
            tenant_id: テナントID
            query: 検索クエリ
            limit: 最大結果数

        Returns:
            マッチしたリードのリスト
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
