"""
Analytics Service

Business logic for analytics and reporting with multi-tenant support.
"""

from uuid import UUID
from typing import Dict, List, Any
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.lead import Lead
from app.models.assessment import Assessment


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
        
        # Status counts
        status_counts = self._count_by_status(leads)
        
        # Score distribution
        score_distribution = self._count_by_score_range(leads)
        
        # Average score
        average_score = sum(lead.score for lead in leads) / len(leads)
        
        # Conversion rate
        converted = status_counts.get("converted", 0)
        conversion_rate = (converted / len(leads)) * 100 if len(leads) > 0 else 0.0
        
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
            "average_score": round(average_score, 2),
            "conversion_rate": round(conversion_rate, 2),
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
        
        # Status counts
        status_counts = {
            "draft": sum(1 for a in assessments if a.status == "draft"),
            "published": sum(1 for a in assessments if a.status == "published"),
            "archived": sum(1 for a in assessments if a.status == "archived"),
        }
        
        # AI generation counts
        ai_counts = {
            "ai": sum(1 for a in assessments if a.ai_generated == "ai"),
            "manual": sum(1 for a in assessments if a.ai_generated == "manual"),
            "hybrid": sum(1 for a in assessments if a.ai_generated == "hybrid"),
        }
        
        return {
            "total": len(assessments),
            "published": status_counts["published"],
            "draft": status_counts["draft"],
            "archived": status_counts["archived"],
            "ai_generated": ai_counts["ai"],
            "manual_created": ai_counts["manual"],
            "hybrid": ai_counts["hybrid"],
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
        days = self._parse_period(period)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
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
        
        # Group by date
        data_points = self._group_by_date(leads, start_date, end_date)
        
        # Calculate summary
        total = len(leads)
        days_count = (end_date - start_date).days + 1
        average_per_day = total / days_count if days_count > 0 else 0
        
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
        
        data_points = self._group_by_date(assessments, start_date, end_date)
        
        total = len(assessments)
        days_count = (end_date - start_date).days + 1
        average_per_day = total / days_count if days_count > 0 else 0
        
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
    
    def _count_by_status(self, leads: List[Lead]) -> Dict[str, int]:
        """Count leads by status"""
        counts = {}
        for lead in leads:
            counts[lead.status] = counts.get(lead.status, 0) + 1
        return counts

    def _count_by_score_range(self, leads: List[Lead]) -> Dict[str, int]:
        """Count leads by score range (hot/warm/cold)"""
        hot = sum(1 for lead in leads if lead.score >= 61)
        warm = sum(1 for lead in leads if 31 <= lead.score <= 60)
        cold = sum(1 for lead in leads if lead.score <= 30)
        
        return {"hot": hot, "warm": warm, "cold": cold}

    def _group_by_date(
        self, items: List, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Group items by date"""
        date_counts = {}
        
        # Count items by date
        for item in items:
            date_key = item.created_at.date().isoformat()
            date_counts[date_key] = date_counts.get(date_key, 0) + 1
        
        # Fill in missing dates with 0
        data_points = []
        current_date = start_date.date()
        end = end_date.date()
        
        while current_date <= end:
            date_key = current_date.isoformat()
            data_points.append({
                "date": date_key,
                "value": date_counts.get(date_key, 0),
            })
            current_date += timedelta(days=1)
        
        return data_points

    def _parse_period(self, period: str) -> int:
        """Parse period string to days"""
        period_map = {
            "7d": 7,
            "30d": 30,
            "90d": 90,
        }
        return period_map.get(period, 30)

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
