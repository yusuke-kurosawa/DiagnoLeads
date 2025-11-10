"""
Multi-tenant isolation tests

These tests verify that tenant data is properly isolated
and cross-tenant access is prevented.
"""

import pytest
import uuid
from sqlalchemy.orm import Session

from app.models.tenant import Tenant
from app.models.user import User


@pytest.fixture
def tenant_a(db_session: Session):
    """Create tenant A for testing"""
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Tenant A",
        slug="tenant-a",
        plan="free",
        settings={},
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def tenant_b(db_session: Session):
    """Create tenant B for testing"""
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Tenant B",
        slug="tenant-b",
        plan="free",
        settings={},
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def user_a(db_session: Session, tenant_a: Tenant):
    """Create user for tenant A"""
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_a.id,
        email="user_a@example.com",
        password_hash="hashed_password",
        name="User A",
        role="user",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def user_b(db_session: Session, tenant_b: Tenant):
    """Create user for tenant B"""
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_b.id,
        email="user_b@example.com",
        password_hash="hashed_password",
        name="User B",
        role="user",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_tenant_isolation(db_session: Session, tenant_a: Tenant, tenant_b: Tenant):
    """Test that tenants are properly isolated in database"""
    # Query all tenants
    tenants = db_session.query(Tenant).all()
    assert len(tenants) == 2

    # Verify each tenant exists
    tenant_ids = [t.id for t in tenants]
    assert tenant_a.id in tenant_ids
    assert tenant_b.id in tenant_ids


def test_user_belongs_to_correct_tenant(
    db_session: Session, user_a: User, user_b: User, tenant_a: Tenant, tenant_b: Tenant
):
    """Test that users are associated with correct tenants"""
    # Verify user A belongs to tenant A
    assert user_a.tenant_id == tenant_a.id

    # Verify user B belongs to tenant B
    assert user_b.tenant_id == tenant_b.id


def test_query_users_by_tenant(
    db_session: Session, user_a: User, user_b: User, tenant_a: Tenant, tenant_b: Tenant
):
    """Test querying users filtered by tenant_id"""
    # Query users for tenant A
    users_a = (
        db_session.query(User).filter(User.tenant_id == tenant_a.id).all()
    )
    assert len(users_a) == 1
    assert users_a[0].id == user_a.id

    # Query users for tenant B
    users_b = (
        db_session.query(User).filter(User.tenant_id == tenant_b.id).all()
    )
    assert len(users_b) == 1
    assert users_b[0].id == user_b.id


def test_cross_tenant_data_access_prevented(
    db_session: Session, user_a: User, user_b: User, tenant_a: Tenant, tenant_b: Tenant
):
    """
    Test that cross-tenant data access is prevented
    
    This is a critical security test to ensure tenant isolation.
    """
    # Try to query user B's data with tenant A's filter
    cross_tenant_query = (
        db_session.query(User)
        .filter(User.tenant_id == tenant_a.id)
        .filter(User.id == user_b.id)
        .first()
    )

    # Should return None because user B belongs to tenant B, not A
    assert cross_tenant_query is None

    # Verify the opposite direction
    cross_tenant_query_reverse = (
        db_session.query(User)
        .filter(User.tenant_id == tenant_b.id)
        .filter(User.id == user_a.id)
        .first()
    )

    # Should also return None
    assert cross_tenant_query_reverse is None


def test_tenant_cascade_delete(
    db_session: Session, tenant_a: Tenant, user_a: User
):
    """Test that deleting a tenant cascades to users"""
    # Verify user exists
    user = db_session.query(User).filter(User.id == user_a.id).first()
    assert user is not None

    # Delete tenant
    db_session.delete(tenant_a)
    db_session.commit()

    # Verify user was also deleted (cascade)
    user = db_session.query(User).filter(User.id == user_a.id).first()
    assert user is None
