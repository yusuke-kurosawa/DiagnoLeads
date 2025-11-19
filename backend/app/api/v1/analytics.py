"""
Analytics API Endpoints

REST API for analytics and reporting with multi-tenant support.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get(
    "/tenants/{tenant_id}/analytics/overview",
    summary="Get overview analytics",
    operation_id="getOverviewAnalytics",
)
async def get_overview_analytics(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get overview analytics for dashboard

    Returns:
        - Lead statistics (total, status distribution, score distribution)
        - Assessment statistics (total, status distribution, AI generation)
        - Conversion metrics
    """
    # Check tenant access
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this tenant's analytics is forbidden",
        )

    service = AnalyticsService(db)
    analytics = service.get_overview(tenant_id)

    return analytics


@router.get(
    "/tenants/{tenant_id}/analytics/leads",
    summary="Get lead analytics",
    operation_id="getLeadAnalytics",
)
async def get_lead_analytics(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed lead analytics

    Returns:
        - Total leads
        - Status distribution (new, contacted, qualified, converted, disqualified)
        - Score distribution (hot, warm, cold)
        - Average score
        - Conversion rate
    """
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this tenant's analytics is forbidden",
        )

    service = AnalyticsService(db)
    analytics = service.get_lead_analytics(tenant_id)

    return analytics


@router.get(
    "/tenants/{tenant_id}/analytics/assessments",
    summary="Get assessment analytics",
    operation_id="getAssessmentAnalytics",
)
async def get_assessment_analytics(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed assessment analytics

    Returns:
        - Total assessments
        - Status distribution (draft, published, archived)
        - AI generation vs manual creation
    """
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this tenant's analytics is forbidden",
        )

    service = AnalyticsService(db)
    analytics = service.get_assessment_analytics(tenant_id)

    return analytics


@router.get(
    "/tenants/{tenant_id}/analytics/trends",
    summary="Get trend data",
    operation_id="getTrendData",
)
async def get_trends(
    tenant_id: UUID,
    period: str = Query("30d", pattern="^(7d|30d|90d)$"),
    metric: str = Query("leads", pattern="^(leads|assessments)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get trend data for a specific metric

    Args:
        period: Time period (7d, 30d, 90d)
        metric: Metric type (leads, assessments)

    Returns:
        - Data points with date and value
        - Summary statistics
    """
    if current_user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this tenant's analytics is forbidden",
        )

    service = AnalyticsService(db)
    trends = service.get_trends(tenant_id, period, metric)

    return trends
