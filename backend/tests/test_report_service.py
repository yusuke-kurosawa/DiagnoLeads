"""
Tests for Report Service

Comprehensive test coverage for report_service.py
Target: 100% coverage
"""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from app.models.assessment import Assessment
from app.models.lead import Lead
from app.models.report import Report
from app.schemas.report import ReportConfig, ReportCreate, ReportUpdate, ScheduleConfig
from app.services.report_service import ReportService


class TestReportServiceCreate:
    """Tests for report creation"""

    def test_create_basic_report(self, db_session, test_tenant, test_user):
        """Test creating a basic report"""
        service = ReportService(db_session)

        config = ReportConfig(
            metrics=["leads_total", "average_score"],
            filters={"status": ["new", "qualified"]},
            visualization="bar_chart",
        )

        data = ReportCreate(
            name="Test Report",
            description="A test report",
            report_type="lead_analysis",
            config=config,
            is_public=True,
        )

        report = service.create(data, test_tenant.id, test_user.id)

        assert report.id is not None
        assert report.name == "Test Report"
        assert report.description == "A test report"
        assert report.report_type == "lead_analysis"
        assert report.tenant_id == test_tenant.id
        assert report.created_by == test_user.id
        assert report.is_public is True
        assert "metrics" in report.config
        assert report.config["metrics"] == ["leads_total", "average_score"]

    def test_create_scheduled_report(self, db_session, test_tenant, test_user):
        """Test creating a scheduled report"""
        service = ReportService(db_session)

        config = ReportConfig(
            metrics=["conversion_rate"],
            visualization="line_chart",
        )

        schedule = ScheduleConfig(
            frequency="weekly",
            day_of_week=1,
            time="09:00",
            timezone="Asia/Tokyo",
            recipients=["user@example.com"],
        )

        data = ReportCreate(
            name="Weekly Report",
            report_type="custom",
            config=config,
            is_scheduled=True,
            schedule_config=schedule,
        )

        report = service.create(data, test_tenant.id, test_user.id)

        assert report.is_scheduled is True
        assert report.schedule_config is not None
        assert report.schedule_config["frequency"] == "weekly"
        assert report.schedule_config["day_of_week"] == 1


class TestReportServiceGet:
    """Tests for report retrieval"""

    def test_get_by_id_success(self, db_session, test_tenant, test_user):
        """Test getting report by ID"""
        service = ReportService(db_session)

        # Create report
        report = Report(
            tenant_id=test_tenant.id,
            name="Test Report",
            report_type="custom",
            config={"metrics": ["leads_total"]},
            created_by=test_user.id,
        )
        db_session.add(report)
        db_session.commit()

        # Retrieve report
        retrieved = service.get_by_id(report.id, test_tenant.id)

        assert retrieved is not None
        assert retrieved.id == report.id
        assert retrieved.name == "Test Report"

    def test_get_by_id_wrong_tenant(self, db_session, test_tenant, test_tenant_2, test_user):
        """Test tenant isolation in get_by_id"""
        service = ReportService(db_session)

        # Create report for test_tenant
        report = Report(
            tenant_id=test_tenant.id,
            name="Tenant 1 Report",
            report_type="custom",
            config={"metrics": ["leads_total"]},
            created_by=test_user.id,
        )
        db_session.add(report)
        db_session.commit()

        # Try to retrieve with wrong tenant_id
        retrieved = service.get_by_id(report.id, test_tenant_2.id)

        assert retrieved is None

    def test_list_reports_public_only(self, db_session, test_tenant, test_user):
        """Test listing public reports only"""
        service = ReportService(db_session)

        # Create public and private reports
        public_report = Report(
            tenant_id=test_tenant.id,
            name="Public Report",
            report_type="custom",
            config={"metrics": ["leads_total"]},
            created_by=test_user.id,
            is_public=True,
        )
        private_report = Report(
            tenant_id=test_tenant.id,
            name="Private Report",
            report_type="custom",
            config={"metrics": ["leads_total"]},
            created_by=test_user.id,
            is_public=False,
        )
        db_session.add_all([public_report, private_report])
        db_session.commit()

        # List without include_private
        reports = service.list_reports(test_tenant.id, test_user.id, include_private=False)

        assert len(reports) == 1
        assert reports[0].name == "Public Report"

    def test_list_reports_include_private(self, db_session, test_tenant, test_user):
        """Test listing reports including user's private reports"""
        service = ReportService(db_session)

        # Create public and private reports
        public_report = Report(
            tenant_id=test_tenant.id,
            name="Public Report",
            report_type="custom",
            config={"metrics": ["leads_total"]},
            created_by=test_user.id,
            is_public=True,
        )
        private_report = Report(
            tenant_id=test_tenant.id,
            name="Private Report",
            report_type="custom",
            config={"metrics": ["leads_total"]},
            created_by=test_user.id,
            is_public=False,
        )
        db_session.add_all([public_report, private_report])
        db_session.commit()

        # List with include_private
        reports = service.list_reports(test_tenant.id, test_user.id, include_private=True)

        assert len(reports) == 2


class TestReportServiceUpdate:
    """Tests for report updates"""

    def test_update_report_success(self, db_session, test_tenant, test_user):
        """Test successful report update"""
        service = ReportService(db_session)

        # Create report
        report = Report(
            tenant_id=test_tenant.id,
            name="Original Name",
            report_type="custom",
            config={"metrics": ["leads_total"]},
            created_by=test_user.id,
        )
        db_session.add(report)
        db_session.commit()

        # Update report
        update_data = ReportUpdate(
            name="Updated Name",
            description="Updated description",
        )
        updated = service.update(report.id, update_data, test_tenant.id)

        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.description == "Updated description"

    def test_update_report_config(self, db_session, test_tenant, test_user):
        """Test updating report config"""
        service = ReportService(db_session)

        # Create report
        report = Report(
            tenant_id=test_tenant.id,
            name="Test Report",
            report_type="custom",
            config={"metrics": ["leads_total"]},
            created_by=test_user.id,
        )
        db_session.add(report)
        db_session.commit()

        # Update config
        new_config = ReportConfig(
            metrics=["leads_total", "conversion_rate"],
            filters={"status": ["qualified"]},
            visualization="pie_chart",
        )
        update_data = ReportUpdate(config=new_config)
        updated = service.update(report.id, update_data, test_tenant.id)

        assert updated.config["metrics"] == ["leads_total", "conversion_rate"]
        assert updated.config["filters"]["status"] == ["qualified"]

    def test_update_nonexistent_report(self, db_session, test_tenant):
        """Test updating non-existent report"""
        service = ReportService(db_session)

        update_data = ReportUpdate(name="New Name")
        updated = service.update(uuid4(), update_data, test_tenant.id)

        assert updated is None


class TestReportServiceDelete:
    """Tests for report deletion"""

    def test_delete_report_success(self, db_session, test_tenant, test_user):
        """Test successful report deletion"""
        service = ReportService(db_session)

        # Create report
        report = Report(
            tenant_id=test_tenant.id,
            name="To Delete",
            report_type="custom",
            config={"metrics": ["leads_total"]},
            created_by=test_user.id,
        )
        db_session.add(report)
        db_session.commit()
        report_id = report.id

        # Delete
        result = service.delete(report_id, test_tenant.id)

        assert result is True

        # Verify deletion
        deleted = service.get_by_id(report_id, test_tenant.id)
        assert deleted is None

    def test_delete_nonexistent_report(self, db_session, test_tenant):
        """Test deleting non-existent report"""
        service = ReportService(db_session)

        result = service.delete(uuid4(), test_tenant.id)

        assert result is False


class TestReportServiceExecuteLeadAnalysis:
    """Tests for lead analysis report execution"""

    def test_execute_lead_analysis_basic(self, db_session, test_tenant, test_user):
        """Test basic lead analysis report execution"""
        service = ReportService(db_session)

        # Create leads
        lead1 = Lead(
            tenant_id=test_tenant.id,
            name="Lead 1",
            email="lead1@example.com",
            score=80,
            status="new",
            created_by=test_user.id,
        )
        lead2 = Lead(
            tenant_id=test_tenant.id,
            name="Lead 2",
            email="lead2@example.com",
            score=60,
            status="qualified",
            created_by=test_user.id,
        )
        db_session.add_all([lead1, lead2])
        db_session.commit()

        # Create report
        report = Report(
            tenant_id=test_tenant.id,
            name="Lead Analysis",
            report_type="lead_analysis",
            config={
                "metrics": ["leads_total", "average_score"],
                "filters": {},
            },
            created_by=test_user.id,
        )
        db_session.add(report)
        db_session.commit()

        # Execute report
        results = service.execute_report(report.id, test_tenant.id)

        assert results is not None
        assert "data_points" in results
        assert "summary" in results
        assert results["total_records"] == 2

    def test_execute_lead_analysis_with_filters(self, db_session, test_tenant, test_user):
        """Test lead analysis with filters"""
        service = ReportService(db_session)

        # Create leads with different statuses
        lead1 = Lead(
            tenant_id=test_tenant.id,
            name="New Lead",
            email="new@example.com",
            score=80,
            status="new",
            created_by=test_user.id,
        )
        lead2 = Lead(
            tenant_id=test_tenant.id,
            name="Qualified Lead",
            email="qualified@example.com",
            score=90,
            status="qualified",
            created_by=test_user.id,
        )
        db_session.add_all([lead1, lead2])
        db_session.commit()

        # Create report with status filter
        report = Report(
            tenant_id=test_tenant.id,
            name="Qualified Leads Report",
            report_type="lead_analysis",
            config={
                "metrics": ["leads_total"],
                "filters": {"status": ["qualified"]},
            },
            created_by=test_user.id,
        )
        db_session.add(report)
        db_session.commit()

        # Execute report
        results = service.execute_report(report.id, test_tenant.id)

        # Should only include qualified lead
        assert results["total_records"] == 1

    def test_execute_lead_analysis_with_score_filter(self, db_session, test_tenant, test_user):
        """Test lead analysis with score range filter"""
        service = ReportService(db_session)

        # Create leads with different scores
        lead1 = Lead(
            tenant_id=test_tenant.id,
            name="High Score",
            email="high@example.com",
            score=85,
            status="new",
            created_by=test_user.id,
        )
        lead2 = Lead(
            tenant_id=test_tenant.id,
            name="Low Score",
            email="low@example.com",
            score=40,
            status="new",
            created_by=test_user.id,
        )
        db_session.add_all([lead1, lead2])
        db_session.commit()

        # Create report with score filter
        report = Report(
            tenant_id=test_tenant.id,
            name="High Score Leads",
            report_type="lead_analysis",
            config={
                "metrics": ["leads_total"],
                "filters": {"score_range": {"min": 70}},
            },
            created_by=test_user.id,
        )
        db_session.add(report)
        db_session.commit()

        # Execute report
        results = service.execute_report(report.id, test_tenant.id)

        # Should only include high score lead
        assert results["total_records"] == 1

    def test_execute_lead_analysis_grouped(self, db_session, test_tenant, test_user):
        """Test lead analysis with grouping"""
        service = ReportService(db_session)

        # Create leads with different statuses
        lead1 = Lead(
            tenant_id=test_tenant.id,
            name="New Lead 1",
            email="new1@example.com",
            score=80,
            status="new",
            created_by=test_user.id,
        )
        lead2 = Lead(
            tenant_id=test_tenant.id,
            name="New Lead 2",
            email="new2@example.com",
            score=75,
            status="new",
            created_by=test_user.id,
        )
        lead3 = Lead(
            tenant_id=test_tenant.id,
            name="Qualified Lead",
            email="qualified@example.com",
            score=90,
            status="qualified",
            created_by=test_user.id,
        )
        db_session.add_all([lead1, lead2, lead3])
        db_session.commit()

        # Create report with grouping by status
        report = Report(
            tenant_id=test_tenant.id,
            name="Leads by Status",
            report_type="lead_analysis",
            config={
                "metrics": ["leads_total", "average_score"],
                "filters": {},
                "group_by": "status",
            },
            created_by=test_user.id,
        )
        db_session.add(report)
        db_session.commit()

        # Execute report
        results = service.execute_report(report.id, test_tenant.id)

        # Should have multiple data points (one per status)
        assert len(results["data_points"]) == 2  # new and qualified
        labels = [dp["label"] for dp in results["data_points"]]
        assert "new" in labels
        assert "qualified" in labels


class TestReportServiceExecuteAssessmentPerformance:
    """Tests for assessment performance report execution"""

    def test_execute_assessment_performance(self, db_session, test_tenant, test_user):
        """Test assessment performance report execution"""
        service = ReportService(db_session)

        # Create assessments
        assessment1 = Assessment(
            tenant_id=test_tenant.id,
            title="Assessment 1",
            description="Test",
            status="published",
            ai_generated="ai",
            created_by=test_user.id,
        )
        assessment2 = Assessment(
            tenant_id=test_tenant.id,
            title="Assessment 2",
            description="Test",
            status="draft",
            ai_generated="manual",
            created_by=test_user.id,
        )
        db_session.add_all([assessment1, assessment2])
        db_session.commit()

        # Create report
        report = Report(
            tenant_id=test_tenant.id,
            name="Assessment Performance",
            report_type="assessment_performance",
            config={
                "metrics": ["assessments_total", "published_count"],
                "filters": {},
            },
            created_by=test_user.id,
        )
        db_session.add(report)
        db_session.commit()

        # Execute report
        results = service.execute_report(report.id, test_tenant.id)

        assert results is not None
        assert results["total_records"] == 2


class TestReportServiceExecuteCustom:
    """Tests for custom report execution"""

    def test_execute_custom_report(self, db_session, test_tenant, test_user):
        """Test custom report execution combining multiple data sources"""
        service = ReportService(db_session)

        # Create lead
        lead = Lead(
            tenant_id=test_tenant.id,
            name="Test Lead",
            email="lead@example.com",
            score=80,
            status="new",
            created_by=test_user.id,
        )
        # Create assessment
        assessment = Assessment(
            tenant_id=test_tenant.id,
            title="Test Assessment",
            description="Test",
            status="published",
            created_by=test_user.id,
        )
        db_session.add_all([lead, assessment])
        db_session.commit()

        # Create custom report
        report = Report(
            tenant_id=test_tenant.id,
            name="Custom Report",
            report_type="custom",
            config={
                "metrics": ["lead_total", "assessment_total"],
                "filters": {},
            },
            created_by=test_user.id,
        )
        db_session.add(report)
        db_session.commit()

        # Execute report
        results = service.execute_report(report.id, test_tenant.id)

        assert results is not None
        assert "data_points" in results


class TestReportServiceReportNotFound:
    """Tests for error handling"""

    def test_execute_nonexistent_report(self, db_session, test_tenant):
        """Test executing non-existent report raises error"""
        service = ReportService(db_session)

        with pytest.raises(ValueError, match="Report not found"):
            service.execute_report(uuid4(), test_tenant.id)
