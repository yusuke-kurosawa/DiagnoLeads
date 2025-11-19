"""
Pytest configuration and fixtures for DiagnoLeads tests
"""

import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.database import Base, get_db

# Use PostgreSQL for testing
import os

# Get base database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/diagnoleads_test"
)

# Async database URL (for async tests)
if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace(
        "postgresql://", "postgresql+asyncpg://", 1
    )
elif DATABASE_URL.startswith("postgresql+asyncpg://"):
    ASYNC_DATABASE_URL = DATABASE_URL
else:
    ASYNC_DATABASE_URL = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/diagnoleads_test"
    )

# Sync database URL (for sync tests)
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    SYNC_DATABASE_URL = DATABASE_URL.replace(
        "postgresql+asyncpg://", "postgresql://", 1
    )
elif DATABASE_URL.startswith("postgresql://"):
    SYNC_DATABASE_URL = DATABASE_URL
else:
    SYNC_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/diagnoleads_test"

# Create async engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    poolclass=NullPool,  # Disable pooling for tests
)

# Create sync engine
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    poolclass=NullPool,  # Disable pooling for tests
)

TestingSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

SyncTestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=sync_engine
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db():
    """Create a fresh async database session for each test"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh sync database session for each test"""
    Base.metadata.create_all(bind=sync_engine)
    session = SyncTestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=sync_engine)


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession):
    """Create a test client with overridden database session"""

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_tenant(db: AsyncSession):
    """Create a test tenant"""
    from app.models.tenant import Tenant

    tenant = Tenant(
        name="Test Tenant",
        slug="test-tenant",
        plan="free",
        settings={},
    )
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return tenant


@pytest_asyncio.fixture
async def test_tenant_2(db: AsyncSession):
    """Create a second test tenant for cross-tenant tests"""
    from app.models.tenant import Tenant

    tenant = Tenant(
        name="Test Tenant 2",
        slug="test-tenant-2",
        plan="free",
        settings={},
    )
    db.add(tenant)
    await db.commit()
    await db.refresh(tenant)
    return tenant


@pytest_asyncio.fixture
async def test_user(db: AsyncSession, test_tenant):
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
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
