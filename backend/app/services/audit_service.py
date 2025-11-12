"""
Audit Service

Handles audit log creation and retrieval.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from app.models.audit_log import AuditLog, AuditAction, AuditLogEntity
from app.models.user import User


class AuditService:
    """Service for managing audit logs"""

    @staticmethod
    def log_change(
        db: Session,
        tenant_id: UUID,
        user_id: UUID,
        entity_type: str,
        entity_id: UUID,
        action: str,
        entity_name: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Create an audit log entry"""
        
        audit_log = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            entity_name=entity_name,
            old_values=old_values,
            new_values=new_values,
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log

    @staticmethod
    def get_audit_logs(
        db: Session,
        tenant_id: UUID,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[AuditLog], int]:
        """Get audit logs with optional filtering"""
        
        query = db.query(AuditLog).filter(AuditLog.tenant_id == tenant_id)
        
        # Apply filters
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        
        if entity_id:
            query = query.filter(AuditLog.entity_id == entity_id)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        # Get total count
        total_count = query.count()
        
        # Order by created_at descending (newest first)
        logs = query.order_by(desc(AuditLog.created_at)).offset(skip).limit(limit).all()
        
        return logs, total_count

    @staticmethod
    def get_user_activity(
        db: Session,
        tenant_id: UUID,
        user_id: UUID,
        days: int = 30,
    ) -> List[AuditLog]:
        """Get recent activity for a specific user"""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        logs = db.query(AuditLog).filter(
            AuditLog.tenant_id == tenant_id,
            AuditLog.user_id == user_id,
            AuditLog.created_at >= start_date,
        ).order_by(desc(AuditLog.created_at)).all()
        
        return logs

    @staticmethod
    def get_entity_history(
        db: Session,
        tenant_id: UUID,
        entity_type: str,
        entity_id: UUID,
    ) -> List[AuditLog]:
        """Get complete change history for a specific entity"""
        
        logs = db.query(AuditLog).filter(
            AuditLog.tenant_id == tenant_id,
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == entity_id,
        ).order_by(desc(AuditLog.created_at)).all()
        
        return logs

    @staticmethod
    def cleanup_old_logs(
        db: Session,
        days: int = 90,
    ) -> int:
        """Delete audit logs older than specified days"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        count = db.query(AuditLog).filter(
            AuditLog.created_at < cutoff_date
        ).delete()
        
        db.commit()
        
        return count
