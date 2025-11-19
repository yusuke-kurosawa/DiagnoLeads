"""
Audit Log Schemas

Pydantic models for audit log request/response validation.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    """Audit log response model"""

    id: UUID
    tenant_id: UUID
    user_id: UUID
    entity_type: str
    entity_id: UUID
    action: str
    entity_name: Optional[str]
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]
    reason: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogsListResponse(BaseModel):
    """List of audit logs with pagination"""

    total: int
    skip: int
    limit: int
    items: list[AuditLogResponse]
