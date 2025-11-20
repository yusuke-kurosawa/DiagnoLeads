"""
Error Log Service

Handles error logging, retrieval, and analysis.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models.error_log import Environment, ErrorLog, ErrorSeverity

logger = logging.getLogger(__name__)


class ErrorLogService:
    """Service for managing error logs"""

    @staticmethod
    def log_error(
        db: Session,
        error_type: str,
        error_message: str,
        tenant_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        error_code: Optional[str] = None,
        severity: str = ErrorSeverity.MEDIUM.value,
        stack_trace: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        status_code: Optional[int] = None,
        request_body: Optional[Dict[str, Any]] = None,
        request_headers: Optional[Dict[str, Any]] = None,
        response_body: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        environment: str = Environment.DEVELOPMENT.value,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        workflow_name: Optional[str] = None,
        job_name: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> ErrorLog:
        """
        Create an error log entry

        Args:
            db: Database session
            error_type: Type of error (from ErrorType enum)
            error_message: Error message
            tenant_id: Optional tenant ID
            user_id: Optional user ID
            error_code: Optional error code
            severity: Error severity (from ErrorSeverity enum)
            stack_trace: Full stack trace
            endpoint: API endpoint
            method: HTTP method
            status_code: HTTP status code
            request_body: Request body data
            request_headers: Request headers
            response_body: Response body data
            duration_ms: Request duration in milliseconds
            environment: Environment (dev/staging/prod)
            ip_address: Client IP address
            user_agent: Client user agent
            context: Additional context data
            correlation_id: Correlation ID for tracing
            workflow_name: GitHub Actions workflow name
            job_name: GitHub Actions job name
            run_id: GitHub Actions run ID

        Returns:
            ErrorLog: Created error log entry
        """
        try:
            # Sanitize sensitive data from headers
            if request_headers:
                request_headers = {
                    k: v if k.lower() not in ["authorization", "cookie", "x-api-key"] else "***REDACTED***"
                    for k, v in request_headers.items()
                }

            error_log = ErrorLog(
                tenant_id=tenant_id,
                user_id=user_id,
                error_type=error_type,
                error_code=error_code,
                severity=severity,
                error_message=error_message,
                stack_trace=stack_trace,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                request_body=request_body,
                request_headers=request_headers,
                response_body=response_body,
                duration_ms=duration_ms,
                environment=environment,
                ip_address=ip_address,
                user_agent=user_agent,
                context=context,
                correlation_id=correlation_id,
                workflow_name=workflow_name,
                job_name=job_name,
                run_id=run_id,
            )

            db.add(error_log)
            db.commit()
            db.refresh(error_log)

            logger.info(f"Error logged: {error_type} - {error_message[:100]}")
            return error_log

        except Exception as e:
            logger.error(f"Failed to log error to database: {str(e)}")
            db.rollback()
            # Don't raise exception to avoid error logging loop
            return None

    @staticmethod
    def get_error_logs(
        db: Session,
        tenant_id: Optional[UUID] = None,
        error_type: Optional[str] = None,
        severity: Optional[str] = None,
        environment: Optional[str] = None,
        endpoint: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        correlation_id: Optional[str] = None,
        workflow_name: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[ErrorLog], int]:
        """
        Get error logs with optional filtering

        Args:
            db: Database session
            tenant_id: Filter by tenant ID
            error_type: Filter by error type
            severity: Filter by severity
            environment: Filter by environment
            endpoint: Filter by endpoint
            start_date: Filter by start date
            end_date: Filter by end date
            correlation_id: Filter by correlation ID
            workflow_name: Filter by workflow name
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            tuple: (List of error logs, total count)
        """
        query = db.query(ErrorLog)

        # Apply filters
        if tenant_id:
            query = query.filter(ErrorLog.tenant_id == tenant_id)

        if error_type:
            query = query.filter(ErrorLog.error_type == error_type)

        if severity:
            query = query.filter(ErrorLog.severity == severity)

        if environment:
            query = query.filter(ErrorLog.environment == environment)

        if endpoint:
            query = query.filter(ErrorLog.endpoint == endpoint)

        if start_date:
            query = query.filter(ErrorLog.created_at >= start_date)

        if end_date:
            query = query.filter(ErrorLog.created_at <= end_date)

        if correlation_id:
            query = query.filter(ErrorLog.correlation_id == correlation_id)

        if workflow_name:
            query = query.filter(ErrorLog.workflow_name == workflow_name)

        # Get total count
        total_count = query.count()

        # Order by created_at descending (newest first)
        logs = query.order_by(desc(ErrorLog.created_at)).offset(skip).limit(limit).all()

        return logs, total_count

    @staticmethod
    def get_error_summary(
        db: Session,
        tenant_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        environment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get error summary statistics

        Args:
            db: Database session
            tenant_id: Filter by tenant ID
            start_date: Start date for analysis
            end_date: End date for analysis
            environment: Filter by environment

        Returns:
            dict: Summary statistics
        """
        query = db.query(ErrorLog)

        # Apply filters
        if tenant_id:
            query = query.filter(ErrorLog.tenant_id == tenant_id)

        if environment:
            query = query.filter(ErrorLog.environment == environment)

        if start_date:
            query = query.filter(ErrorLog.created_at >= start_date)

        if end_date:
            query = query.filter(ErrorLog.created_at <= end_date)

        # Total errors
        total_errors = query.count()

        # Errors by type
        errors_by_type = (
            query.with_entities(ErrorLog.error_type, func.count(ErrorLog.id))
            .group_by(ErrorLog.error_type)
            .all()
        )

        # Errors by severity
        errors_by_severity = (
            query.with_entities(ErrorLog.severity, func.count(ErrorLog.id))
            .group_by(ErrorLog.severity)
            .all()
        )

        # Critical errors
        critical_errors = query.filter(ErrorLog.severity == ErrorSeverity.CRITICAL.value).count()

        return {
            "total_errors": total_errors,
            "errors_by_type": {error_type: count for error_type, count in errors_by_type},
            "errors_by_severity": {severity: count for severity, count in errors_by_severity},
            "critical_errors": critical_errors,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
        }

    @staticmethod
    def get_frequent_errors(
        db: Session,
        tenant_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        environment: Optional[str] = None,
        top_n: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get most frequent errors

        Args:
            db: Database session
            tenant_id: Filter by tenant ID
            start_date: Start date for analysis
            end_date: End date for analysis
            environment: Filter by environment
            top_n: Number of top errors to return

        Returns:
            list: List of frequent errors with counts
        """
        query = db.query(ErrorLog)

        # Apply filters
        if tenant_id:
            query = query.filter(ErrorLog.tenant_id == tenant_id)

        if environment:
            query = query.filter(ErrorLog.environment == environment)

        if start_date:
            query = query.filter(ErrorLog.created_at >= start_date)

        if end_date:
            query = query.filter(ErrorLog.created_at <= end_date)

        # Group by error message and count
        frequent_errors = (
            query.with_entities(
                ErrorLog.error_type,
                ErrorLog.error_message,
                ErrorLog.endpoint,
                func.count(ErrorLog.id).label("count"),
                func.max(ErrorLog.created_at).label("last_occurrence"),
            )
            .group_by(ErrorLog.error_type, ErrorLog.error_message, ErrorLog.endpoint)
            .order_by(desc("count"))
            .limit(top_n)
            .all()
        )

        return [
            {
                "error_type": error_type,
                "error_message": error_message,
                "endpoint": endpoint,
                "count": count,
                "last_occurrence": last_occurrence.isoformat() if last_occurrence else None,
            }
            for error_type, error_message, endpoint, count, last_occurrence in frequent_errors
        ]

    @staticmethod
    def get_error_trend(
        db: Session,
        tenant_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        environment: Optional[str] = None,
        interval: str = "day",
    ) -> List[Dict[str, Any]]:
        """
        Get error trend over time

        Args:
            db: Database session
            tenant_id: Filter by tenant ID
            start_date: Start date for analysis
            end_date: End date for analysis
            environment: Filter by environment
            interval: Time interval (day, hour)

        Returns:
            list: List of error counts by time interval
        """
        query = db.query(ErrorLog)

        # Apply filters
        if tenant_id:
            query = query.filter(ErrorLog.tenant_id == tenant_id)

        if environment:
            query = query.filter(ErrorLog.environment == environment)

        if not start_date:
            start_date = datetime.now() - timedelta(days=7)

        if not end_date:
            end_date = datetime.now()

        query = query.filter(ErrorLog.created_at >= start_date, ErrorLog.created_at <= end_date)

        # Group by time interval
        if interval == "day":
            time_column = func.date_trunc("day", ErrorLog.created_at)
        elif interval == "hour":
            time_column = func.date_trunc("hour", ErrorLog.created_at)
        else:
            time_column = func.date_trunc("day", ErrorLog.created_at)

        trend_data = (
            query.with_entities(
                time_column.label("time_interval"),
                func.count(ErrorLog.id).label("count"),
            )
            .group_by("time_interval")
            .order_by("time_interval")
            .all()
        )

        return [
            {
                "timestamp": time_interval.isoformat() if time_interval else None,
                "count": count,
            }
            for time_interval, count in trend_data
        ]

    @staticmethod
    def get_error_by_correlation_id(
        db: Session, correlation_id: str
    ) -> List[ErrorLog]:
        """
        Get all errors with the same correlation ID

        Args:
            db: Database session
            correlation_id: Correlation ID

        Returns:
            list: List of related error logs
        """
        return (
            db.query(ErrorLog)
            .filter(ErrorLog.correlation_id == correlation_id)
            .order_by(ErrorLog.created_at)
            .all()
        )

    @staticmethod
    def cleanup_old_logs(
        db: Session,
        days: int = 90,
        environment: Optional[str] = None,
    ) -> int:
        """
        Delete error logs older than specified days

        Args:
            db: Database session
            days: Number of days to keep
            environment: Optional environment filter

        Returns:
            int: Number of deleted records
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        query = db.query(ErrorLog).filter(ErrorLog.created_at < cutoff_date)

        if environment:
            query = query.filter(ErrorLog.environment == environment)

        # Delete only non-critical errors
        query = query.filter(ErrorLog.severity != ErrorSeverity.CRITICAL.value)

        deleted_count = query.delete()
        db.commit()

        logger.info(f"Cleaned up {deleted_count} old error logs (older than {days} days)")
        return deleted_count
