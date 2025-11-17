"""
Integrations API Endpoints

REST API for external service integrations (Teams, Slack, etc.)
"""

from uuid import UUID
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.tenant import Tenant


router = APIRouter()


# Schemas
class TeamsIntegrationSettings(BaseModel):
    """Teams integration settings"""
    webhook_url: Optional[str] = Field(None, description="Teams Incoming Webhook URL")
    enabled: bool = Field(default=True, description="Enable/disable Teams notifications")
    hot_lead_threshold: int = Field(default=80, ge=0, le=100, description="Score threshold for hot lead notifications")
    notify_channels: Optional[list[str]] = Field(default=None, description="List of channel IDs to notify")

    class Config:
        json_schema_extra = {
            "example": {
                "webhook_url": "https://your-tenant.webhook.office.com/webhookb2/...",
                "enabled": True,
                "hot_lead_threshold": 80,
                "notify_channels": []
            }
        }


class TeamsIntegrationResponse(BaseModel):
    """Teams integration response"""
    enabled: bool
    configured: bool
    hot_lead_threshold: int
    webhook_url_set: bool  # Don't expose actual URL for security


class TeamsTestNotificationRequest(BaseModel):
    """Test notification request"""
    message: str = Field(default="これはDiagnoLeadsからのテスト通知です", description="Test message")


# API Endpoints
@router.get(
    "/tenants/{tenant_id}/integrations/teams",
    response_model=TeamsIntegrationResponse,
    summary="Get Teams integration settings",
    operation_id="getTeamsIntegration",
)
async def get_teams_integration(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current Teams integration settings"""
    # Permission check
    if current_user.tenant_id != tenant_id and current_user.role != "system_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden"
        )

    # Get tenant
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Get Teams settings from tenant.settings JSON field
    teams_settings = tenant.settings.get("teams", {})

    return TeamsIntegrationResponse(
        enabled=teams_settings.get("enabled", False),
        configured=bool(teams_settings.get("webhook_url")),
        hot_lead_threshold=teams_settings.get("hot_lead_threshold", 80),
        webhook_url_set=bool(teams_settings.get("webhook_url"))
    )


@router.put(
    "/tenants/{tenant_id}/integrations/teams",
    response_model=TeamsIntegrationResponse,
    summary="Update Teams integration settings",
    operation_id="updateTeamsIntegration",
)
async def update_teams_integration(
    tenant_id: UUID,
    settings: TeamsIntegrationSettings,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update Teams integration settings"""
    # Permission check - only tenant admin or system admin
    if current_user.tenant_id != tenant_id and current_user.role != "system_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden"
        )

    if current_user.role not in ["tenant_admin", "system_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tenant admins can update integration settings"
        )

    # Get tenant
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Validate webhook URL if provided
    if settings.webhook_url:
        if not settings.webhook_url.startswith("https://"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Webhook URL must start with https://"
            )
        if "webhook.office.com" not in settings.webhook_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Teams webhook URL format"
            )

    # Update tenant settings
    if not tenant.settings:
        tenant.settings = {}

    tenant.settings["teams"] = {
        "webhook_url": settings.webhook_url,
        "enabled": settings.enabled,
        "hot_lead_threshold": settings.hot_lead_threshold,
        "notify_channels": settings.notify_channels or []
    }

    # Also store at root level for backward compatibility
    if settings.webhook_url:
        tenant.settings["teams_webhook_url"] = settings.webhook_url

    db.commit()
    db.refresh(tenant)

    return TeamsIntegrationResponse(
        enabled=settings.enabled,
        configured=bool(settings.webhook_url),
        hot_lead_threshold=settings.hot_lead_threshold,
        webhook_url_set=bool(settings.webhook_url)
    )


@router.post(
    "/tenants/{tenant_id}/integrations/teams/test",
    summary="Send test notification to Teams",
    operation_id="testTeamsNotification",
)
async def test_teams_notification(
    tenant_id: UUID,
    request: TeamsTestNotificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a test notification to verify Teams webhook configuration"""
    # Permission check
    if current_user.tenant_id != tenant_id and current_user.role != "system_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden"
        )

    # Get tenant
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Get webhook URL
    teams_settings = tenant.settings.get("teams", {})
    webhook_url = teams_settings.get("webhook_url") or tenant.settings.get("teams_webhook_url")

    if not webhook_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Teams webhook URL not configured. Please set it up first."
        )

    # Send test message
    try:
        from app.integrations.microsoft.teams_webhook_client import TeamsWebhookClient

        teams_client = TeamsWebhookClient(webhook_url)
        await teams_client.send_simple_message(
            title="DiagnoLeads テスト通知",
            text=request.message
        )

        return {
            "status": "success",
            "message": "Test notification sent successfully",
            "tenant_name": tenant.name
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test notification: {str(e)}"
        )


@router.delete(
    "/tenants/{tenant_id}/integrations/teams",
    summary="Remove Teams integration",
    operation_id="removeTeamsIntegration",
)
async def remove_teams_integration(
    tenant_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove Teams integration (delete webhook URL and disable)"""
    # Permission check - only tenant admin or system admin
    if current_user.tenant_id != tenant_id and current_user.role != "system_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden"
        )

    if current_user.role not in ["tenant_admin", "system_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tenant admins can remove integration settings"
        )

    # Get tenant
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # Remove Teams settings
    if tenant.settings and "teams" in tenant.settings:
        del tenant.settings["teams"]
    if tenant.settings and "teams_webhook_url" in tenant.settings:
        del tenant.settings["teams_webhook_url"]

    db.commit()

    return {
        "status": "success",
        "message": "Teams integration removed successfully"
    }
