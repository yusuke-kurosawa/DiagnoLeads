"""
Lead Services Module

リードサービスを提供するモジュールです。
後方互換性を維持するため、既存のLeadServiceインターフェースを保持しています。

モジュール構成:
- lead_crud.py: CRUD操作
- lead_scoring.py: スコアリング機能
- lead_search.py: 検索・フィルタリング
- lead_notifications.py: 通知機能（将来実装予定）
"""

from app.services.leads.lead_crud import LeadCRUDService
from app.services.leads.lead_scoring import LeadScoringService
from app.services.leads.lead_search import LeadSearchService

__all__ = [
    "LeadCRUDService",
    "LeadScoringService",
    "LeadSearchService",
]
