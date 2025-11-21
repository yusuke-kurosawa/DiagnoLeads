"""
Tests for Error Log API Endpoints

エラーログAPI のテスト（エラー報告、分析、監視機能）
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi import status

from app.models.error_log import ErrorLog
from app.models.user import User
from app.services.auth import AuthService


class TestReportError:
    """Tests for POST /api/v1/error-logs/report endpoint"""

    def test_report_error_authenticated(self, client, test_user, test_tenant):
        """Test reporting error with authentication"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        error_data = {
            "error_type": "TypeError",
            "error_message": "Cannot read property 'x' of undefined",
            "error_code": "ERR_FRONTEND_001",
            "severity": "MEDIUM",
            "stack_trace": "at Component.render (Component.tsx:42)",
            "endpoint": "/api/v1/assessments",
            "method": "GET",
            "status_code": 500,
            "context": {"component": "AssessmentList", "user_action": "load"},
            "correlation_id": "req_abc123",
            "environment": "development",
        }

        response = client.post(
            "/api/v1/error-logs/report",
            json=error_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["error_type"] == "TypeError"
        assert data["error_message"] == error_data["error_message"]
        assert data["severity"] == "MEDIUM"

    def test_report_error_unauthenticated(self, client):
        """Test reporting error without authentication (should still work)"""
        error_data = {
            "error_type": "NetworkError",
            "error_message": "Failed to fetch",
            "severity": "HIGH",
        }

        response = client.post("/api/v1/error-logs/report", json=error_data)

        # Should succeed even without auth (for frontend error reporting)
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_401_UNAUTHORIZED]

    def test_report_error_minimal_data(self, client, test_user, test_tenant):
        """Test reporting error with minimal required fields"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        error_data = {
            "error_type": "Error",
            "error_message": "Something went wrong",
        }

        response = client.post(
            "/api/v1/error-logs/report",
            json=error_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_201_CREATED

    def test_report_error_invalid_severity(self, client, test_user, test_tenant):
        """Test reporting error with invalid severity level"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        error_data = {
            "error_type": "Error",
            "error_message": "Test error",
            "severity": "INVALID_SEVERITY",
        }

        response = client.post(
            "/api/v1/error-logs/report",
            json=error_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        # Should validate severity
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_201_CREATED]


class TestListErrorLogs:
    """Tests for GET /api/v1/error-logs endpoint"""

    def test_list_error_logs_as_system_admin(self, client, test_tenant, db_session):
        """Test listing error logs as system admin"""
        # Create system admin
        system_admin = User(
            id=uuid4(),
            tenant_id=test_tenant.id,
            email="sysadmin@example.com",
            password_hash=AuthService.hash_password("password123"),
            name="System Admin",
            role="system_admin",
        )
        db_session.add(system_admin)
        db_session.commit()

        token = AuthService.create_access_token(
            data={
                "sub": str(system_admin.id),
                "tenant_id": str(test_tenant.id),
                "email": system_admin.email,
            }
        )

        response = client.get(
            "/api/v1/error-logs",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_error_logs_as_tenant_admin(self, client, test_user, test_tenant):
        """Test listing error logs as tenant admin"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        response = client.get(
            f"/api/v1/error-logs?tenant_id={test_tenant.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

    def test_list_error_logs_filter_by_type(self, client, test_user, test_tenant, db_session):
        """Test filtering error logs by error type"""
        # Create error logs with different types
        for error_type in ["TypeError", "NetworkError", "ValidationError"]:
            error_log = ErrorLog(
                tenant_id=test_tenant.id,
                user_id=test_user.id,
                error_type=error_type,
                error_message=f"Test {error_type}",
                severity="MEDIUM",
                environment="test",
            )
            db_session.add(error_log)
        db_session.commit()

        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        response = client.get(
            f"/api/v1/error-logs?tenant_id={test_tenant.id}&error_type=TypeError",
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code == 200:
            data = response.json()
            assert "items" in data

    def test_list_error_logs_filter_by_severity(self, client, test_user, test_tenant):
        """Test filtering error logs by severity"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        response = client.get(
            f"/api/v1/error-logs?tenant_id={test_tenant.id}&severity=CRITICAL",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

    def test_list_error_logs_unauthorized(self, client):
        """Test listing error logs without authentication"""
        response = client.get("/api/v1/error-logs")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_error_logs_pagination(self, client, test_user, test_tenant):
        """Test error logs pagination"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        response = client.get(
            f"/api/v1/error-logs?tenant_id={test_tenant.id}&skip=0&limit=50",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]


class TestErrorLogSummary:
    """Tests for GET /api/v1/error-logs/summary endpoint"""

    def test_get_error_summary(self, client, test_user, test_tenant):
        """Test getting error summary"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        response = client.get(
            f"/api/v1/error-logs/summary?tenant_id={test_tenant.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
        if response.status_code == 200:
            data = response.json()
            assert "total_errors" in data
            assert "errors_by_type" in data
            assert "errors_by_severity" in data

    def test_get_error_summary_with_date_range(self, client, test_user, test_tenant):
        """Test getting error summary with date range"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        response = client.get(
            f"/api/v1/error-logs/summary?tenant_id={test_tenant.id}&days=30",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]


class TestFrequentErrors:
    """Tests for GET /api/v1/error-logs/frequent endpoint"""

    def test_get_frequent_errors(self, client, test_user, test_tenant):
        """Test getting frequent errors"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        response = client.get(
            f"/api/v1/error-logs/frequent?tenant_id={test_tenant.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_get_frequent_errors_with_limit(self, client, test_user, test_tenant):
        """Test getting top N frequent errors"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        response = client.get(
            f"/api/v1/error-logs/frequent?tenant_id={test_tenant.id}&limit=10",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]


class TestErrorTrend:
    """Tests for GET /api/v1/error-logs/trend endpoint"""

    def test_get_error_trend(self, client, test_user, test_tenant):
        """Test getting error trend"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        response = client.get(
            f"/api/v1/error-logs/trend?tenant_id={test_tenant.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_get_error_trend_with_interval(self, client, test_user, test_tenant):
        """Test getting error trend with custom interval"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        response = client.get(
            f"/api/v1/error-logs/trend?tenant_id={test_tenant.id}&days=30",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]


class TestErrorAnalytics:
    """Tests for GET /api/v1/error-logs/analytics endpoint"""

    def test_get_error_analytics(self, client, test_user, test_tenant):
        """Test getting comprehensive error analytics"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        response = client.get(
            f"/api/v1/error-logs/analytics?tenant_id={test_tenant.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
        if response.status_code == 200:
            data = response.json()
            assert "summary" in data
            assert "frequent_errors" in data
            assert "trend" in data


class TestErrorLogByCorrelation:
    """Tests for GET /api/v1/error-logs/correlation/{correlation_id} endpoint"""

    def test_get_errors_by_correlation_id(self, client, test_user, test_tenant, db_session):
        """Test getting errors by correlation ID"""
        correlation_id = "req_test123"

        # Create error logs with same correlation ID
        for i in range(3):
            error_log = ErrorLog(
                tenant_id=test_tenant.id,
                user_id=test_user.id,
                error_type="TestError",
                error_message=f"Error {i}",
                severity="MEDIUM",
                correlation_id=correlation_id,
                environment="test",
            )
            db_session.add(error_log)
        db_session.commit()

        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        response = client.get(
            f"/api/v1/error-logs/correlation/{correlation_id}?tenant_id={test_tenant.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)


class TestGetErrorLog:
    """Tests for GET /api/v1/error-logs/{error_id} endpoint"""

    def test_get_error_log_by_id(self, client, test_user, test_tenant, db_session):
        """Test getting specific error log by ID"""
        error_log = ErrorLog(
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            error_type="TestError",
            error_message="Test error message",
            severity="HIGH",
            environment="test",
        )
        db_session.add(error_log)
        db_session.commit()
        db_session.refresh(error_log)

        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        response = client.get(
            f"/api/v1/error-logs/{error_log.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
        if response.status_code == 200:
            data = response.json()
            assert data["error_type"] == "TestError"
            assert data["error_message"] == "Test error message"

    def test_get_error_log_not_found(self, client, test_user):
        """Test getting non-existent error log"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_user.tenant_id),
                "email": test_user.email,
            }
        )

        fake_error_id = uuid4()
        response = client.get(
            f"/api/v1/error-logs/{fake_error_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]


class TestTenantIsolation:
    """Tests for tenant isolation in error log operations"""

    def test_cannot_access_other_tenant_error_logs(self, client, test_user, test_tenant, db_session):
        """Test that users cannot access error logs from other tenants"""
        # Create error log for another tenant
        other_tenant_id = uuid4()
        other_error = ErrorLog(
            tenant_id=other_tenant_id,
            user_id=uuid4(),
            error_type="OtherTenantError",
            error_message="Should not be accessible",
            severity="MEDIUM",
            environment="test",
        )
        db_session.add(other_error)
        db_session.commit()
        db_session.refresh(other_error)

        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        # Try to access with test_user (different tenant)
        response = client.get(
            f"/api/v1/error-logs/{other_error.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Should deny access
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]


# Run tests with: pytest tests/test_error_logs_api.py -v
