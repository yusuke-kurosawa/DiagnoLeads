"""
Tests for Audit Service

Comprehensive test coverage for audit_service.py
Target: 100% coverage
"""

from datetime import datetime, timedelta
from uuid import uuid4

from app.models.audit_log import AuditLog
from app.services.audit_service import AuditService


class TestAuditServiceLogChange:
    """Tests for log_change method"""

    def test_log_change_basic(self, db_session, test_tenant, test_user):
        """Test basic audit log creation"""
        entity_id = uuid4()

        log = AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=entity_id,
            action="CREATE",
        )

        assert log.id is not None
        assert log.tenant_id == test_tenant.id
        assert log.user_id == test_user.id
        assert log.entity_type == "USER"
        assert log.entity_id == entity_id
        assert log.action == "CREATE"

    def test_log_change_with_full_details(self, db_session, test_tenant, test_user):
        """Test audit log creation with all optional fields"""
        entity_id = uuid4()
        old_values = {"name": "Old Name", "status": "draft"}
        new_values = {"name": "New Name", "status": "published"}

        log = AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="ASSESSMENT",
            entity_id=entity_id,
            action="UPDATE",
            entity_name="Test Assessment",
            old_values=old_values,
            new_values=new_values,
            reason="Updated for review",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )

        assert log.entity_name == "Test Assessment"
        assert log.old_values == old_values
        assert log.new_values == new_values
        assert log.reason == "Updated for review"
        assert log.ip_address == "192.168.1.1"
        assert log.user_agent == "Mozilla/5.0"

    def test_log_change_create_action(self, db_session, test_tenant, test_user):
        """Test logging CREATE action"""
        entity_id = uuid4()
        new_values = {"name": "New User", "email": "user@example.com"}

        log = AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=entity_id,
            action="CREATE",
            new_values=new_values,
        )

        assert log.action == "CREATE"
        assert log.new_values == new_values
        assert log.old_values is None

    def test_log_change_delete_action(self, db_session, test_tenant, test_user):
        """Test logging DELETE action"""
        entity_id = uuid4()
        old_values = {"name": "Deleted User", "email": "deleted@example.com"}

        log = AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=entity_id,
            action="DELETE",
            old_values=old_values,
        )

        assert log.action == "DELETE"
        assert log.old_values == old_values
        assert log.new_values is None


class TestAuditServiceGetAuditLogs:
    """Tests for get_audit_logs method"""

    def test_get_audit_logs_all(self, db_session, test_tenant, test_user):
        """Test getting all audit logs for a tenant"""
        # Create multiple audit logs
        entity_id1 = uuid4()
        entity_id2 = uuid4()

        AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=entity_id1,
            action="CREATE",
        )
        AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="LEAD",
            entity_id=entity_id2,
            action="UPDATE",
        )

        logs, total = AuditService.get_audit_logs(db=db_session, tenant_id=test_tenant.id)

        assert len(logs) == 2
        assert total == 2

    def test_get_audit_logs_filter_by_entity_type(self, db_session, test_tenant, test_user):
        """Test filtering audit logs by entity type"""
        entity_id1 = uuid4()
        entity_id2 = uuid4()

        AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=entity_id1,
            action="CREATE",
        )
        AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="LEAD",
            entity_id=entity_id2,
            action="CREATE",
        )

        logs, total = AuditService.get_audit_logs(db=db_session, tenant_id=test_tenant.id, entity_type="USER")

        assert len(logs) == 1
        assert total == 1
        assert logs[0].entity_type == "USER"

    def test_get_audit_logs_filter_by_entity_id(self, db_session, test_tenant, test_user):
        """Test filtering audit logs by entity ID"""
        entity_id1 = uuid4()
        entity_id2 = uuid4()

        AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=entity_id1,
            action="CREATE",
        )
        AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=entity_id2,
            action="CREATE",
        )

        logs, total = AuditService.get_audit_logs(db=db_session, tenant_id=test_tenant.id, entity_id=entity_id1)

        assert len(logs) == 1
        assert total == 1
        assert logs[0].entity_id == entity_id1

    def test_get_audit_logs_filter_by_action(self, db_session, test_tenant, test_user):
        """Test filtering audit logs by action"""
        entity_id1 = uuid4()
        entity_id2 = uuid4()

        AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=entity_id1,
            action="CREATE",
        )
        AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=entity_id2,
            action="UPDATE",
        )

        logs, total = AuditService.get_audit_logs(db=db_session, tenant_id=test_tenant.id, action="UPDATE")

        assert len(logs) == 1
        assert total == 1
        assert logs[0].action == "UPDATE"

    def test_get_audit_logs_filter_by_date_range(self, db_session, test_tenant, test_user):
        """Test filtering audit logs by date range"""
        entity_id = uuid4()

        # Create log
        AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=entity_id,
            action="CREATE",
        )

        # Filter by date range (yesterday to tomorrow)
        start_date = datetime.utcnow() - timedelta(days=1)
        end_date = datetime.utcnow() + timedelta(days=1)

        logs, total = AuditService.get_audit_logs(
            db=db_session, tenant_id=test_tenant.id, start_date=start_date, end_date=end_date
        )

        assert len(logs) == 1
        assert total == 1

    def test_get_audit_logs_pagination(self, db_session, test_tenant, test_user):
        """Test pagination of audit logs"""
        # Create 5 audit logs
        for i in range(5):
            AuditService.log_change(
                db=db_session,
                tenant_id=test_tenant.id,
                user_id=test_user.id,
                entity_type="USER",
                entity_id=uuid4(),
                action="CREATE",
            )

        # Get first page
        logs, total = AuditService.get_audit_logs(db=db_session, tenant_id=test_tenant.id, skip=0, limit=2)

        assert len(logs) == 2
        assert total == 5

        # Get second page
        logs, total = AuditService.get_audit_logs(db=db_session, tenant_id=test_tenant.id, skip=2, limit=2)

        assert len(logs) == 2
        assert total == 5

    def test_get_audit_logs_tenant_isolation(self, db_session, test_tenant, test_tenant_2, test_user):
        """Test tenant isolation in audit logs"""
        entity_id1 = uuid4()
        entity_id2 = uuid4()

        # Create log for test_tenant
        AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=entity_id1,
            action="CREATE",
        )

        # Create log for test_tenant_2
        AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant_2.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=entity_id2,
            action="CREATE",
        )

        # Get logs for test_tenant only
        logs, total = AuditService.get_audit_logs(db=db_session, tenant_id=test_tenant.id)

        assert len(logs) == 1
        assert total == 1
        assert logs[0].tenant_id == test_tenant.id


class TestAuditServiceGetUserActivity:
    """Tests for get_user_activity method"""

    def test_get_user_activity(self, db_session, test_tenant, test_user):
        """Test getting user activity"""
        entity_id1 = uuid4()
        entity_id2 = uuid4()

        # Create audit logs for user
        AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=entity_id1,
            action="CREATE",
        )
        AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="LEAD",
            entity_id=entity_id2,
            action="UPDATE",
        )

        logs = AuditService.get_user_activity(db=db_session, tenant_id=test_tenant.id, user_id=test_user.id)

        assert len(logs) == 2
        assert all(log.user_id == test_user.id for log in logs)

    def test_get_user_activity_with_days_filter(self, db_session, test_tenant, test_user):
        """Test getting user activity with custom days filter"""
        entity_id = uuid4()

        # Create recent audit log
        AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=entity_id,
            action="CREATE",
        )

        # Get activity from last 7 days
        logs = AuditService.get_user_activity(db=db_session, tenant_id=test_tenant.id, user_id=test_user.id, days=7)

        assert len(logs) == 1


class TestAuditServiceGetEntityHistory:
    """Tests for get_entity_history method"""

    def test_get_entity_history(self, db_session, test_tenant, test_user):
        """Test getting complete history for an entity"""
        entity_id = uuid4()

        # Create multiple changes for same entity
        AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=entity_id,
            action="CREATE",
        )
        AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=entity_id,
            action="UPDATE",
        )
        AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=entity_id,
            action="UPDATE",
        )

        logs = AuditService.get_entity_history(
            db=db_session, tenant_id=test_tenant.id, entity_type="USER", entity_id=entity_id
        )

        assert len(logs) == 3
        assert all(log.entity_id == entity_id for log in logs)
        assert all(log.entity_type == "USER" for log in logs)

    def test_get_entity_history_different_entities(self, db_session, test_tenant, test_user):
        """Test that entity history is specific to one entity"""
        entity_id1 = uuid4()
        entity_id2 = uuid4()

        # Create logs for different entities
        AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=entity_id1,
            action="CREATE",
        )
        AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=entity_id2,
            action="CREATE",
        )

        # Get history for entity1 only
        logs = AuditService.get_entity_history(
            db=db_session, tenant_id=test_tenant.id, entity_type="USER", entity_id=entity_id1
        )

        assert len(logs) == 1
        assert logs[0].entity_id == entity_id1


class TestAuditServiceCleanupOldLogs:
    """Tests for cleanup_old_logs method"""

    def test_cleanup_old_logs(self, db_session, test_tenant, test_user):
        """Test cleaning up old audit logs"""
        entity_id = uuid4()

        # Create an old log
        old_log = AuditLog(
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=entity_id,
            action="CREATE",
        )
        # Manually set created_at to old date
        db_session.add(old_log)
        db_session.flush()

        # Update created_at to be 100 days ago
        db_session.query(AuditLog).filter(AuditLog.id == old_log.id).update(
            {"created_at": datetime.utcnow() - timedelta(days=100)}
        )
        db_session.commit()

        # Create a recent log
        AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=uuid4(),
            action="CREATE",
        )

        # Cleanup logs older than 90 days
        deleted_count = AuditService.cleanup_old_logs(db=db_session, days=90)

        assert deleted_count == 1

        # Verify recent log still exists
        remaining_logs = db_session.query(AuditLog).all()
        assert len(remaining_logs) == 1

    def test_cleanup_old_logs_no_old_logs(self, db_session, test_tenant, test_user):
        """Test cleanup when there are no old logs"""
        entity_id = uuid4()

        # Create recent log
        AuditService.log_change(
            db=db_session,
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            entity_type="USER",
            entity_id=entity_id,
            action="CREATE",
        )

        # Cleanup logs older than 90 days
        deleted_count = AuditService.cleanup_old_logs(db=db_session, days=90)

        assert deleted_count == 0

        # Verify log still exists
        remaining_logs = db_session.query(AuditLog).all()
        assert len(remaining_logs) == 1
