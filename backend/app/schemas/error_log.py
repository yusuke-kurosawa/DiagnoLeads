"""
Error Log Schemas

Pydantic models for error log request/response validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ErrorLogCreate(BaseModel):
    """Error log creation model (for frontend error reporting)"""

    error_type: str
    error_message: str
    error_code: Optional[str] = None
    severity: str = "MEDIUM"
    stack_trace: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    context: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None
    environment: str = "development"


class ErrorLogResponse(BaseModel):
    """Error log response model"""

    id: UUID
    tenant_id: Optional[UUID]
    user_id: Optional[UUID]
    error_type: str
    error_code: Optional[str]
    severity: str
    error_message: str
    stack_trace: Optional[str]
    endpoint: Optional[str]
    method: Optional[str]
    status_code: Optional[int]
    request_body: Optional[Dict[str, Any]]
    request_headers: Optional[Dict[str, Any]]
    response_body: Optional[Dict[str, Any]]
    duration_ms: Optional[int]
    environment: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    context: Optional[Dict[str, Any]]
    correlation_id: Optional[str]
    workflow_name: Optional[str]
    job_name: Optional[str]
    run_id: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ErrorLogListResponse(BaseModel):
    """List of error logs with pagination"""

    total: int
    skip: int
    limit: int
    items: List[ErrorLogResponse]


class ErrorSummaryResponse(BaseModel):
    """Error summary statistics"""

    total_errors: int
    errors_by_type: Dict[str, int]
    errors_by_severity: Dict[str, int]
    critical_errors: int
    start_date: Optional[str]
    end_date: Optional[str]


class FrequentErrorResponse(BaseModel):
    """Frequent error response model"""

    error_type: str
    error_message: str
    endpoint: Optional[str]
    count: int
    last_occurrence: Optional[str]


class ErrorTrendResponse(BaseModel):
    """Error trend response model"""

    timestamp: Optional[str]
    count: int


class ErrorAnalyticsResponse(BaseModel):
    """Comprehensive error analytics"""

    summary: ErrorSummaryResponse
    frequent_errors: List[FrequentErrorResponse]
    trend: List[ErrorTrendResponse]
