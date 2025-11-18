"""
Analytics API Tests

Comprehensive tests for Analytics endpoints with multi-tenant isolation.
Following OpenSpec test strategy from openspec/specs/features/analytics-dashboard.md
"""

from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.assessment import Assessment
from app.models.user import User
from app.services.auth import AuthService


def test_get_overview_analytics(
    client: TestClient, db_session: Session, test_user: User
):
    """Test getting overview analytics"""
    auth_service = AuthService()
    token = auth_service.create_access_token(
        {
            "sub": str(test_user.id),
            "tenant_id": str(test_user.tenant_id),
            "email": test_user.email,
        }
    )

    # Create test data
    for i in range(5):
        lead = Lead(
            name=f"Lead {i}",
            email=f"lead{i}@example.com",
            status="new" if i < 2 else "contacted",
            score=i * 20,
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            tags=[],
            custom_fields={},
        )
        db_session.add(lead)

    for i in range(3):
        assessment = Assessment(
            title=f"Assessment {i}",
            description="Test",
            status="published" if i < 2 else "draft",
            ai_generated="ai" if i == 0 else "manual",
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
        )
        db_session.add(assessment)

    db_session.commit()

    response = client.get(
        f"/api/v1/tenants/{test_user.tenant_id}/analytics/overview",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()

    # Verify structure
    assert "tenant_id" in data
    assert "period" in data
    assert "leads" in data
    assert "assessments" in data
    assert "generated_at" in data

    # Verify lead analytics
    assert data["leads"]["total"] == 5
    assert data["leads"]["new"] == 2
    assert data["leads"]["contacted"] == 3

    # Verify assessment analytics
    assert data["assessments"]["total"] == 3
    assert data["assessments"]["published"] == 2
    assert data["assessments"]["draft"] == 1


def test_get_lead_analytics(client: TestClient, db_session: Session, test_user: User):
    """Test getting detailed lead analytics"""
    auth_service = AuthService()
    token = auth_service.create_access_token(
        {
            "sub": str(test_user.id),
            "tenant_id": str(test_user.tenant_id),
            "email": test_user.email,
        }
    )

    # Create leads with different scores and statuses
    leads_data = [
        {
            "name": "Hot Lead 1",
            "email": "hot1@example.com",
            "status": "qualified",
            "score": 80,
        },
        {
            "name": "Hot Lead 2",
            "email": "hot2@example.com",
            "status": "converted",
            "score": 90,
        },
        {
            "name": "Warm Lead",
            "email": "warm@example.com",
            "status": "contacted",
            "score": 45,
        },
        {
            "name": "Cold Lead 1",
            "email": "cold1@example.com",
            "status": "new",
            "score": 20,
        },
        {
            "name": "Cold Lead 2",
            "email": "cold2@example.com",
            "status": "disqualified",
            "score": 10,
        },
    ]

    for lead_data in leads_data:
        lead = Lead(
            **lead_data,
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            tags=[],
            custom_fields={},
        )
        db_session.add(lead)
    db_session.commit()

    response = client.get(
        f"/api/v1/tenants/{test_user.tenant_id}/analytics/leads",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()

    # Verify counts
    assert data["total"] == 5
    assert data["new"] == 1
    assert data["contacted"] == 1
    assert data["qualified"] == 1
    assert data["converted"] == 1
    assert data["disqualified"] == 1

    # Verify score distribution
    assert data["hot_leads"] == 2  # score >= 61
    assert data["warm_leads"] == 1  # score 31-60
    assert data["cold_leads"] == 2  # score <= 30

    # Verify average score
    expected_avg = (80 + 90 + 45 + 20 + 10) / 5
    assert data["average_score"] == round(expected_avg, 2)

    # Verify conversion rate
    expected_rate = (1 / 5) * 100  # 1 converted out of 5
    assert data["conversion_rate"] == round(expected_rate, 2)


def test_get_assessment_analytics(
    client: TestClient, db_session: Session, test_user: User
):
    """Test getting detailed assessment analytics"""
    auth_service = AuthService()
    token = auth_service.create_access_token(
        {
            "sub": str(test_user.id),
            "tenant_id": str(test_user.tenant_id),
            "email": test_user.email,
        }
    )

    # Create assessments with different statuses and AI generation types
    assessments_data = [
        {"title": "Assessment 1", "status": "published", "ai_generated": "ai"},
        {"title": "Assessment 2", "status": "published", "ai_generated": "ai"},
        {"title": "Assessment 3", "status": "draft", "ai_generated": "manual"},
        {"title": "Assessment 4", "status": "draft", "ai_generated": "manual"},
        {"title": "Assessment 5", "status": "archived", "ai_generated": "hybrid"},
    ]

    for assessment_data in assessments_data:
        assessment = Assessment(
            **assessment_data,
            description="Test",
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
        )
        db_session.add(assessment)
    db_session.commit()

    response = client.get(
        f"/api/v1/tenants/{test_user.tenant_id}/analytics/assessments",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()

    # Verify counts
    assert data["total"] == 5
    assert data["published"] == 2
    assert data["draft"] == 2
    assert data["archived"] == 1

    # Verify AI generation counts
    assert data["ai_generated"] == 2
    assert data["manual_created"] == 2
    assert data["hybrid"] == 1


def test_get_trends_leads(client: TestClient, db_session: Session, test_user: User):
    """Test getting lead trends over 30 days"""
    auth_service = AuthService()
    token = auth_service.create_access_token(
        {
            "sub": str(test_user.id),
            "tenant_id": str(test_user.tenant_id),
            "email": test_user.email,
        }
    )

    # Create leads with different creation dates
    base_date = datetime.utcnow() - timedelta(days=10)

    for i in range(5):
        lead = Lead(
            name=f"Lead {i}",
            email=f"lead{i}@example.com",
            status="new",
            score=50,
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            tags=[],
            custom_fields={},
            created_at=base_date + timedelta(days=i * 2),
        )
        db_session.add(lead)
    db_session.commit()

    response = client.get(
        f"/api/v1/tenants/{test_user.tenant_id}/analytics/trends?period=30d&metric=leads",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()

    # Verify structure
    assert data["period"] == "31d"  # 30 days + 1
    assert data["metric"] == "leads"
    assert "data_points" in data
    assert "summary" in data

    # Verify data points (should have 31 data points for 30d period)
    assert len(data["data_points"]) == 31

    # Verify summary
    assert data["summary"]["total"] == 5
    assert "average_per_day" in data["summary"]


def test_get_trends_assessments(
    client: TestClient, db_session: Session, test_user: User
):
    """Test getting assessment trends over 7 days"""
    auth_service = AuthService()
    token = auth_service.create_access_token(
        {
            "sub": str(test_user.id),
            "tenant_id": str(test_user.tenant_id),
            "email": test_user.email,
        }
    )

    # Create assessments with different creation dates
    base_date = datetime.utcnow() - timedelta(days=5)

    for i in range(3):
        assessment = Assessment(
            title=f"Assessment {i}",
            description="Test",
            status="published",
            ai_generated="ai",
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            created_at=base_date + timedelta(days=i),
        )
        db_session.add(assessment)
    db_session.commit()

    response = client.get(
        f"/api/v1/tenants/{test_user.tenant_id}/analytics/trends?period=7d&metric=assessments",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()

    # Verify structure
    assert data["period"] == "8d"  # 7 days + 1
    assert data["metric"] == "assessments"
    assert len(data["data_points"]) == 8
    assert data["summary"]["total"] == 3


def test_empty_analytics(client: TestClient, db_session: Session, test_user: User):
    """Test analytics with no data"""
    auth_service = AuthService()
    token = auth_service.create_access_token(
        {
            "sub": str(test_user.id),
            "tenant_id": str(test_user.tenant_id),
            "email": test_user.email,
        }
    )

    response = client.get(
        f"/api/v1/tenants/{test_user.tenant_id}/analytics/overview",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()

    # All values should be 0 or empty
    assert data["leads"]["total"] == 0
    assert data["leads"]["average_score"] == 0.0
    assert data["leads"]["conversion_rate"] == 0.0

    assert data["assessments"]["total"] == 0


def test_cross_tenant_analytics_access_denied(
    client: TestClient, db_session: Session, test_user: User, test_tenant_2
):
    """Test that users cannot access analytics from other tenants"""
    auth_service = AuthService()
    token = auth_service.create_access_token(
        {
            "sub": str(test_user.id),
            "tenant_id": str(test_user.tenant_id),
            "email": test_user.email,
        }
    )

    # Try to access analytics from another tenant
    response = client.get(
        f"/api/v1/tenants/{test_tenant_2.id}/analytics/overview",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert "forbidden" in response.json()["detail"].lower()


def test_analytics_unauthorized(client: TestClient, test_user: User):
    """Test analytics access without authentication"""
    response = client.get(
        f"/api/v1/tenants/{test_user.tenant_id}/analytics/overview",
    )

    assert response.status_code == 401


def test_invalid_period_parameter(
    client: TestClient, db_session: Session, test_user: User
):
    """Test trends with invalid period parameter"""
    auth_service = AuthService()
    token = auth_service.create_access_token(
        {
            "sub": str(test_user.id),
            "tenant_id": str(test_user.tenant_id),
            "email": test_user.email,
        }
    )

    response = client.get(
        f"/api/v1/tenants/{test_user.tenant_id}/analytics/trends?period=invalid",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Should return 422 for validation error
    assert response.status_code == 422


def test_invalid_metric_parameter(
    client: TestClient, db_session: Session, test_user: User
):
    """Test trends with invalid metric parameter"""
    auth_service = AuthService()
    token = auth_service.create_access_token(
        {
            "sub": str(test_user.id),
            "tenant_id": str(test_user.tenant_id),
            "email": test_user.email,
        }
    )

    response = client.get(
        f"/api/v1/tenants/{test_user.tenant_id}/analytics/trends?metric=invalid",
        headers={"Authorization": f"Bearer {token}"},
    )

    # Should return 422 for validation error
    assert response.status_code == 422
