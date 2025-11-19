"""
Authentication API Endpoints

Handles user registration, login, and token management.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.schemas.auth import (
    PasswordResetConfirm,
    PasswordResetRequest,
    Token,
    TokenRefresh,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.auth import AuthService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def build_user_response(user) -> UserResponse:
    """
    Build UserResponse with tenant information.
    Safely handles cases where tenant relationship might not be loaded.
    """
    tenant_name = None
    tenant_slug = None
    tenant_plan = None

    if hasattr(user, "tenant") and user.tenant:
        tenant_name = user.tenant.name
        tenant_slug = user.tenant.slug
        tenant_plan = user.tenant.plan

    return UserResponse(
        id=user.id,
        tenant_id=user.tenant_id,
        email=user.email,
        name=user.name,
        role=user.role,
        tenant_name=tenant_name,
        tenant_slug=tenant_slug,
        tenant_plan=tenant_plan,
        created_at=user.created_at,
    )


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new user and create a new tenant.

    The first user of a tenant is automatically assigned the 'tenant_admin' role.
    """
    user = AuthService.create_user(db, user_data)

    # Generate access token
    access_token = AuthService.create_access_token(
        data={
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id),
            "email": user.email,
        }
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=build_user_response(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Login with email and password.

    Returns both access and refresh tokens on success.
    Implements rate limiting: 5 failed attempts lock for 15 minutes.
    """
    email = form_data.username

    # Check login attempt limits first
    can_attempt, error_msg = AuthService.check_and_increment_login_attempts(db, email)
    if not can_attempt:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=error_msg,
        )

    # Authenticate user
    user = AuthService.authenticate_user(db, email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Reset login attempts on successful login
    AuthService.reset_login_attempts(user, db)

    # Generate tokens
    access_token = AuthService.create_access_token(
        data={
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id),
            "email": user.email,
        }
    )
    refresh_token = AuthService.create_refresh_token(
        data={
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id),
            "email": user.email,
        }
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=86400,  # 24 hours
        user=build_user_response(user),
    )


@router.post("/login/json", response_model=Token)
async def login_json(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    """
    Login with JSON payload (alternative to form-based login).

    Returns a JWT access token on success.
    """
    user = AuthService.authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
        )

    # Generate access token
    access_token = AuthService.create_access_token(
        data={
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id),
            "email": user.email,
        }
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=build_user_response(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Get current authenticated user info.

    Requires a valid JWT token in the Authorization header.
    """
    token_data = AuthService.decode_access_token(token)

    if not token_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = AuthService.get_user_by_id(db, token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return build_user_response(user)


@router.post("/password-reset", status_code=status.HTTP_200_OK)
async def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    """
    Request a password reset.

    Sends a password reset link to the user's email.
    """
    result = AuthService.create_password_reset_request(db, request.email)

    if not result:
        # Don't reveal if email exists (security best practice)
        return {"message": "パスワードリセットメールを送信しました"}

    user, reset_token = result

    # Send password reset email
    from app.services.email_service import email_service

    email_sent = email_service.send_password_reset_email(
        to_email=user.email,
        reset_token=reset_token,
        user_name=user.name,
    )

    if not email_sent:
        # Fallback: log the token for development
        print(f"🔐 Password reset token for {user.email}: {reset_token}")
        print(f"Reset link: http://localhost:5173/reset-password?token={reset_token}")

    return {"message": "パスワードリセットメールを送信しました"}


@router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    """
    Confirm password reset with token and new password.

    Validates the reset token and updates the password.
    """
    user = AuthService.verify_password_reset_token(db, request.token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無効または期限切れのリセットトークンです",
        )

    # Reset password
    AuthService.reset_password(db, user, request.password)

    return {"message": "パスワードを更新しました。ログインしてください。"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: TokenRefresh,
    db: Session = Depends(get_db),
):
    """
    Refresh access token using refresh token.

    Returns a new access token and refresh token.
    """
    try:
        payload = jwt.decode(
            request.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        email = payload.get("email")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        user = AuthService.get_user_by_id(db, UUID(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Generate new tokens
        new_access_token = AuthService.create_access_token(
            data={
                "sub": user_id,
                "tenant_id": tenant_id,
                "email": email,
            }
        )
        new_refresh_token = AuthService.create_refresh_token(
            data={
                "sub": user_id,
                "tenant_id": tenant_id,
                "email": email,
            }
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=86400,
            user=build_user_response(user),
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
