"""
Pytest configuration and fixtures for DiagnoLeads tests
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, TypeDecorator, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid

from app.main import app
from app.core.database import Base, get_db


# Use PostgreSQL for testing (same as production)
# This ensures tests are closer to production environment
import os

SQLALCHEMY_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/diagnoleads_test"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_tenant(db_session):
    """Create a test tenant"""
    from app.models.tenant import Tenant
    tenant = Tenant(
        name="Test Tenant",
        slug="test-tenant",
        plan="free",
        settings={},
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture(scope="function")
def test_tenant_2(db_session):
    """Create a second test tenant for cross-tenant tests"""
    from app.models.tenant import Tenant
    tenant = Tenant(
        name="Test Tenant 2",
        slug="test-tenant-2",
        plan="free",
        settings={},
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture(scope="function")
def test_user(db_session, test_tenant):
    """Create a test user"""
    from app.models.user import User
    from app.services.auth import AuthService
    
    user = User(
        email="test@example.com",
        password_hash=AuthService.hash_password("password123"),
        name="Test User",
        tenant_id=test_tenant.id,
        role="tenant_admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden database session"""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
