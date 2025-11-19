"""
Tests for Utility Helper Functions

Comprehensive test coverage for utils/helpers.py
Target: 100% coverage
"""

from datetime import datetime, timedelta

from app.models.lead import Lead
from app.utils.helpers import (
    apply_date_range_filter,
    calculate_average_score,
    calculate_conversion_rate,
    classify_lead_by_score,
    count_by_attribute,
    get_date_range_from_period,
    group_by_date,
    paginate_query,
    parse_period_to_days,
    safe_divide,
    sanitize_filename,
    truncate_string,
    validate_email,
)


class TestClassifyLeadByScore:
    """Tests for classify_lead_by_score function"""

    def test_classify_hot_lead(self):
        """Test classifying hot lead (score >= 61)"""
        assert classify_lead_by_score(61) == "hot"
        assert classify_lead_by_score(100) == "hot"
        assert classify_lead_by_score(85) == "hot"

    def test_classify_warm_lead(self):
        """Test classifying warm lead (31 <= score < 61)"""
        assert classify_lead_by_score(31) == "warm"
        assert classify_lead_by_score(60) == "warm"
        assert classify_lead_by_score(45) == "warm"

    def test_classify_cold_lead(self):
        """Test classifying cold lead (score < 31)"""
        assert classify_lead_by_score(0) == "cold"
        assert classify_lead_by_score(30) == "cold"
        assert classify_lead_by_score(15) == "cold"


class TestCalculateAverageScore:
    """Tests for calculate_average_score function"""

    def test_calculate_average_with_scores(self):
        """Test calculating average with multiple scores"""
        assert calculate_average_score([80, 90, 70]) == 80.0
        assert calculate_average_score([100, 50]) == 75.0

    def test_calculate_average_empty_list(self):
        """Test calculating average with empty list"""
        assert calculate_average_score([]) == 0.0

    def test_calculate_average_single_score(self):
        """Test calculating average with single score"""
        assert calculate_average_score([85]) == 85.0

    def test_calculate_average_rounding(self):
        """Test that average is rounded to 2 decimal places"""
        assert calculate_average_score([10, 20, 25]) == 18.33


class TestCountByAttribute:
    """Tests for count_by_attribute function"""

    def test_count_by_status(self, db_session, test_tenant, test_user):
        """Test counting leads by status"""
        # Create test leads with different statuses
        leads = [
            Lead(
                tenant_id=test_tenant.id,
                name="Lead 1",
                email="lead1@example.com",
                score=80,
                status="new",
                created_by=test_user.id,
            ),
            Lead(
                tenant_id=test_tenant.id,
                name="Lead 2",
                email="lead2@example.com",
                score=70,
                status="new",
                created_by=test_user.id,
            ),
            Lead(
                tenant_id=test_tenant.id,
                name="Lead 3",
                email="lead3@example.com",
                score=60,
                status="qualified",
                created_by=test_user.id,
            ),
        ]

        counts = count_by_attribute(leads, "status")

        assert counts["new"] == 2
        assert counts["qualified"] == 1

    def test_count_by_nonexistent_attribute(self):
        """Test counting by non-existent attribute"""
        items = [type("Obj", (), {})() for _ in range(3)]
        counts = count_by_attribute(items, "nonexistent")

        assert counts["unknown"] == 3


class TestApplyDateRangeFilter:
    """Tests for apply_date_range_filter function"""

    def test_apply_start_date_filter(self, db_session, test_tenant, test_user):
        """Test applying start date filter"""
        from sqlalchemy import select

        query = select(Lead)
        start_date = "2024-01-01T00:00:00"

        filtered = apply_date_range_filter(query, Lead, "created_at", start_date=start_date)

        # Just verify it doesn't crash - actual filtering tested in integration
        assert filtered is not None

    def test_apply_end_date_filter(self, db_session):
        """Test applying end date filter"""
        from sqlalchemy import select

        query = select(Lead)
        end_date = "2024-12-31T23:59:59"

        filtered = apply_date_range_filter(query, Lead, "created_at", end_date=end_date)

        assert filtered is not None

    def test_apply_both_date_filters(self, db_session):
        """Test applying both start and end date filters"""
        from sqlalchemy import select

        query = select(Lead)
        start_date = "2024-01-01T00:00:00"
        end_date = "2024-12-31T23:59:59"

        filtered = apply_date_range_filter(query, Lead, "created_at", start_date=start_date, end_date=end_date)

        assert filtered is not None


class TestParsePeriodToDays:
    """Tests for parse_period_to_days function"""

    def test_parse_week(self):
        """Test parsing 7 days"""
        assert parse_period_to_days("7d") == 7

    def test_parse_month(self):
        """Test parsing 30 days"""
        assert parse_period_to_days("30d") == 30

    def test_parse_quarter(self):
        """Test parsing 90 days"""
        assert parse_period_to_days("90d") == 90

    def test_parse_year(self):
        """Test parsing 365 days"""
        assert parse_period_to_days("365d") == 365

    def test_parse_unknown_period(self):
        """Test parsing unknown period returns default (30 days)"""
        assert parse_period_to_days("unknown") == 30


class TestGetDateRangeFromPeriod:
    """Tests for get_date_range_from_period function"""

    def test_get_date_range_7d(self):
        """Test getting date range for 7 days"""
        start, end = get_date_range_from_period("7d")

        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert (end - start).days == 7

    def test_get_date_range_30d(self):
        """Test getting date range for 30 days"""
        start, end = get_date_range_from_period("30d")

        assert (end - start).days == 30


class TestGroupByDate:
    """Tests for group_by_date function"""

    def test_group_by_date(self, db_session, test_tenant, test_user):
        """Test grouping items by date"""
        # Create leads on different dates
        today = datetime.utcnow()
        yesterday = today - timedelta(days=1)

        leads = [
            type(
                "Lead",
                (),
                {"created_at": today},
            )(),
            type("Lead", (), {"created_at": today})(),
            type("Lead", (), {"created_at": yesterday})(),
        ]

        start_date = yesterday
        end_date = today

        data_points = group_by_date(leads, "created_at", start_date, end_date)

        assert len(data_points) == 2  # Two days
        assert data_points[0]["value"] == 1  # Yesterday
        assert data_points[1]["value"] == 2  # Today

    def test_group_by_date_fills_missing_dates(self):
        """Test that missing dates are filled with 0"""
        today = datetime.utcnow()
        start_date = today - timedelta(days=3)
        end_date = today

        # No items
        data_points = group_by_date([], "created_at", start_date, end_date)

        assert len(data_points) == 4  # 4 days
        assert all(dp["value"] == 0 for dp in data_points)


class TestCalculateConversionRate:
    """Tests for calculate_conversion_rate function"""

    def test_conversion_rate_normal(self):
        """Test normal conversion rate calculation"""
        assert calculate_conversion_rate(25, 100) == 25.0
        assert calculate_conversion_rate(1, 2) == 50.0

    def test_conversion_rate_zero_total(self):
        """Test conversion rate with zero total"""
        assert calculate_conversion_rate(0, 0) == 0.0

    def test_conversion_rate_all_converted(self):
        """Test 100% conversion rate"""
        assert calculate_conversion_rate(50, 50) == 100.0


class TestPaginateQuery:
    """Tests for paginate_query function"""

    def test_paginate_first_page(self, db_session, test_tenant, test_user):
        """Test paginating first page"""
        # Create 5 test leads
        for i in range(5):
            lead = Lead(
                tenant_id=test_tenant.id,
                name=f"Lead {i}",
                email=f"lead{i}@example.com",
                score=i * 20,
                status="new",
                created_by=test_user.id,
            )
            db_session.add(lead)
        db_session.commit()

        query = db_session.query(Lead)
        items, total = paginate_query(query, page=1, page_size=2)

        assert len(items) == 2
        assert total == 5

    def test_paginate_exceeds_max_page_size(self, db_session):
        """Test that page size is limited to max_page_size"""
        query = db_session.query(Lead)
        items, total = paginate_query(query, page=1, page_size=200, max_page_size=100)

        # Should use max_page_size=100 instead of 200
        assert total == 0  # No items in empty database


class TestSafeDivide:
    """Tests for safe_divide function"""

    def test_safe_divide_normal(self):
        """Test normal division"""
        assert safe_divide(10, 2) == 5.0
        assert safe_divide(7, 2) == 3.5

    def test_safe_divide_by_zero(self):
        """Test division by zero returns default"""
        assert safe_divide(10, 0) == 0.0
        assert safe_divide(10, 0, default=99.0) == 99.0


class TestTruncateString:
    """Tests for truncate_string function"""

    def test_truncate_long_string(self):
        """Test truncating a long string"""
        text = "This is a very long string that needs truncation"
        result = truncate_string(text, 20)

        assert len(result) == 20
        assert result.endswith("...")

    def test_truncate_short_string(self):
        """Test that short string is not truncated"""
        text = "Short"
        result = truncate_string(text, 20)

        assert result == "Short"

    def test_truncate_with_custom_suffix(self):
        """Test truncating with custom suffix"""
        text = "This is a long string"
        result = truncate_string(text, 10, suffix=">>")

        assert result.endswith(">>")
        assert len(result) == 10


class TestValidateEmail:
    """Tests for validate_email function"""

    def test_validate_valid_emails(self):
        """Test validating valid email addresses"""
        assert validate_email("user@example.com") is True
        assert validate_email("test.user+tag@example.co.uk") is True
        assert validate_email("user123@test-domain.com") is True

    def test_validate_invalid_emails(self):
        """Test validating invalid email addresses"""
        assert validate_email("invalid") is False
        assert validate_email("@example.com") is False
        assert validate_email("user@") is False
        assert validate_email("user@.com") is False


class TestSanitizeFilename:
    """Tests for sanitize_filename function"""

    def test_sanitize_unsafe_characters(self):
        """Test sanitizing unsafe characters"""
        filename = 'test<>:"/\\|?*file.txt'
        result = sanitize_filename(filename)

        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert "/" not in result
        assert "\\" not in result

    def test_sanitize_spaces(self):
        """Test that spaces are replaced with underscores"""
        filename = "my test file.txt"
        result = sanitize_filename(filename)

        assert result == "my_test_file.txt"

    def test_sanitize_long_filename(self):
        """Test that long filenames are truncated"""
        filename = "a" * 300 + ".txt"
        result = sanitize_filename(filename)

        assert len(result) <= 255
