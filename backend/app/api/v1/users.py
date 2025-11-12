"""
User Management API Endpoints

Provides access to user management for tenant admins and system admins.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService


router = APIRouter(prefix="/users", tags=["Users"])


def check_admin_access(current_user: User, tenant_id: UUID):
    """Verify that user is admin for the requested tenant"""
    # System admin can manage any tenant
    if current_user.role == "system_admin":
        return current_user
    
    # Tenant admin can only manage their own tenant
    if current_user.role == "tenant_admin" and current_user.tenant_id == tenant_id:
        return current_user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only administrators can manage users",
    )


@router.get("", response_model=List[UserResponse])
async def list_users(
    tenant_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List users (admin only)
    
    - System admin: Can see all users (tenant_id optional, shows all if not provided)
    - Tenant admin: Can only see users in their tenant
    """
    # System admin can see all users or filter by tenant
    if current_user.role == "system_admin":
        if tenant_id:
            # Filter by specific tenant
            users = db.query(User).filter(User.tenant_id == tenant_id).offset(skip).limit(limit).all()
        else:
            # Return all users from all tenants
            users = db.query(User).offset(skip).limit(limit).all()
    # Tenant admin can only see users in their tenant
    elif current_user.role == "tenant_admin":
        if tenant_id and tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant admins can only view users in their own tenant",
            )
        users = db.query(User).filter(User.tenant_id == current_user.tenant_id).offset(skip).limit(limit).all()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can manage users",
        )
    
    # Build responses with tenant information
    responses = []
    for user in users:
        response = UserResponse.from_orm(user)
        if user.tenant:
            response.tenant_name = user.tenant.name
        responses.append(response)
    return responses


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific user details (admin or self)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Allow user to view themselves or allow admin to view their tenant's users
    if current_user.id != user_id:
        if current_user.role == "system_admin":
            pass  # System admin can view any user
        elif current_user.role == "tenant_admin" and current_user.tenant_id == user.tenant_id:
            pass  # Tenant admin can view users in their tenant
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view this user",
            )
    
    return UserResponse.from_orm(user)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new user (admin only)"""
    check_admin_access(current_user, user_data.tenant_id)
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    
    # Create new user
    user = UserService.create_user(db, user_data)
    return UserResponse.from_orm(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a user (admin or self)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check access permissions
    if current_user.id != user_id:
        check_admin_access(current_user, user.tenant_id)
    
    # Update user fields
    if user_data.name is not None:
        user.name = user_data.name
    
    if user_data.email is not None:
        # Check for duplicate email
        duplicate = db.query(User).filter(
            User.email == user_data.email,
            User.id != user_id
        ).first()
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )
        user.email = user_data.email
    
    if user_data.role is not None:
        # Only admins can change roles
        if current_user.role != "system_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only system admins can change user roles",
            )
        user.role = user_data.role
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return UserResponse.from_orm(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Prevent self-deletion
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )
    
    check_admin_access(current_user, user.tenant_id)
    
    db.delete(user)
    db.commit()
