"""
AI Services Package

Contains AI-powered services including assessment generation and analysis.
"""

from .industry_templates import (
    get_industry_template,
    list_available_industries,
    INDUSTRY_TEMPLATES,
)

__all__ = [
    "get_industry_template",
    "list_available_industries",
    "INDUSTRY_TEMPLATES",
]
