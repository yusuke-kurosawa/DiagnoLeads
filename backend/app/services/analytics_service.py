"""
Analytics Service

Business logic for analytics and reporting with multi-tenant support.
"""

from uuid import UUID
from typing import Dict, List, Any
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.lead import Lead
from app.models.assessment import Assessment
from app.core.constants import LeadScoreThreshold
from app.utils.helpers import (
    count_by_attribute,
    calculate_average_score,
    calculate_conversion_rate,
    group_by_date,
    parse_period_to_days,
    classify_lead_by_score,
    get_date_range_from_period,
    safe_divide,
)


class AnalyticsService:
    """
    Analytics service with strict multi-tenant isolation

    **IMPORTANT**: All methods enforce tenant_id filtering
    """

    def __init__(self, db: Session):
        self.db = db

    def get_overview(self, tenant_id: UUID) -> Dict[str, Any]:
        """
        Get overview analytics for dashboard
        """
        lead_analytics = self.get_lead_analytics(tenant_id)
        assessment_analytics = self.get_assessment_analytics(tenant_id)

        return {
            "tenant_id": str(tenant_id),
            "period": "all_time",
            "leads": lead_analytics,
            "assessments": assessment_analytics,
            "generated_at": datetime.utcnow().isoformat(),
        }

    def get_lead_analytics(self, tenant_id: UUID) -> Dict[str, Any]:
        """
        Get detailed lead analytics
        """
        # Get all leads for tenant
        leads = self.db.query(Lead).filter(
            Lead.tenant_id == tenant_id
        ).all()

        if not leads:
            return self._empty_lead_analytics()

        # Status counts using helper
        status_counts = count_by_attribute(leads, 'status')

        # Score distribution
        score_distribution = self._count_by_score_range(leads)

        # Average score using helper
        scores = [lead.score for lead in leads]
        average_score = calculate_average_score(scores)

        # Conversion rate using helper
        converted = status_counts.get("converted", 0)
        conversion_rate = calculate_conversion_rate(converted, len(leads))

        return {
            "total": len(leads),
            "new": status_counts.get("new", 0),
            "contacted": status_counts.get("contacted", 0),
            "qualified": status_counts.get("qualified", 0),
            "converted": status_counts.get("converted", 0),
            "disqualified": status_counts.get("disqualified", 0),
            "hot_leads": score_distribution.get("hot", 0),
            "warm_leads": score_distribution.get("warm", 0),
            "cold_leads": score_distribution.get("cold", 0),
            "average_score": average_score,
            "conversion_rate": conversion_rate,
        }

    def get_assessment_analytics(self, tenant_id: UUID) -> Dict[str, Any]:
        """
        Get detailed assessment analytics
        """
        # Get all assessments for tenant
        assessments = self.db.query(Assessment).filter(
            Assessment.tenant_id == tenant_id
        ).all()

        if not assessments:
            return self._empty_assessment_analytics()

        # Status counts using helper
        status_counts = count_by_attribute(assessments, 'status')

        # AI generation counts using helper
        ai_counts = count_by_attribute(assessments, 'ai_generated')

        return {
            "total": len(assessments),
            "published": status_counts.get("published", 0),
            "draft": status_counts.get("draft", 0),
            "archived": status_counts.get("archived", 0),
            "ai_generated": ai_counts.get("ai", 0),
            "manual_created": ai_counts.get("manual", 0),
            "hybrid": ai_counts.get("hybrid", 0),
        }

    def get_trends(
        self, tenant_id: UUID, period: str = "30d", metric: str = "leads"
    ) -> Dict[str, Any]:
        """
        Get trend data for a specific metric

        Args:
            period: "7d", "30d", "90d"
            metric: "leads", "assessments", "score"
        """
        # Use helper to get date range
        start_date, end_date = get_date_range_from_period(period)

        if metric == "leads":
            return self._get_lead_trends(tenant_id, start_date, end_date)
        elif metric == "assessments":
            return self._get_assessment_trends(tenant_id, start_date, end_date)
        else:
            return {"error": "Invalid metric"}

    def _get_lead_trends(
        self, tenant_id: UUID, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Get lead creation trends"""
        # Query leads within date range
        leads = self.db.query(Lead).filter(
            and_(
                Lead.tenant_id == tenant_id,
                Lead.created_at >= start_date,
                Lead.created_at <= end_date,
            )
        ).all()

        # Group by date using helper
        data_points = group_by_date(leads, 'created_at', start_date, end_date)

        # Calculate summary
        total = len(leads)
        days_count = (end_date - start_date).days + 1
        average_per_day = safe_divide(total, days_count)

        return {
            "period": f"{days_count}d",
            "metric": "leads",
            "data_points": data_points,
            "summary": {
                "total": total,
                "average_per_day": round(average_per_day, 2),
            },
        }

    def _get_assessment_trends(
        self, tenant_id: UUID, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Get assessment creation trends"""
        assessments = self.db.query(Assessment).filter(
            and_(
                Assessment.tenant_id == tenant_id,
                Assessment.created_at >= start_date,
                Assessment.created_at <= end_date,
            )
        ).all()

        # Group by date using helper
        data_points = group_by_date(assessments, 'created_at', start_date, end_date)

        total = len(assessments)
        days_count = (end_date - start_date).days + 1
        average_per_day = safe_divide(total, days_count)

        return {
            "period": f"{days_count}d",
            "metric": "assessments",
            "data_points": data_points,
            "summary": {
                "total": total,
                "average_per_day": round(average_per_day, 2),
            },
        }

    # Helper methods

    def _count_by_score_range(self, leads: List[Lead]) -> Dict[str, int]:
        """
        Count leads by score range (hot/warm/cold) using constants
        """
        hot = sum(1 for lead in leads if lead.score >= LeadScoreThreshold.HOT_MIN)
        warm = sum(
            1 for lead in leads
            if LeadScoreThreshold.WARM_MIN <= lead.score < LeadScoreThreshold.HOT_MIN
        )
        cold = sum(1 for lead in leads if lead.score < LeadScoreThreshold.WARM_MIN)

        return {"hot": hot, "warm": warm, "cold": cold}

    def _empty_lead_analytics(self) -> Dict[str, Any]:
        """Return empty lead analytics"""
        return {
            "total": 0,
            "new": 0,
            "contacted": 0,
            "qualified": 0,
            "converted": 0,
            "disqualified": 0,
            "hot_leads": 0,
            "warm_leads": 0,
            "cold_leads": 0,
            "average_score": 0.0,
            "conversion_rate": 0.0,
        }

    def _empty_assessment_analytics(self) -> Dict[str, Any]:
        """Return empty assessment analytics"""
        return {
            "total": 0,
            "published": 0,
            "draft": 0,
            "archived": 0,
            "ai_generated": 0,
            "manual_created": 0,
            "hybrid": 0,
        }
