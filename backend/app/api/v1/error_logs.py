"""
Error Log API Endpoints

Provides access to error logs for debugging and monitoring.
Accessible to system admins and tenant admins (within their tenant).
Also provides an endpoint for frontend error reporting.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.error_log import (
    ErrorAnalyticsResponse,
    ErrorLogCreate,
    ErrorLogListResponse,
    ErrorLogResponse,
    ErrorSummaryResponse,
    ErrorTrendResponse,
    FrequentErrorResponse,
)
from app.services.error_log_service import ErrorLogService

router = APIRouter(prefix="/error-logs", tags=["Error Logs"])


def check_error_log_access(current_user: User, requested_tenant_id: Optional[UUID] = None):
    """Verify that user can access error logs"""
    # System admin can view all error logs
    if current_user.role == "system_admin":
        return current_user

    # Tenant admin or user can only view their own tenant's logs
    if requested_tenant_id and current_user.tenant_id == requested_tenant_id:
        return current_user

    # If no tenant_id is requested, check if user is system admin
    if not requested_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system admins can view all error logs",
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Can only view error logs for your own tenant",
    )


@router.post("/report", response_model=ErrorLogResponse, status_code=status.HTTP_201_CREATED)
async def report_error(
    error: ErrorLogCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """
    Report an error from frontend or external systems.
    Can be called with or without authentication.
    """
    # Extract request context
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # Get tenant and user ID if authenticated
    tenant_id = current_user.tenant_id if current_user else None
    user_id = current_user.id if current_user else None

    # Log the error
    error_log = ErrorLogService.log_error(
        db=db,
        tenant_id=tenant_id,
        user_id=user_id,
        error_type=error.error_type,
        error_message=error.error_message,
        error_code=error.error_code,
        severity=error.severity,
        stack_trace=error.stack_trace,
        endpoint=error.endpoint,
        method=error.method,
        status_code=error.status_code,
        context=error.context,
        correlation_id=error.correlation_id,
        environment=settings.ENVIRONMENT,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    if not error_log:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log error",
        )

    return ErrorLogResponse.model_validate(error_log)


@router.get("", response_model=ErrorLogListResponse)
async def list_error_logs(
    tenant_id: Optional[UUID] = Query(None),
    error_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    endpoint: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=365),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List error logs with filtering"""
    check_error_log_access(current_user, tenant_id)

    # If user is not system admin, force their tenant_id
    if current_user.role != "system_admin":
        tenant_id = current_user.tenant_id

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    logs, total = ErrorLogService.get_error_logs(
        db=db,
        tenant_id=tenant_id,
        error_type=error_type,
        severity=severity,
        environment=environment,
        endpoint=endpoint,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )

    return ErrorLogListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[ErrorLogResponse.model_validate(log) for log in logs],
    )


@router.get("/summary", response_model=ErrorSummaryResponse)
async def get_error_summary(
    tenant_id: Optional[UUID] = Query(None),
    days: int = Query(7, ge=1, le=365),
    environment: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get error summary statistics"""
    check_error_log_access(current_user, tenant_id)

    # If user is not system admin, force their tenant_id
    if current_user.role != "system_admin":
        tenant_id = current_user.tenant_id

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    summary = ErrorLogService.get_error_summary(
        db=db,
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date,
        environment=environment,
    )

    return ErrorSummaryResponse(**summary)


@router.get("/frequent", response_model=List[FrequentErrorResponse])
async def get_frequent_errors(
    tenant_id: Optional[UUID] = Query(None),
    days: int = Query(7, ge=1, le=365),
    environment: Optional[str] = Query(None),
    top_n: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get most frequent errors"""
    check_error_log_access(current_user, tenant_id)

    # If user is not system admin, force their tenant_id
    if current_user.role != "system_admin":
        tenant_id = current_user.tenant_id

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    frequent_errors = ErrorLogService.get_frequent_errors(
        db=db,
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date,
        environment=environment,
        top_n=top_n,
    )

    return [FrequentErrorResponse(**error) for error in frequent_errors]


@router.get("/trend", response_model=List[ErrorTrendResponse])
async def get_error_trend(
    tenant_id: Optional[UUID] = Query(None),
    days: int = Query(7, ge=1, le=365),
    environment: Optional[str] = Query(None),
    interval: str = Query("day", pattern="^(day|hour)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get error trend over time"""
    check_error_log_access(current_user, tenant_id)

    # If user is not system admin, force their tenant_id
    if current_user.role != "system_admin":
        tenant_id = current_user.tenant_id

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    trend = ErrorLogService.get_error_trend(
        db=db,
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date,
        environment=environment,
        interval=interval,
    )

    return [ErrorTrendResponse(**item) for item in trend]


@router.get("/analytics", response_model=ErrorAnalyticsResponse)
async def get_error_analytics(
    tenant_id: Optional[UUID] = Query(None),
    days: int = Query(7, ge=1, le=365),
    environment: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get comprehensive error analytics"""
    check_error_log_access(current_user, tenant_id)

    # If user is not system admin, force their tenant_id
    if current_user.role != "system_admin":
        tenant_id = current_user.tenant_id

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Get summary
    summary = ErrorLogService.get_error_summary(
        db=db,
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date,
        environment=environment,
    )

    # Get frequent errors
    frequent_errors = ErrorLogService.get_frequent_errors(
        db=db,
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date,
        environment=environment,
        top_n=10,
    )

    # Get trend
    trend = ErrorLogService.get_error_trend(
        db=db,
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date,
        environment=environment,
        interval="day",
    )

    return ErrorAnalyticsResponse(
        summary=ErrorSummaryResponse(**summary),
        frequent_errors=[FrequentErrorResponse(**error) for error in frequent_errors],
        trend=[ErrorTrendResponse(**item) for item in trend],
    )


@router.get("/correlation/{correlation_id}", response_model=List[ErrorLogResponse])
async def get_errors_by_correlation(
    correlation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all errors with the same correlation ID"""
    # System admin only for correlation ID queries
    if current_user.role != "system_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system admins can query by correlation ID",
        )

    logs = ErrorLogService.get_error_by_correlation_id(db, correlation_id)

    return [ErrorLogResponse.model_validate(log) for log in logs]


@router.get("/{error_id}", response_model=ErrorLogResponse)
async def get_error_log(
    error_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific error log by ID"""
    from app.models.error_log import ErrorLog

    error_log = db.query(ErrorLog).filter(ErrorLog.id == error_id).first()

    if not error_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Error log not found",
        )

    # Check access
    if current_user.role != "system_admin":
        if error_log.tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only view error logs for your own tenant",
            )

    return ErrorLogResponse.model_validate(error_log)
