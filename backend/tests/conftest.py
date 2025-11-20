"""
Pytest configuration and fixtures for DiagnoLeads tests
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app

# Use TEST_DATABASE_URL if available, otherwise DATABASE_URL,
# fallback to localhost PostgreSQL
SQLALCHEMY_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres"),
)

# Create engine with appropriate settings
engine = create_engine(SQLALCHEMY_DATABASE_URL)


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Check if database is available
def is_database_available():
    """
    Check if PostgreSQL database is available and accessible.

    Returns:
        bool: True if database connection succeeds, False otherwise
    """
    try:
        # Try to connect to the database
        connection = engine.connect()
        connection.close()
        return True
    except Exception as e:
        # Database not available (server not running, connection refused, etc.)
        print(f"\n⚠️  Database not available: {e}")
        print("💡 Database-dependent tests will be skipped.")
        print("   To run all tests, start PostgreSQL server on localhost:5432")
        return False


# Global flag for database availability
DB_AVAILABLE = is_database_available()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    if not DB_AVAILABLE:
        pytest.skip("PostgreSQL database not available. Start PostgreSQL on localhost:5432 to run this test.")

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
