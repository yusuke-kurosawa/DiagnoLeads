"""
Audit Log API Endpoints

Provides access to audit logs for compliance and audit trail tracking.
Only accessible to system admins and tenant admins (within their tenant).
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.services.audit_service import AuditService
from app.schemas.audit_log import AuditLogResponse, AuditLogsListResponse


router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


def check_admin_access(current_user: User):
    """Verify that user is admin"""
    if current_user.role not in ["system_admin", "tenant_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access audit logs",
        )
    return current_user


@router.get("", response_model=AuditLogsListResponse)
async def list_audit_logs(
    tenant_id: UUID,
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[UUID] = Query(None),
    action: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List audit logs (admin only)"""
    check_admin_access(current_user)
    
    # Tenant admin can only view their own tenant's logs
    if current_user.role == "tenant_admin" and tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only view audit logs for your own tenant",
        )
    
    logs, total = AuditService.get_audit_logs(
        db,
        tenant_id=tenant_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        skip=skip,
        limit=limit,
    )
    
    return AuditLogsListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[AuditLogResponse.from_orm(log) for log in logs],
    )


@router.get("/entity/{entity_type}/{entity_id}", response_model=list[AuditLogResponse])
async def get_entity_history(
    tenant_id: UUID,
    entity_type: str,
    entity_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get change history for a specific entity"""
    check_admin_access(current_user)
    
    # Tenant admin can only view their own tenant's logs
    if current_user.role == "tenant_admin" and tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only view audit logs for your own tenant",
        )
    
    logs = AuditService.get_entity_history(
        db,
        tenant_id=tenant_id,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    
    return [AuditLogResponse.from_orm(log) for log in logs]


@router.get("/user/{user_id}", response_model=list[AuditLogResponse])
async def get_user_activity(
    tenant_id: UUID,
    user_id: UUID,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get recent activity for a specific user"""
    check_admin_access(current_user)
    
    # Tenant admin can only view their own tenant's logs
    if current_user.role == "tenant_admin" and tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only view audit logs for your own tenant",
        )
    
    logs = AuditService.get_user_activity(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        days=days,
    )
    
    return [AuditLogResponse.from_orm(log) for log in logs]
