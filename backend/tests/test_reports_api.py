"""
Tests for Reports API Endpoints

Test coverage for custom report management and execution.
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi import status
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


class TestReportNotFound:
    """Tests for 404 not found scenarios"""

    def test_get_nonexistent_report(self, client: TestClient, test_user: User):
        """Test getting non-existent report returns 404"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        response = client.get(
            f"/api/v1/tenants/{test_user.tenant_id}/reports/{uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_nonexistent_report(self, client: TestClient, test_user: User):
        """Test updating non-existent report returns 404"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        response = client.put(
            f"/api/v1/tenants/{test_user.tenant_id}/reports/{uuid4()}",
            json={"name": "Updated"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_report(self, client: TestClient, test_user: User):
        """Test deleting non-existent report returns 404"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        response = client.delete(
            f"/api/v1/tenants/{test_user.tenant_id}/reports/{uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_execute_nonexistent_report(self, client: TestClient, test_user: User):
        """Test executing non-existent report returns 404"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        response = client.post(
            f"/api/v1/tenants/{test_user.tenant_id}/reports/{uuid4()}/execute",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_export_nonexistent_report(self, client: TestClient, test_user: User):
        """Test exporting non-existent report returns 404"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        response = client.post(
            f"/api/v1/tenants/{test_user.tenant_id}/reports/{uuid4()}/export?format=csv",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestReportUnauthorized:
    """Tests for unauthorized access (401)"""

    def test_create_report_unauthorized(self, client: TestClient, test_tenant):
        """Test creating report without authentication"""
        response = client.post(
            f"/api/v1/tenants/{test_tenant.id}/reports",
            json={"name": "Test", "report_type": "leads", "config": {}},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_reports_unauthorized(self, client: TestClient, test_tenant):
        """Test listing reports without authentication"""
        response = client.get(f"/api/v1/tenants/{test_tenant.id}/reports")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_report_unauthorized(self, client: TestClient, test_tenant):
        """Test getting report without authentication"""
        response = client.get(f"/api/v1/tenants/{test_tenant.id}/reports/{uuid4()}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_report_unauthorized(self, client: TestClient, test_tenant):
        """Test updating report without authentication"""
        response = client.put(
            f"/api/v1/tenants/{test_tenant.id}/reports/{uuid4()}",
            json={"name": "Updated"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_report_unauthorized(self, client: TestClient, test_tenant):
        """Test deleting report without authentication"""
        response = client.delete(f"/api/v1/tenants/{test_tenant.id}/reports/{uuid4()}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_execute_report_unauthorized(self, client: TestClient, test_tenant):
        """Test executing report without authentication"""
        response = client.post(f"/api/v1/tenants/{test_tenant.id}/reports/{uuid4()}/execute")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_export_report_unauthorized(self, client: TestClient, test_tenant):
        """Test exporting report without authentication"""
        response = client.post(f"/api/v1/tenants/{test_tenant.id}/reports/{uuid4()}/export")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestReportExport:
    """Tests for report export functionality"""

    @patch("app.api.v1.reports.ReportService")
    @patch("app.api.v1.reports.ReportExportService")
    def test_export_report_csv(self, mock_export_service_class, mock_service_class, client: TestClient, db_session: Session, test_user: User):
        """Test exporting report as CSV"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create report
        report = Report(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="Export Test",
            description="Test",
            report_type="leads",
            config={"metrics": ["total"]},
            is_public=True,
        )
        db_session.add(report)
        db_session.commit()
        db_session.refresh(report)

        # Mock services
        mock_service = MagicMock()
        mock_service.get_by_id.return_value = report
        mock_service.execute_report.return_value = {
            "data_points": [{"label": "2024-01", "values": {"total": 100}}],
            "summary": {"total": 100},
            "total_records": 1,
        }
        mock_service_class.return_value = mock_service

        mock_export_service = MagicMock()
        mock_export_service.export_to_csv.return_value = b"label,total\n2024-01,100\n"
        mock_export_service_class.return_value = mock_export_service

        response = client.post(
            f"/api/v1/tenants/{test_user.tenant_id}/reports/{report.id}/export?format=csv",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "Export_Test.csv" in response.headers["content-disposition"]

    @patch("app.api.v1.reports.ReportService")
    @patch("app.api.v1.reports.ReportExportService")
    def test_export_report_xlsx(self, mock_export_service_class, mock_service_class, client: TestClient, db_session: Session, test_user: User):
        """Test exporting report as Excel"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create report
        report = Report(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="Excel Export",
            description="Test",
            report_type="leads",
            config={"metrics": ["total"]},
            is_public=True,
        )
        db_session.add(report)
        db_session.commit()
        db_session.refresh(report)

        # Mock services
        mock_service = MagicMock()
        mock_service.get_by_id.return_value = report
        mock_service.execute_report.return_value = {
            "data_points": [{"label": "2024-01", "values": {"total": 100}}],
            "summary": {"total": 100},
            "total_records": 1,
        }
        mock_service_class.return_value = mock_service

        mock_export_service = MagicMock()
        mock_export_service.export_to_excel.return_value = b"Excel binary data"
        mock_export_service_class.return_value = mock_export_service

        response = client.post(
            f"/api/v1/tenants/{test_user.tenant_id}/reports/{report.id}/export?format=xlsx",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers["content-type"]
        assert "Excel_Export.xlsx" in response.headers["content-disposition"]

    @patch("app.api.v1.reports.ReportService")
    @patch("app.api.v1.reports.ReportExportService")
    def test_export_report_pdf(self, mock_export_service_class, mock_service_class, client: TestClient, db_session: Session, test_user: User):
        """Test exporting report as PDF"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create report
        report = Report(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="PDF Export",
            description="Test",
            report_type="leads",
            config={"metrics": ["total"]},
            is_public=True,
        )
        db_session.add(report)
        db_session.commit()
        db_session.refresh(report)

        # Mock services
        mock_service = MagicMock()
        mock_service.get_by_id.return_value = report
        mock_service.execute_report.return_value = {
            "data_points": [{"label": "2024-01", "values": {"total": 100}}],
            "summary": {"total": 100},
            "total_records": 1,
        }
        mock_service_class.return_value = mock_service

        mock_export_service = MagicMock()
        mock_export_service.export_to_pdf.return_value = b"PDF binary data"
        mock_export_service_class.return_value = mock_export_service

        response = client.post(
            f"/api/v1/tenants/{test_user.tenant_id}/reports/{report.id}/export?format=pdf",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/pdf"
        assert "PDF_Export.pdf" in response.headers["content-disposition"]

    def test_export_report_invalid_format(self, client: TestClient, db_session: Session, test_user: User):
        """Test exporting with invalid format returns 422"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create report
        report = Report(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="Test",
            description="Test",
            report_type="leads",
            config={"metrics": ["total"]},
            is_public=True,
        )
        db_session.add(report)
        db_session.commit()
        db_session.refresh(report)

        response = client.post(
            f"/api/v1/tenants/{test_user.tenant_id}/reports/{report.id}/export?format=invalid",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Query param validation should fail with 422
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestReportExecutionErrors:
    """Tests for report execution error handling"""

    @patch("app.api.v1.reports.ReportService")
    def test_execute_report_value_error(self, mock_service_class, client: TestClient, db_session: Session, test_user: User):
        """Test report execution with ValueError returns 400"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create report
        report = Report(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="Error Test",
            description="Test",
            report_type="leads",
            config={"metrics": ["invalid_metric"]},
            is_public=True,
        )
        db_session.add(report)
        db_session.commit()
        db_session.refresh(report)

        # Mock service to raise ValueError
        mock_service = MagicMock()
        mock_service.get_by_id.return_value = report
        mock_service.execute_report.side_effect = ValueError("Invalid metric configuration")
        mock_service_class.return_value = mock_service

        response = client.post(
            f"/api/v1/tenants/{test_user.tenant_id}/reports/{report.id}/execute",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid metric" in response.json()["detail"]

    @patch("app.api.v1.reports.ReportService")
    def test_execute_report_general_error(self, mock_service_class, client: TestClient, db_session: Session, test_user: User):
        """Test report execution with general exception returns 500"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create report
        report = Report(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="Error Test",
            description="Test",
            report_type="leads",
            config={"metrics": ["total"]},
            is_public=True,
        )
        db_session.add(report)
        db_session.commit()
        db_session.refresh(report)

        # Mock service to raise general exception
        mock_service = MagicMock()
        mock_service.get_by_id.return_value = report
        mock_service.execute_report.side_effect = Exception("Database connection failed")
        mock_service_class.return_value = mock_service

        response = client.post(
            f"/api/v1/tenants/{test_user.tenant_id}/reports/{report.id}/execute",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "execution failed" in response.json()["detail"].lower()


class TestReportTenantIsolation:
    """Tests for tenant isolation in report operations"""

    def test_cannot_access_other_tenant_report(self, client: TestClient, db_session: Session, test_user: User, test_tenant_2):
        """Test that users cannot access reports from other tenants"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create report in different tenant
        other_report = Report(
            tenant_id=test_tenant_2.id,
            created_by=uuid4(),
            name="Other Tenant Report",
            description="Test",
            report_type="leads",
            config={"metrics": ["total"]},
            is_public=True,
        )
        db_session.add(other_report)
        db_session.commit()
        db_session.refresh(other_report)

        # Try to access with test_user (different tenant)
        response = client.get(
            f"/api/v1/tenants/{test_tenant_2.id}/reports/{other_report.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Should return 403 Forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_reports_filters_by_tenant(self, client: TestClient, db_session: Session, test_user: User, test_tenant_2):
        """Test that listing reports only returns tenant's reports"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create reports in both tenants
        own_report = Report(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="Own Report",
            description="Test",
            report_type="leads",
            config={"metrics": ["total"]},
            is_public=True,
        )
        other_report = Report(
            tenant_id=test_tenant_2.id,
            created_by=uuid4(),
            name="Other Tenant Report",
            description="Test",
            report_type="leads",
            config={"metrics": ["total"]},
            is_public=True,
        )
        db_session.add_all([own_report, other_report])
        db_session.commit()

        # List reports for own tenant
        response = client.get(
            f"/api/v1/tenants/{test_user.tenant_id}/reports",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should only contain own tenant's reports
        report_names = [r["name"] for r in data]
        assert "Own Report" in report_names
        assert "Other Tenant Report" not in report_names


class TestReportPrivacy:
    """Tests for report privacy settings"""

    def test_list_reports_excludes_other_users_private_reports(self, client: TestClient, db_session: Session, test_user: User):
        """Test that listing reports excludes private reports from other users"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create another user in same tenant
        other_user_id = uuid4()

        # Create private report by other user
        other_private = Report(
            tenant_id=test_user.tenant_id,
            created_by=other_user_id,
            name="Other User Private",
            description="Private",
            report_type="leads",
            config={"metrics": ["total"]},
            is_public=False,
        )
        # Create public report by other user
        other_public = Report(
            tenant_id=test_user.tenant_id,
            created_by=other_user_id,
            name="Other User Public",
            description="Public",
            report_type="leads",
            config={"metrics": ["total"]},
            is_public=True,
        )
        db_session.add_all([other_private, other_public])
        db_session.commit()

        # List reports without include_private
        response = client.get(
            f"/api/v1/tenants/{test_user.tenant_id}/reports",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        report_names = [r["name"] for r in data]
        # Should see public report but not private
        assert "Other User Public" in report_names
        assert "Other User Private" not in report_names


# Run tests with: pytest tests/test_reports_api.py -v
