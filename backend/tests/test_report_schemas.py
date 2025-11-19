"""
Tests for Report Schemas

Comprehensive test coverage for Report Pydantic models and validation.
"""

from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.report import (
    ExportFormat,
    ReportConfig,
    ReportCreate,
    ReportDataPoint,
    ReportExportRequest,
    ReportResponse,
    ReportResultsResponse,
    ReportUpdate,
    ScheduleConfig,
)


class TestReportConfig:
    """Tests for ReportConfig schema"""

    def test_valid_report_config(self):
        """Test creating valid report config"""
        config = ReportConfig(
            metrics=["leads_total", "conversion_rate"],
            filters={"status": ["new", "qualified"]},
            group_by="status",
            visualization="bar_chart",
            sort_by="leads_total",
            sort_order="desc",
        )

        assert config.metrics == ["leads_total", "conversion_rate"]
        assert config.filters["status"] == ["new", "qualified"]
        assert config.group_by == "status"
        assert config.visualization == "bar_chart"

    def test_report_config_minimal(self):
        """Test report config with minimal fields"""
        config = ReportConfig(metrics=["leads_total"])

        assert config.metrics == ["leads_total"]
        assert config.filters is None
        assert config.group_by is None
        assert config.visualization == "table"  # default
        assert config.sort_order == "desc"  # default

    def test_report_config_missing_metrics(self):
        """Test that metrics field is required"""
        with pytest.raises(ValidationError) as exc_info:
            ReportConfig()

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("metrics",) for error in errors)


class TestScheduleConfig:
    """Tests for ScheduleConfig schema"""

    def test_valid_daily_schedule(self):
        """Test creating valid daily schedule"""
        schedule = ScheduleConfig(
            frequency="daily",
            time="09:00",
            timezone="Asia/Tokyo",
            recipients=["admin@example.com"],
        )

        assert schedule.frequency == "daily"
        assert schedule.time == "09:00"
        assert schedule.recipients == ["admin@example.com"]

    def test_valid_weekly_schedule(self):
        """Test creating valid weekly schedule"""
        schedule = ScheduleConfig(
            frequency="weekly",
            day_of_week=1,  # Tuesday
            time="10:30",
            recipients=["user1@example.com", "user2@example.com"],
        )

        assert schedule.frequency == "weekly"
        assert schedule.day_of_week == 1
        assert len(schedule.recipients) == 2

    def test_valid_monthly_schedule(self):
        """Test creating valid monthly schedule"""
        schedule = ScheduleConfig(
            frequency="monthly",
            day_of_month=15,
            time="14:00",
            recipients=["report@example.com"],
        )

        assert schedule.frequency == "monthly"
        assert schedule.day_of_month == 15

    def test_schedule_config_invalid_time_format(self):
        """Test invalid time format"""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleConfig(
                frequency="daily",
                time="9:00",  # Invalid: should be 09:00
                recipients=["admin@example.com"],
            )

        errors = exc_info.value.errors()
        assert any("time" in str(error["loc"]) for error in errors)

    def test_schedule_config_invalid_day_of_week(self):
        """Test invalid day_of_week value"""
        with pytest.raises(ValidationError):
            ScheduleConfig(
                frequency="weekly",
                day_of_week=7,  # Invalid: should be 0-6
                time="09:00",
                recipients=["admin@example.com"],
            )

    def test_schedule_config_invalid_day_of_month(self):
        """Test invalid day_of_month value"""
        with pytest.raises(ValidationError):
            ScheduleConfig(
                frequency="monthly",
                day_of_month=32,  # Invalid: should be 1-31
                time="09:00",
                recipients=["admin@example.com"],
            )


class TestReportCreate:
    """Tests for ReportCreate schema"""

    def test_valid_report_create(self):
        """Test creating valid report creation request"""
        config = ReportConfig(metrics=["leads_total", "conversion_rate"])

        report = ReportCreate(
            name="Monthly Leads Report",
            description="Monthly analysis of leads",
            report_type="lead_analysis",
            config=config,
            is_scheduled=False,
            is_public=True,
        )

        assert report.name == "Monthly Leads Report"
        assert report.report_type == "lead_analysis"
        assert report.is_public is True

    def test_report_create_with_schedule(self):
        """Test report creation with schedule"""
        config = ReportConfig(metrics=["conversion_rate"])
        schedule = ScheduleConfig(
            frequency="weekly",
            day_of_week=0,
            time="08:00",
            recipients=["team@example.com"],
        )

        report = ReportCreate(
            name="Weekly Report",
            config=config,
            is_scheduled=True,
            schedule_config=schedule,
        )

        assert report.is_scheduled is True
        assert report.schedule_config.frequency == "weekly"

    def test_report_create_name_too_short(self):
        """Test report name validation (too short)"""
        config = ReportConfig(metrics=["leads_total"])

        with pytest.raises(ValidationError) as exc_info:
            ReportCreate(name="", config=config)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_report_create_description_too_long(self):
        """Test description max length validation"""
        config = ReportConfig(metrics=["leads_total"])

        with pytest.raises(ValidationError):
            ReportCreate(
                name="Test Report",
                description="x" * 1001,  # Exceeds max_length
                config=config,
            )


class TestReportUpdate:
    """Tests for ReportUpdate schema"""

    def test_valid_report_update(self):
        """Test creating valid report update request"""
        update = ReportUpdate(
            name="Updated Report Name",
            description="Updated description",
            is_public=False,
        )

        assert update.name == "Updated Report Name"
        assert update.is_public is False

    def test_report_update_partial(self):
        """Test partial update (only some fields)"""
        update = ReportUpdate(name="New Name Only")

        assert update.name == "New Name Only"
        assert update.description is None
        assert update.config is None

    def test_report_update_all_none(self):
        """Test update with no fields set"""
        update = ReportUpdate()

        assert update.name is None
        assert update.description is None
        assert update.is_scheduled is None


class TestReportResponse:
    """Tests for ReportResponse schema"""

    def test_valid_report_response(self):
        """Test creating valid report response"""
        tenant_id = uuid4()
        user_id = uuid4()
        report_id = uuid4()

        response = ReportResponse(
            id=report_id,
            tenant_id=tenant_id,
            name="Test Report",
            description="Test Description",
            report_type="custom",
            config={"metrics": ["leads_total"]},
            is_scheduled=False,
            schedule_config=None,
            last_generated_at=None,
            created_by=user_id,
            is_public=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert response.id == report_id
        assert response.tenant_id == tenant_id
        assert response.name == "Test Report"


class TestReportDataPoint:
    """Tests for ReportDataPoint schema"""

    def test_valid_data_point(self):
        """Test creating valid report data point"""
        point = ReportDataPoint(
            label="January 2024",
            values={"leads_total": 150, "conversion_rate": 0.25},
        )

        assert point.label == "January 2024"
        assert point.values["leads_total"] == 150
        assert point.values["conversion_rate"] == 0.25

    def test_data_point_empty_values(self):
        """Test data point with empty values dict"""
        point = ReportDataPoint(label="Test Label", values={})

        assert point.label == "Test Label"
        assert point.values == {}


class TestReportResultsResponse:
    """Tests for ReportResultsResponse schema"""

    def test_valid_report_results(self):
        """Test creating valid report results response"""
        report_id = uuid4()

        results = ReportResultsResponse(
            report_id=report_id,
            report_name="Monthly Report",
            generated_at=datetime.now(),
            config={"metrics": ["leads_total"]},
            data_points=[
                ReportDataPoint(label="Jan", values={"leads_total": 100}),
                ReportDataPoint(label="Feb", values={"leads_total": 120}),
            ],
            summary={"total_leads": 220, "average": 110},
            total_records=2,
        )

        assert results.report_id == report_id
        assert results.report_name == "Monthly Report"
        assert len(results.data_points) == 2
        assert results.total_records == 2
        assert results.summary["total_leads"] == 220


class TestExportFormat:
    """Tests for ExportFormat schema"""

    def test_valid_export_format_pdf(self):
        """Test creating valid PDF export format"""
        export = ExportFormat(
            format="pdf",
            include_charts=True,
            page_size="A4",
            orientation="portrait",
        )

        assert export.format == "pdf"
        assert export.include_charts is True
        assert export.page_size == "A4"

    def test_valid_export_format_xlsx(self):
        """Test creating valid XLSX export format"""
        export = ExportFormat(
            format="xlsx",
            include_charts=False,
            orientation="landscape",
        )

        assert export.format == "xlsx"
        assert export.include_charts is False

    def test_valid_export_format_csv(self):
        """Test creating valid CSV export format"""
        export = ExportFormat(format="csv")

        assert export.format == "csv"
        assert export.include_charts is True  # default

    def test_export_format_invalid_format(self):
        """Test invalid export format"""
        with pytest.raises(ValidationError) as exc_info:
            ExportFormat(format="doc")  # Invalid format

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("format",) for error in errors)


class TestReportExportRequest:
    """Tests for ReportExportRequest schema"""

    def test_valid_export_request(self):
        """Test creating valid export request"""
        report_id = uuid4()
        export_format = ExportFormat(format="pdf")

        request = ReportExportRequest(
            report_id=report_id,
            export_format=export_format,
            filters={"date_range": {"start": "2024-01-01", "end": "2024-12-31"}},
        )

        assert request.report_id == report_id
        assert request.export_format.format == "pdf"
        assert request.filters["date_range"]["start"] == "2024-01-01"

    def test_export_request_without_filters(self):
        """Test export request without custom filters"""
        report_id = uuid4()
        export_format = ExportFormat(format="xlsx")

        request = ReportExportRequest(
            report_id=report_id,
            export_format=export_format,
        )

        assert request.filters is None
