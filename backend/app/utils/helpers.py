"""
Utility Helper Functions

Common helper functions used across services.
"""

from typing import TypeVar, List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Query
from sqlalchemy import and_

from app.core.constants import LeadScoreThreshold, TimeInterval

T = TypeVar('T')


def classify_lead_by_score(score: int) -> str:
    """
    Classify lead as hot/warm/cold based on score.

    Args:
        score: Lead score (0-100)

    Returns:
        Classification: 'hot', 'warm', or 'cold'
    """
    if score >= LeadScoreThreshold.HOT_MIN:
        return "hot"
    elif score >= LeadScoreThreshold.WARM_MIN:
        return "warm"
    else:
        return "cold"


def calculate_average_score(scores: List[int]) -> float:
    """
    Calculate average score from a list of scores.

    Args:
        scores: List of scores

    Returns:
        Average score rounded to 2 decimal places
    """
    if not scores:
        return 0.0
    return round(sum(scores) / len(scores), 2)


def count_by_attribute(items: List[T], attribute: str) -> Dict[str, int]:
    """
    Count items by a specific attribute value.

    Args:
        items: List of items
        attribute: Attribute name to count by

    Returns:
        Dictionary of attribute value to count
    """
    counts: Dict[str, int] = {}
    for item in items:
        value = getattr(item, attribute, "unknown")
        counts[value] = counts.get(value, 0) + 1
    return counts


def apply_date_range_filter(
    query: Query,
    model,
    date_field: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Query:
    """
    Apply date range filter to a SQLAlchemy query.

    Args:
        query: SQLAlchemy query
        model: Model class
        date_field: Name of the date field
        start_date: Start date (ISO format string)
        end_date: End date (ISO format string)

    Returns:
        Filtered query
    """
    field = getattr(model, date_field)

    if start_date:
        start_dt = datetime.fromisoformat(start_date)
        query = query.filter(field >= start_dt)

    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        query = query.filter(field <= end_dt)

    return query


def parse_period_to_days(period: str) -> int:
    """
    Parse period string to number of days.

    Args:
        period: Period string ('7d', '30d', '90d', '365d')

    Returns:
        Number of days
    """
    period_map = {
        "7d": TimeInterval.WEEK,
        "30d": TimeInterval.MONTH,
        "90d": TimeInterval.QUARTER,
        "365d": TimeInterval.YEAR,
    }
    return period_map.get(period, TimeInterval.MONTH)


def get_date_range_from_period(period: str) -> tuple[datetime, datetime]:
    """
    Get start and end dates from a period string.

    Args:
        period: Period string ('7d', '30d', '90d', '365d')

    Returns:
        Tuple of (start_date, end_date)
    """
    days = parse_period_to_days(period)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def group_by_date(
    items: List[T],
    date_field: str,
    start_date: datetime,
    end_date: datetime
) -> List[Dict[str, Any]]:
    """
    Group items by date and fill in missing dates with 0.

    Args:
        items: List of items
        date_field: Name of the date field
        start_date: Start date
        end_date: End date

    Returns:
        List of data points with date and count
    """
    date_counts: Dict[str, int] = {}

    # Count items by date
    for item in items:
        date_value = getattr(item, date_field, None)
        if date_value:
            date_key = date_value.date().isoformat()
            date_counts[date_key] = date_counts.get(date_key, 0) + 1

    # Fill in missing dates with 0
    data_points = []
    current_date = start_date.date()
    end = end_date.date()

    while current_date <= end:
        date_key = current_date.isoformat()
        data_points.append({
            "date": date_key,
            "value": date_counts.get(date_key, 0),
        })
        current_date += timedelta(days=1)

    return data_points


def calculate_conversion_rate(converted: int, total: int) -> float:
    """
    Calculate conversion rate percentage.

    Args:
        converted: Number of converted items
        total: Total number of items

    Returns:
        Conversion rate as percentage (0-100)
    """
    if total == 0:
        return 0.0
    return round((converted / total) * 100, 2)


def paginate_query(
    query: Query,
    page: int = 1,
    page_size: int = 20,
    max_page_size: int = 100
) -> tuple[List[T], int]:
    """
    Paginate a SQLAlchemy query.

    Args:
        query: SQLAlchemy query
        page: Page number (1-indexed)
        page_size: Number of items per page
        max_page_size: Maximum allowed page size

    Returns:
        Tuple of (items, total_count)
    """
    # Validate and limit page size
    page_size = min(page_size, max_page_size)

    # Get total count
    total_count = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    items = query.limit(page_size).offset(offset).all()

    return items, total_count


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is 0.

    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division is not possible

    Returns:
        Result of division or default
    """
    if denominator == 0:
        return default
    return numerator / denominator


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def validate_email(email: str) -> bool:
    """
    Basic email validation.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing/replacing unsafe characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    import re
    # Remove path separators and other unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Limit length
    return filename[:255]
