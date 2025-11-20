"""
DiagnoLeads FastAPI Application

Multi-tenant B2B assessment platform with AI capabilities.
"""

import logging
import traceback
from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.middleware import TenantMiddleware
from app.models.error_log import ErrorSeverity, ErrorType
from app.services.error_log_service import ErrorLogService

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="Multi-tenant B2B assessment platform with AI",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Multi-tenant Middleware (enforce tenant isolation)
# NOTE: This must be added AFTER CORS middleware so CORS headers are set first
app.add_middleware(TenantMiddleware)

# CORS Middleware - MUST be added last so it wraps everything
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "diagnoleads-api",
            "version": "0.1.0",
        }
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return JSONResponse(
        content={
            "message": "DiagnoLeads API",
            "version": "0.1.0",
            "docs": "/api/docs",
        }
    )


# ============================================================================
# Global Error Handlers
# ============================================================================


def get_client_ip(request: Request) -> Optional[str]:
    """Extract client IP address from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def get_tenant_id_from_request(request: Request) -> Optional[str]:
    """Extract tenant ID from request state"""
    return getattr(request.state, "tenant_id", None)


def get_user_id_from_request(request: Request) -> Optional[str]:
    """Extract user ID from request state"""
    return getattr(request.state, "user_id", None)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    # Log error to database
    db = SessionLocal()
    try:
        # Determine error severity based on status code
        if exc.status_code >= 500:
            severity = ErrorSeverity.HIGH.value
            error_type = ErrorType.INTERNAL_ERROR.value
        elif exc.status_code == 401:
            severity = ErrorSeverity.MEDIUM.value
            error_type = ErrorType.AUTHENTICATION_ERROR.value
        elif exc.status_code == 403:
            severity = ErrorSeverity.MEDIUM.value
            error_type = ErrorType.AUTHORIZATION_ERROR.value
        elif exc.status_code == 422:
            severity = ErrorSeverity.LOW.value
            error_type = ErrorType.VALIDATION_ERROR.value
        else:
            severity = ErrorSeverity.MEDIUM.value
            error_type = ErrorType.API_ERROR.value

        ErrorLogService.log_error(
            db=db,
            error_type=error_type,
            error_message=str(exc.detail),
            tenant_id=get_tenant_id_from_request(request),
            user_id=get_user_id_from_request(request),
            error_code=str(exc.status_code),
            severity=severity,
            endpoint=str(request.url.path),
            method=request.method,
            status_code=exc.status_code,
            environment=settings.ENVIRONMENT,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
        )
    except Exception as e:
        logger.error(f"Failed to log HTTP exception: {str(e)}")
    finally:
        db.close()

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    # Log error to database
    db = SessionLocal()
    try:
        ErrorLogService.log_error(
            db=db,
            error_type=ErrorType.VALIDATION_ERROR.value,
            error_message="Request validation failed",
            tenant_id=get_tenant_id_from_request(request),
            user_id=get_user_id_from_request(request),
            error_code="422",
            severity=ErrorSeverity.LOW.value,
            endpoint=str(request.url.path),
            method=request.method,
            status_code=422,
            context={"validation_errors": exc.errors()},
            environment=settings.ENVIRONMENT,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
        )
    except Exception as e:
        logger.error(f"Failed to log validation exception: {str(e)}")
    finally:
        db.close()

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions"""
    # Get full stack trace
    stack_trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

    # Log to console
    logger.error(f"Unhandled exception: {str(exc)}\n{stack_trace}")

    # Log error to database
    db = SessionLocal()
    try:
        ErrorLogService.log_error(
            db=db,
            error_type=ErrorType.INTERNAL_ERROR.value,
            error_message=str(exc),
            tenant_id=get_tenant_id_from_request(request),
            user_id=get_user_id_from_request(request),
            severity=ErrorSeverity.CRITICAL.value,
            stack_trace=stack_trace,
            endpoint=str(request.url.path),
            method=request.method,
            status_code=500,
            environment=settings.ENVIRONMENT,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
        )
    except Exception as e:
        logger.error(f"Failed to log exception to database: {str(e)}")
    finally:
        db.close()

    # Return user-friendly error message
    # Hide detailed error information in production
    if settings.ENVIRONMENT == "production":
        error_detail = "An internal server error occurred. Please try again later."
    else:
        error_detail = str(exc)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": error_detail,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
