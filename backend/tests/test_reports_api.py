"""
Tests for Reports API Endpoints

Test coverage for custom report management and execution.
"""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.report import Report
from app.models.user import User
from app.services.auth import AuthService


class TestReportsAPI:
    """Tests for Reports API endpoints"""

    def test_create_report(self, client: TestClient, db_session: Session, test_user: User):
        """Test creating a new report"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        report_data = {
            "name": "Monthly Leads Report",
            "description": "Monthly lead statistics",
            "report_type": "leads",
            "config": {
                "metrics": ["total", "hot_leads", "conversion_rate"],
                "filters": {"status": "new"},
                "visualization": "bar",
            },
            "is_public": True,
        }

        response = client.post(
            f"/api/v1/tenants/{test_user.tenant_id}/reports",
            json=report_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Monthly Leads Report"
        assert data["report_type"] == "leads"

    def test_create_report_forbidden_other_tenant(self, client: TestClient, test_user: User, test_tenant_2):
        """Test that users cannot create reports for other tenants"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        report_data = {
            "name": "Unauthorized Report",
            "description": "Should fail",
            "report_type": "leads",
            "config": {
                "metrics": ["total"],
            },
        }

        response = client.post(
            f"/api/v1/tenants/{test_tenant_2.id}/reports",
            json=report_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    def test_list_reports(self, client: TestClient, db_session: Session, test_user: User):
        """Test listing reports"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create test reports
        report1 = Report(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="Public Report",
            description="Public",
            report_type="leads",
            config={"metrics": ["total"]},
            is_public=True,
        )
        report2 = Report(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="Private Report",
            description="Private",
            report_type="assessments",
            config={"metrics": ["total"]},
            is_public=False,
        )
        db_session.add_all([report1, report2])
        db_session.commit()

        # Get public reports only
        response = client.get(
            f"/api/v1/tenants/{test_user.tenant_id}/reports",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        # Should get at least the public report
        assert len(data) >= 1

    def test_list_reports_include_private(self, client: TestClient, db_session: Session, test_user: User):
        """Test listing reports including private ones"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create private report
        report = Report(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="My Private Report",
            description="Private",
            report_type="leads",
            config={"metrics": ["total"]},
            is_public=False,
        )
        db_session.add(report)
        db_session.commit()

        response = client.get(
            f"/api/v1/tenants/{test_user.tenant_id}/reports?include_private=true",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    def test_get_report_by_id(self, client: TestClient, db_session: Session, test_user: User):
        """Test getting a specific report"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create report
        report = Report(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="Test Report",
            description="Test",
            report_type="leads",
            config={"metrics": ["total"]},
            is_public=True,
        )
        db_session.add(report)
        db_session.commit()
        db_session.refresh(report)

        response = client.get(
            f"/api/v1/tenants/{test_user.tenant_id}/reports/{report.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Report"

    def test_update_report(self, client: TestClient, db_session: Session, test_user: User):
        """Test updating a report"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create report
        report = Report(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="Original Name",
            description="Original",
            report_type="leads",
            config={"metrics": ["total"]},
            is_public=True,
        )
        db_session.add(report)
        db_session.commit()
        db_session.refresh(report)

        update_data = {"name": "Updated Name", "description": "Updated description"}

        response = client.put(
            f"/api/v1/tenants/{test_user.tenant_id}/reports/{report.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_delete_report(self, client: TestClient, db_session: Session, test_user: User):
        """Test deleting a report"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create report
        report = Report(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="To Delete",
            description="Will be deleted",
            report_type="leads",
            config={"metrics": ["total"]},
            is_public=True,
        )
        db_session.add(report)
        db_session.commit()
        db_session.refresh(report)

        response = client.delete(
            f"/api/v1/tenants/{test_user.tenant_id}/reports/{report.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 204

        # Verify deleted
        deleted = db_session.query(Report).filter(Report.id == report.id).first()
        assert deleted is None

    @patch("app.api.v1.reports.ReportService")
    def test_execute_report(self, mock_service_class, client: TestClient, db_session: Session, test_user: User):
        """Test executing a report"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create report
        report = Report(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="Execution Report",
            description="Test",
            report_type="leads",
            config={"metrics": ["total", "hot_leads"]},
            is_public=True,
        )
        db_session.add(report)
        db_session.commit()
        db_session.refresh(report)

        # Mock service
        mock_service = MagicMock()
        mock_service.get_by_id.return_value = report
        mock_service.execute_report.return_value = {
            "data_points": [{"label": "2024-01-01", "values": {"total": 100, "hot_leads": 25}}],
            "summary": {"total": 100, "hot_leads": 25},
            "total_records": 1,
        }
        mock_service_class.return_value = mock_service

        response = client.post(
            f"/api/v1/tenants/{test_user.tenant_id}/reports/{report.id}/execute",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "data_points" in data or "summary" in data
