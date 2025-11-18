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

__all__ = [
    "get_industry_template",
    "list_available_industries",
    "INDUSTRY_TEMPLATES",
    "get_lead_analysis_template",
    "get_recommended_action",
    "LEAD_ANALYSIS_TEMPLATES",
]
