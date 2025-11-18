"""
AI Services Package

Contains AI-powered services including assessment generation and analysis.
"""

from .industry_templates import (
    get_industry_template,
    list_available_industries,
    INDUSTRY_TEMPLATES,
)
from .lead_analysis_templates import (
    get_lead_analysis_template,
    get_recommended_action,
    LEAD_ANALYSIS_TEMPLATES,
)
from .exceptions import (
    AIServiceError,
    AIAPIError,
    AIRateLimitError,
    AIValidationError,
    AIJSONParseError,
    AIPromptInjectionError,
)
from .json_extractor import JSONExtractor
from .prompt_sanitizer import PromptSanitizer
from .prompt_templates import PromptTemplates
from .retry_helper import retry_with_backoff

__all__ = [
    # Templates
    "get_industry_template",
    "list_available_industries",
    "INDUSTRY_TEMPLATES",
    "get_lead_analysis_template",
    "get_recommended_action",
    "LEAD_ANALYSIS_TEMPLATES",
    # Exceptions
    "AIServiceError",
    "AIAPIError",
    "AIRateLimitError",
    "AIValidationError",
    "AIJSONParseError",
    "AIPromptInjectionError",
    # Utilities
    "JSONExtractor",
    "PromptSanitizer",
    "PromptTemplates",
    "retry_with_backoff",
]
