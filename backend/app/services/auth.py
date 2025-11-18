"""
Authentication Service

Handles password hashing, JWT token generation, and user authentication.
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
import uuid
import secrets

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.models import User, Tenant
from app.schemas.auth import UserCreate, TokenData


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service for user management and JWT tokens"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a new JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> TokenData:
        """Decode and validate a JWT token"""
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id: Optional[str] = payload.get("sub")
            tenant_id: Optional[str] = payload.get("tenant_id")
            email: Optional[str] = payload.get("email")

            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                )

            return TokenData(
                user_id=UUID(user_id) if user_id else None,
                tenant_id=UUID(tenant_id) if tenant_id else None,
                email=email,
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user with a new tenant"""
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このメールアドレスは既に使用されています",
            )

        # Check if tenant slug already exists
        existing_tenant = (
            db.query(Tenant).filter(Tenant.slug == user_data.tenant_slug).first()
        )
        if existing_tenant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このテナントスラッグは既に使用されています",
            )

        # Create new tenant
        tenant = Tenant(
            id=uuid.uuid4(),
            name=user_data.tenant_name,
            slug=user_data.tenant_slug,
            plan="free",
            settings={},
        )
        db.add(tenant)
        db.flush()  # Get tenant ID without committing

        # Create new user as tenant admin
        user = User(
            id=uuid.uuid4(),
            tenant_id=tenant.id,
            email=user_data.email,
            password_hash=AuthService.hash_password(user_data.password),
            name=user_data.name,
            role="tenant_admin",  # First user is tenant admin
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create a refresh token (valid for 7 days)"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def create_password_reset_token() -> str:
        """Generate a secure password reset token"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def create_password_reset_request(
        db: Session, email: str
    ) -> Optional[tuple[User, str]]:
        """
        Create a password reset request and return user and token
        Returns (user, token) or None if user not found
        """
        user = AuthService.get_user_by_email(db, email)
        if not user:
            return None

        # Generate reset token (valid for 1 hour)
        reset_token = AuthService.create_password_reset_token()
        user.password_reset_token = reset_token
        user.password_reset_expires_at = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        db.refresh(user)

        return user, reset_token

    @staticmethod
    def verify_password_reset_token(db: Session, token: str) -> Optional[User]:
        """Verify password reset token and return user if valid"""
        user = (
            db.query(User)
            .filter(User.password_reset_token == token)
            .filter(User.password_reset_expires_at > datetime.utcnow())
            .first()
        )
        return user

    @staticmethod
    def reset_password(db: Session, user: User, new_password: str) -> User:
        """Reset user password and clear reset token"""
        user.password_hash = AuthService.hash_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires_at = None
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def check_and_increment_login_attempts(
        db: Session, email: str
    ) -> tuple[bool, Optional[str]]:
        """
        Check login attempts and increment counter.
        Returns (can_attempt, error_message)
        """
        user = AuthService.get_user_by_email(db, email)
        if not user:
            return True, None

        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            remaining_minutes = int(
                (user.locked_until - datetime.utcnow()).total_seconds() / 60
            )
            return (
                False,
                f"アカウントが一時的にロックされています。{remaining_minutes}分後に再試行してください",
            )

        # Check if max attempts exceeded
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            db.commit()
            return (
                False,
                "アカウントが一時的にロックされています。15分後に再試行してください",
            )

        # Increment attempts
        user.failed_login_attempts += 1
        db.commit()

        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            db.commit()
            return (
                False,
                "アカウントが一時的にロックされています。15分後に再試行してください",
            )

        return True, None

    @staticmethod
    def reset_login_attempts(user: User, db: Session) -> None:
        """Reset login attempts after successful login"""
        user.failed_login_attempts = 0
        user.locked_until = None
        db.commit()
