"""
User Service

Business logic for user management operations.
"""

from sqlalchemy.orm import Session
from uuid import UUID
import bcrypt

from app.models.user import User
from app.schemas.user import UserCreate


class UserService:
    """User management service"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against a hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        user = User(
            tenant_id=user_data.tenant_id,
            email=user_data.email,
            password_hash=UserService.hash_password(user_data.password),
            name=user_data.name,
            role=user_data.role or "user",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> User | None:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_tenant_users(db: Session, tenant_id: UUID, skip: int = 0, limit: int = 100):
        """Get all users for a tenant"""
        return db.query(User).filter(User.tenant_id == tenant_id).offset(skip).limit(limit).all()
