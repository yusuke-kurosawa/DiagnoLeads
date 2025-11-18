"""Google Analytics Integration API Endpoints

REST API for managing GA4 integrations with multi-tenant support.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.services.google_analytics_service import GoogleAnalyticsService
from app.schemas.google_analytics import (
    GoogleAnalyticsIntegrationCreate,
    GoogleAnalyticsIntegrationResponse,
    GoogleAnalyticsIntegrationPublic,
    GoogleAnalyticsTestResponse,
)

router = APIRouter()


@router.put(
    "/tenants/{tenant_id}/integrations/google-analytics",
    response_model=GoogleAnalyticsIntegrationResponse,
    status_code=status.HTTP_200_OK,
    summary="Create or update Google Analytics integration",
    operation_id="createOrUpdateGoogleAnalytics",
)
async def create_or_update_ga_integration(
    tenant_id: UUID,
    data: GoogleAnalyticsIntegrationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create or update Google Analytics 4 integration for a tenant

    **Required permissions:** Tenant Admin

    **Request body:**
    - measurement_id: GA4 Measurement ID (G-XXXXXXXXXX format)
    - measurement_protocol_api_secret: Optional API secret for server-side tracking
    - enabled: Enable/disable GA4 tracking
    - track_frontend: Track React admin dashboard events
    - track_embed_widget: Track embedded widget events
    - track_server_events: Track server-side events

    **Returns:** GA4 integration configuration
    """
    # Check tenant access
    if str(current_user.tenant_id) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this tenant's Google Analytics settings is forbidden",
        )

    # Check if user is tenant admin
    if current_user.role not in ["tenant_admin", "system_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tenant admins can configure Google Analytics",
        )

    service = GoogleAnalyticsService(db)

    try:
        integration = await service.create_or_update(tenant_id, data)
        return GoogleAnalyticsIntegrationResponse.model_validate(integration)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/tenants/{tenant_id}/integrations/google-analytics",
    response_model=GoogleAnalyticsIntegrationResponse,
    summary="Get Google Analytics integration",
    operation_id="getGoogleAnalytics",
)
async def get_ga_integration(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get Google Analytics 4 integration settings for a tenant

    **Required permissions:** Authenticated user in the same tenant

    **Returns:** GA4 integration configuration or 404 if not configured
    """
    # Check tenant access
    if str(current_user.tenant_id) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this tenant's Google Analytics settings is forbidden",
        )

    service = GoogleAnalyticsService(db)
    integration = service.get_by_tenant(tenant_id)

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Google Analytics integration not configured for this tenant",
        )

    return GoogleAnalyticsIntegrationResponse.model_validate(integration)


@router.delete(
    "/tenants/{tenant_id}/integrations/google-analytics",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Google Analytics integration",
    operation_id="deleteGoogleAnalytics",
)
async def delete_ga_integration(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete Google Analytics 4 integration for a tenant

    **Required permissions:** Tenant Admin

    **Returns:** 204 No Content on success
    """
    # Check tenant access
    if str(current_user.tenant_id) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this tenant's Google Analytics settings is forbidden",
        )

    # Check if user is tenant admin
    if current_user.role not in ["tenant_admin", "system_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tenant admins can delete Google Analytics integration",
        )

    service = GoogleAnalyticsService(db)
    deleted = await service.delete(tenant_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Google Analytics integration not found",
        )

    return None


@router.post(
    "/tenants/{tenant_id}/integrations/google-analytics/test",
    response_model=GoogleAnalyticsTestResponse,
    summary="Test Google Analytics connection",
    operation_id="testGoogleAnalyticsConnection",
)
async def test_ga_connection(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Test Google Analytics 4 connection by sending a test event

    **Required permissions:** Tenant Admin

    **Returns:** Test result with status and message

    **Note:** After sending test event, check GA4 Realtime Report to verify reception
    """
    # Check tenant access
    if str(current_user.tenant_id) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this tenant's Google Analytics settings is forbidden",
        )

    # Check if user is tenant admin
    if current_user.role not in ["tenant_admin", "system_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tenant admins can test Google Analytics connection",
        )

    service = GoogleAnalyticsService(db)
    result = await service.test_connection(tenant_id)

    return result


@router.get(
    "/public/assessments/{assessment_id}/google-analytics-config",
    response_model=GoogleAnalyticsIntegrationPublic,
    summary="Get public GA4 configuration for embed widget",
    operation_id="getPublicGoogleAnalyticsConfig",
)
async def get_public_ga_config(assessment_id: UUID, db: Session = Depends(get_db)):
    """Get public Google Analytics configuration for embed widget

    **No authentication required** - This is a public endpoint for embed widgets

    **Returns:** Public GA4 configuration (measurement_id, enabled, track_embed_widget)

    **Security:** Does NOT return API secret
    """
    service = GoogleAnalyticsService(db)
    config = service.get_public_config(assessment_id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Google Analytics not configured for this assessment",
        )

    return GoogleAnalyticsIntegrationPublic(**config)
