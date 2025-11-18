"""
Dependencies for FastAPI endpoints

Provides database session, authentication, and authorization dependencies.
"""

from typing import Generator, Optional
from contextvars import ContextVar

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.user import User
from app.models.tenant import Tenant
from app.services.auth import AuthService
from app.services.ai_service import AIService

security = HTTPBearer()

# Context variable to store current tenant_id (set by TenantMiddleware)
current_tenant_id: ContextVar[Optional[str]] = ContextVar('current_tenant_id', default=None)


def get_db() -> Generator[Session, None, None]:
    """Get database session with tenant context for RLS"""
    db = SessionLocal()
    try:
        # Get tenant_id from context variable (set by TenantMiddleware)
        tenant_id = current_tenant_id.get()
        
        # Set tenant context for Row-Level Security (RLS)
        if tenant_id:
            from sqlalchemy import text
            # Use parameterized query to prevent SQL injection
            db.execute(text("SELECT set_config('app.current_tenant_id', :tenant_id, false)"), 
                      {"tenant_id": tenant_id})
        
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization credentials",
        )
    
    token = credentials.credentials

    # Decode token
    token_data = AuthService.decode_access_token(token)

    if not token_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user_id",
        )

    # Get user from database
    user = AuthService.get_user_by_id(db, user_id=token_data.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User not found for id {token_data.user_id}",
        )

    return user


def get_current_tenant(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Tenant:
    """
    Get current user's tenant
    
    Raises:
        HTTPException: If tenant not found
    """
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    return tenant


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current active user (not disabled)
    
    Note: User model doesn't have is_active field yet.
    This is a placeholder for future implementation.
    """
    # TODO: Add is_active field to User model
    # if not current_user.is_active:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Inactive user"
    #     )
    return current_user


def verify_tenant_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Verify current user is a tenant admin

    Raises:
        HTTPException: If user is not a tenant admin
    """
    if current_user.role not in ["tenant_admin", "system_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Tenant admin role required.",
        )

    return current_user


def get_ai_service() -> AIService:
    """
    Get AI service instance for dependency injection.

    Returns:
        AIService instance
    """
    return AIService()
