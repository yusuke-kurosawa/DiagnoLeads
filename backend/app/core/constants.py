"""
Common Constants

Centralized constants used across the application.
"""

from enum import Enum


# Lead scoring thresholds
class LeadScoreThreshold:
    """Lead score thresholds for classification"""

    HOT_MIN = 61  # Hot leads: 61-100
    WARM_MIN = 31  # Warm leads: 31-60
    COLD_MAX = 30  # Cold leads: 0-30

    # Priority thresholds
    CRITICAL_MIN = 90  # Critical priority
    HIGH_MIN = 80  # High priority
    MEDIUM_MIN = 60  # Medium priority
    # Below 60 = Low priority


# Assessment scoring
class AssessmentScore:
    """Assessment score constants"""

    MIN = 0
    LOW = 33
    MEDIUM = 67
    MAX = 100


# Report pagination
class ReportPagination:
    """Default pagination values for reports"""

    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100


# Export formats
class ExportFormat(str, Enum):
    """Supported export formats"""

    CSV = "csv"
    XLSX = "xlsx"
    PDF = "pdf"


# GA4 Event names
class GA4Events:
    """Google Analytics 4 event names"""

    # Widget events
    WIDGET_LOADED = "widget_loaded"
    ASSESSMENT_STARTED = "assessment_started"
    QUESTION_ANSWERED = "question_answered"
    ASSESSMENT_COMPLETED = "assessment_completed"

    # Lead events
    LEAD_GENERATED = "lead_generated"
    HOT_LEAD_GENERATED = "hot_lead_generated"
    LEAD_STATUS_CHANGED = "lead_status_changed"
    LEAD_CONVERTED = "lead_converted"
    LEAD_VIEWED = "lead_viewed"

    # Assessment events (dashboard)
    ASSESSMENT_CREATED = "assessment_created"
    ASSESSMENT_UPDATED = "assessment_updated"
    ASSESSMENT_DELETED = "assessment_deleted"
    ASSESSMENT_PUBLISHED = "assessment_published"


# Time intervals
class TimeInterval:
    """Common time intervals in days"""

    WEEK = 7
    MONTH = 30
    QUARTER = 90
    YEAR = 365


# File size limits
class FileSizeLimit:
    """File size limits in bytes"""

    REPORT_EXPORT_MAX = 50 * 1024 * 1024  # 50MB
    UPLOAD_MAX = 10 * 1024 * 1024  # 10MB


# Cache TTL (Time To Live) in seconds
class CacheTTL:
    """Cache time-to-live values"""

    SHORT = 60  # 1 minute
    MEDIUM = 300  # 5 minutes
    LONG = 3600  # 1 hour
    DAY = 86400  # 24 hours


# API rate limiting
class RateLimit:
    """Rate limit thresholds"""

    REQUESTS_PER_MINUTE = 60
    REQUESTS_PER_HOUR = 1000
    REQUESTS_PER_DAY = 10000


# Status values
class LeadStatus(str, Enum):
    """Lead status enum"""

    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    DISQUALIFIED = "disqualified"


class AssessmentStatus(str, Enum):
    """Assessment status enum"""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ReportType(str, Enum):
    """Report type enum"""

    CUSTOM = "custom"
    LEAD_ANALYSIS = "lead_analysis"
    ASSESSMENT_PERFORMANCE = "assessment_performance"
    CONVERSION_FUNNEL = "conversion_funnel"
    AI_INSIGHTS = "ai_insights"


# AI Configuration
class AIConfig:
    """AI service configuration"""

    MODEL_ASSESSMENT = "claude-3-5-sonnet-20241022"
    MODEL_ANALYSIS = "claude-3-5-sonnet-20241022"

    MAX_TOKENS_ASSESSMENT = 4000
    MAX_TOKENS_ANALYSIS = 1500
    MAX_TOKENS_REPHRASE = 500

    # Temperature settings
    TEMPERATURE_CREATIVE = 0.7
    TEMPERATURE_PRECISE = 0.3
