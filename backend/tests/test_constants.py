"""
Tests for Core Constants

Verify that all constants are correctly defined and accessible.
"""

from app.core.constants import (
    AIConfig,
    AssessmentScore,
    AssessmentStatus,
    CacheTTL,
    ExportFormat,
    FileSizeLimit,
    GA4Events,
    LeadScoreThreshold,
    LeadStatus,
    RateLimit,
    ReportPagination,
    ReportType,
    TimeInterval,
)


class TestLeadScoreThreshold:
    """Tests for lead score thresholds"""

    def test_hot_threshold(self):
        """Test hot lead threshold"""
        assert LeadScoreThreshold.HOT_MIN == 61
        assert LeadScoreThreshold.HOT_MIN > LeadScoreThreshold.WARM_MIN

    def test_warm_threshold(self):
        """Test warm lead threshold"""
        assert LeadScoreThreshold.WARM_MIN == 31
        assert LeadScoreThreshold.WARM_MIN > LeadScoreThreshold.COLD_MAX

    def test_cold_threshold(self):
        """Test cold lead threshold"""
        assert LeadScoreThreshold.COLD_MAX == 30

    def test_priority_thresholds(self):
        """Test priority thresholds"""
        assert LeadScoreThreshold.CRITICAL == 90
        assert LeadScoreThreshold.HIGH == 80
        assert LeadScoreThreshold.MEDIUM == 60
        assert LeadScoreThreshold.CRITICAL > LeadScoreThreshold.HIGH
        assert LeadScoreThreshold.HIGH > LeadScoreThreshold.MEDIUM


class TestAssessmentScore:
    """Tests for assessment score constants"""

    def test_score_range(self):
        """Test assessment score range"""
        assert AssessmentScore.MIN == 0
        assert AssessmentScore.MAX == 100
        assert AssessmentScore.MIN < AssessmentScore.LOW
        assert AssessmentScore.LOW < AssessmentScore.MEDIUM
        assert AssessmentScore.MEDIUM < AssessmentScore.MAX

    def test_score_levels(self):
        """Test score level values"""
        assert AssessmentScore.LOW == 33
        assert AssessmentScore.MEDIUM == 67


class TestReportPagination:
    """Tests for report pagination constants"""

    def test_page_sizes(self):
        """Test pagination sizes"""
        assert ReportPagination.DEFAULT_PAGE_SIZE == 20
        assert ReportPagination.MAX_PAGE_SIZE == 100
        assert ReportPagination.DEFAULT_PAGE_SIZE < ReportPagination.MAX_PAGE_SIZE


class TestExportFormat:
    """Tests for export format enum"""

    def test_export_formats(self):
        """Test all export formats are defined"""
        assert ExportFormat.CSV == "csv"
        assert ExportFormat.XLSX == "xlsx"
        assert ExportFormat.PDF == "pdf"

    def test_enum_values(self):
        """Test enum values are strings"""
        assert isinstance(ExportFormat.CSV.value, str)
        assert isinstance(ExportFormat.XLSX.value, str)
        assert isinstance(ExportFormat.PDF.value, str)


class TestGA4Events:
    """Tests for GA4 event constants"""

    def test_widget_events(self):
        """Test widget event names"""
        assert GA4Events.WIDGET_LOADED == "widget_loaded"
        assert GA4Events.ASSESSMENT_STARTED == "assessment_started"
        assert GA4Events.QUESTION_ANSWERED == "question_answered"
        assert GA4Events.ASSESSMENT_COMPLETED == "assessment_completed"

    def test_lead_events(self):
        """Test lead event names"""
        assert GA4Events.LEAD_GENERATED == "lead_generated"
        assert GA4Events.HOT_LEAD_GENERATED == "hot_lead_generated"
        assert GA4Events.LEAD_STATUS_CHANGED == "lead_status_changed"
        assert GA4Events.LEAD_CONVERTED == "lead_converted"

    def test_assessment_events(self):
        """Test assessment event names"""
        assert GA4Events.ASSESSMENT_CREATED == "assessment_created"
        assert GA4Events.ASSESSMENT_UPDATED == "assessment_updated"
        assert GA4Events.ASSESSMENT_PUBLISHED == "assessment_published"


class TestTimeInterval:
    """Tests for time interval constants"""

    def test_intervals_in_days(self):
        """Test time intervals are correctly defined"""
        assert TimeInterval.WEEK == 7
        assert TimeInterval.MONTH == 30
        assert TimeInterval.QUARTER == 90
        assert TimeInterval.YEAR == 365

    def test_interval_ordering(self):
        """Test intervals are in increasing order"""
        assert TimeInterval.WEEK < TimeInterval.MONTH
        assert TimeInterval.MONTH < TimeInterval.QUARTER
        assert TimeInterval.QUARTER < TimeInterval.YEAR


class TestFileSizeLimit:
    """Tests for file size limit constants"""

    def test_size_limits(self):
        """Test file size limits in bytes"""
        assert FileSizeLimit.REPORT_EXPORT_MAX == 50 * 1024 * 1024  # 50MB
        assert FileSizeLimit.UPLOAD_MAX == 10 * 1024 * 1024  # 10MB

    def test_relative_sizes(self):
        """Test relative sizes"""
        assert FileSizeLimit.REPORT_EXPORT_MAX > FileSizeLimit.UPLOAD_MAX


class TestCacheTTL:
    """Tests for cache TTL constants"""

    def test_ttl_values(self):
        """Test cache TTL values in seconds"""
        assert CacheTTL.SHORT == 60  # 1 minute
        assert CacheTTL.MEDIUM == 300  # 5 minutes
        assert CacheTTL.LONG == 3600  # 1 hour
        assert CacheTTL.DAY == 86400  # 24 hours

    def test_ttl_ordering(self):
        """Test TTL values are in increasing order"""
        assert CacheTTL.SHORT < CacheTTL.MEDIUM
        assert CacheTTL.MEDIUM < CacheTTL.LONG
        assert CacheTTL.LONG < CacheTTL.DAY


class TestRateLimit:
    """Tests for rate limit constants"""

    def test_rate_limits(self):
        """Test rate limit thresholds"""
        assert RateLimit.REQUESTS_PER_MINUTE == 60
        assert RateLimit.REQUESTS_PER_HOUR == 1000
        assert RateLimit.REQUESTS_PER_DAY == 10000

    def test_rate_limit_progression(self):
        """Test rate limits increase appropriately"""
        assert RateLimit.REQUESTS_PER_MINUTE < RateLimit.REQUESTS_PER_HOUR
        assert RateLimit.REQUESTS_PER_HOUR < RateLimit.REQUESTS_PER_DAY


class TestLeadStatus:
    """Tests for lead status enum"""

    def test_lead_statuses(self):
        """Test all lead statuses are defined"""
        assert LeadStatus.NEW == "new"
        assert LeadStatus.CONTACTED == "contacted"
        assert LeadStatus.QUALIFIED == "qualified"
        assert LeadStatus.CONVERTED == "converted"
        assert LeadStatus.DISQUALIFIED == "disqualified"

    def test_enum_type(self):
        """Test lead status enum type"""
        assert isinstance(LeadStatus.NEW, str)


class TestAssessmentStatus:
    """Tests for assessment status enum"""

    def test_assessment_statuses(self):
        """Test all assessment statuses are defined"""
        assert AssessmentStatus.DRAFT == "draft"
        assert AssessmentStatus.PUBLISHED == "published"
        assert AssessmentStatus.ARCHIVED == "archived"


class TestReportType:
    """Tests for report type enum"""

    def test_report_types(self):
        """Test all report types are defined"""
        assert ReportType.CUSTOM == "custom"
        assert ReportType.LEAD_ANALYSIS == "lead_analysis"
        assert ReportType.ASSESSMENT_PERFORMANCE == "assessment_performance"
        assert ReportType.CONVERSION_FUNNEL == "conversion_funnel"
        assert ReportType.AI_INSIGHTS == "ai_insights"


class TestAIConfig:
    """Tests for AI configuration constants"""

    def test_model_names(self):
        """Test AI model names"""
        assert "claude" in AIConfig.MODEL_ASSESSMENT.lower()
        assert "claude" in AIConfig.MODEL_ANALYSIS.lower()

    def test_token_limits(self):
        """Test max token limits"""
        assert AIConfig.MAX_TOKENS_ASSESSMENT == 4000
        assert AIConfig.MAX_TOKENS_ANALYSIS == 1500
        assert AIConfig.MAX_TOKENS_REPHRASE == 500

    def test_token_ordering(self):
        """Test token limits are in appropriate order"""
        assert AIConfig.MAX_TOKENS_REPHRASE < AIConfig.MAX_TOKENS_ANALYSIS
        assert AIConfig.MAX_TOKENS_ANALYSIS < AIConfig.MAX_TOKENS_ASSESSMENT

    def test_temperature_settings(self):
        """Test temperature settings"""
        assert AIConfig.TEMPERATURE_CREATIVE == 0.7
        assert AIConfig.TEMPERATURE_PRECISE == 0.3
        assert 0 <= AIConfig.TEMPERATURE_PRECISE <= 1
        assert 0 <= AIConfig.TEMPERATURE_CREATIVE <= 1
