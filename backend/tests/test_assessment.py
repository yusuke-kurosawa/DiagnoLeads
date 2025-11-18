"""
Assessment API Tests

Tests for assessment CRUD operations with multi-tenant isolation.
"""

import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.tenant import Tenant
from app.models.user import User
from app.models.assessment import Assessment
from app.services.auth import AuthService


@pytest.fixture
def tenant(db_session: Session):
    """Create a test tenant"""
    tenant = Tenant(
        id=uuid.uuid4(),
        name="Test Tenant",
        slug="test-tenant",
        plan="free",
        settings={},
    )
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def user(db_session: Session, tenant: Tenant):
    """Create a test user"""
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        email="test@example.com",
        password_hash=AuthService.hash_password("password123"),
        name="Test User",
        role="tenant_admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(user: User, tenant: Tenant):
    """Generate authentication headers with JWT token"""
    token = AuthService.create_access_token(
        data={
            "sub": str(user.id),
            "tenant_id": str(tenant.id),
            "email": user.email,
        }
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_assessment(db_session: Session, tenant: Tenant, user: User):
    """Create a sample assessment for testing"""
    assessment = Assessment(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        title="Sample Assessment",
        description="This is a test assessment",
        status="draft",
        scoring_logic={},
        created_by=user.id,
    )
    db_session.add(assessment)
    db_session.commit()
    db_session.refresh(assessment)
    return assessment


def test_list_assessments_empty(
    client: TestClient, tenant: Tenant, user: User, auth_headers: dict
):
    """Test listing assessments when none exist"""
    response = client.get(
        f"/api/v1/tenants/{tenant.id}/assessments", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_create_assessment(
    client: TestClient, tenant: Tenant, user: User, auth_headers: dict
):
    """Test creating a new assessment"""
    payload = {
        "title": "Marketing Assessment",
        "description": "Evaluate marketing strategy",
        "status": "draft",
        "topic": "Marketing Strategy",
        "industry": "Technology",
        "ai_generated": "manual",
        "scoring_logic": {"max_score": 100},
    }

    response = client.post(
        f"/api/v1/tenants/{tenant.id}/assessments",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Marketing Assessment"
    assert data["tenant_id"] == str(tenant.id)
    assert data["created_by"] == str(user.id)


def test_get_assessment(
    client: TestClient,
    tenant: Tenant,
    user: User,
    auth_headers: dict,
    sample_assessment: Assessment,
):
    """Test getting a specific assessment"""
    response = client.get(
        f"/api/v1/tenants/{tenant.id}/assessments/{sample_assessment.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_assessment.id)
    assert data["title"] == "Sample Assessment"


def test_list_assessments(
    client: TestClient,
    tenant: Tenant,
    user: User,
    auth_headers: dict,
    sample_assessment: Assessment,
):
    """Test listing all assessments for a tenant"""
    response = client.get(
        f"/api/v1/tenants/{tenant.id}/assessments", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(sample_assessment.id)


def test_update_assessment(
    client: TestClient,
    tenant: Tenant,
    user: User,
    auth_headers: dict,
    sample_assessment: Assessment,
):
    """Test updating an assessment"""
    payload = {"title": "Updated Assessment", "status": "published"}

    response = client.put(
        f"/api/v1/tenants/{tenant.id}/assessments/{sample_assessment.id}",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Assessment"
    assert data["status"] == "published"


def test_delete_assessment(
    client: TestClient,
    tenant: Tenant,
    user: User,
    auth_headers: dict,
    sample_assessment: Assessment,
):
    """Test deleting an assessment"""
    response = client.delete(
        f"/api/v1/tenants/{tenant.id}/assessments/{sample_assessment.id}",
        headers=auth_headers,
    )

    assert response.status_code == 204

    # Verify assessment is deleted
    response = client.get(
        f"/api/v1/tenants/{tenant.id}/assessments/{sample_assessment.id}",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_search_assessments(
    client: TestClient,
    tenant: Tenant,
    user: User,
    auth_headers: dict,
    sample_assessment: Assessment,
):
    """Test searching assessments by title"""
    response = client.get(
        f"/api/v1/tenants/{tenant.id}/assessments/search?q=Sample",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Sample Assessment"


def test_cross_tenant_access_denied(
    client: TestClient, db_session: Session, tenant: Tenant, auth_headers: dict
):
    """
    Test that users cannot access assessments from other tenants

    This is a critical security test.
    """
    # Create another tenant
    other_tenant = Tenant(
        id=uuid.uuid4(),
        name="Other Tenant",
        slug="other-tenant",
        plan="free",
        settings={},
    )
    db_session.add(other_tenant)
    db_session.flush()

    # Create assessment for other tenant
    other_user = User(
        id=uuid.uuid4(),
        tenant_id=other_tenant.id,
        email="other@example.com",
        password_hash="hash",
        name="Other User",
        role="user",
    )
    db_session.add(other_user)
    db_session.flush()

    other_assessment = Assessment(
        id=uuid.uuid4(),
        tenant_id=other_tenant.id,
        title="Other Tenant Assessment",
        status="draft",
        scoring_logic={},
        created_by=other_user.id,
    )
    db_session.add(other_assessment)
    db_session.commit()

    # Try to access other tenant's assessment
    response = client.get(
        f"/api/v1/tenants/{other_tenant.id}/assessments/{other_assessment.id}",
        headers=auth_headers,
    )

    # Should be forbidden
    assert response.status_code == 403


def test_get_nonexistent_assessment(
    client: TestClient, tenant: Tenant, auth_headers: dict
):
    """Test getting a non-existent assessment returns 404"""
    fake_id = uuid.uuid4()
    response = client.get(
        f"/api/v1/tenants/{tenant.id}/assessments/{fake_id}", headers=auth_headers
    )

    assert response.status_code == 404


def test_unauthorized_access(client: TestClient, tenant: Tenant):
    """Test that endpoints require authentication"""
    response = client.get(f"/api/v1/tenants/{tenant.id}/assessments")
    assert response.status_code == 403  # No authentication header
