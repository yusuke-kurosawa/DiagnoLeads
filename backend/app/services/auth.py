"""
Authentication Service

Handles password hashing, JWT token generation, and user authentication.
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
import uuid

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
                detail="Email already registered",
            )

        # Check if tenant slug already exists
        existing_tenant = (
            db.query(Tenant).filter(Tenant.slug == user_data.tenant_slug).first()
        )
        if existing_tenant:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tenant slug already taken",
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
