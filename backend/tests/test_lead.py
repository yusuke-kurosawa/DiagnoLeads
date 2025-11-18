"""
Lead API Tests

Comprehensive tests for Lead CRUD operations with multi-tenant isolation.
Following OpenSpec test strategy from openspec/specs/features/lead-management.md
"""

from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.lead import Lead
from app.models.user import User
from app.services.auth import AuthService


def test_create_lead(client: TestClient, db_session: Session, test_user: User):
    """Test creating a new lead"""
    auth_service = AuthService()
    token = auth_service.create_access_token({
        "sub": str(test_user.id),
        "tenant_id": str(test_user.tenant_id),
        "email": test_user.email,
    })
    
    lead_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "company": "Acme Corp",
        "job_title": "CTO",
        "phone": "+1-555-0100",
        "status": "new",
        "tags": ["enterprise", "tech"],
        "notes": "Met at conference",
    }
    
    response = client.post(
        f"/api/v1/tenants/{test_user.tenant_id}/leads",
        json=lead_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == lead_data["name"]
    assert data["email"] == lead_data["email"]
    assert data["company"] == lead_data["company"]
    assert data["job_title"] == lead_data["job_title"]
    assert data["phone"] == lead_data["phone"]
    assert data["status"] == "new"
    assert data["score"] == 0  # Initial score
    assert data["tags"] == lead_data["tags"]
    assert data["tenant_id"] == str(test_user.tenant_id)
    assert data["created_by"] == str(test_user.id)


def test_create_lead_duplicate_email(client: TestClient, db_session: Session, test_user: User):
    """Test creating a lead with duplicate email in same tenant"""
    auth_service = AuthService()
    token = auth_service.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})
    
    # Create first lead
    lead_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "status": "new",
    }
    
    response1 = client.post(
        f"/api/v1/tenants/{test_user.tenant_id}/leads",
        json=lead_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response1.status_code == 201
    
    # Try to create second lead with same email
    response2 = client.post(
        f"/api/v1/tenants/{test_user.tenant_id}/leads",
        json=lead_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"].lower()


def test_list_leads(client: TestClient, db_session: Session, test_user: User):
    """Test listing all leads for a tenant"""
    auth_service = AuthService()
    token = auth_service.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})
    
    # Create multiple leads
    for i in range(3):
        lead = Lead(
            name=f"Lead {i}",
            email=f"lead{i}@example.com",
            status="new",
            score=i * 20,
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            tags=[],
            custom_fields={},
        )
        db_session.add(lead)
    db_session.commit()
    
    response = client.get(
        f"/api/v1/tenants/{test_user.tenant_id}/leads",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    # Should be sorted by score (descending)
    assert data[0]["score"] >= data[1]["score"] >= data[2]["score"]


def test_list_leads_with_filters(client: TestClient, db_session: Session, test_user: User):
    """Test listing leads with status and score filters"""
    auth_service = AuthService()
    token = auth_service.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})
    
    # Create leads with different statuses and scores
    leads_data = [
        {"name": "Lead 1", "email": "lead1@example.com", "status": "new", "score": 20},
        {"name": "Lead 2", "email": "lead2@example.com", "status": "contacted", "score": 50},
        {"name": "Lead 3", "email": "lead3@example.com", "status": "qualified", "score": 80},
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
    
    # Filter by status
    response = client.get(
        f"/api/v1/tenants/{test_user.tenant_id}/leads?status=contacted",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "contacted"
    
    # Filter by score range
    response = client.get(
        f"/api/v1/tenants/{test_user.tenant_id}/leads?min_score=50&max_score=100",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(50 <= lead["score"] <= 100 for lead in data)


def test_get_lead(client: TestClient, db_session: Session, test_user: User):
    """Test getting a specific lead by ID"""
    auth_service = AuthService()
    token = auth_service.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})
    
    # Create a lead
    lead = Lead(
        name="John Doe",
        email="john.doe@example.com",
        company="Acme Corp",
        status="new",
        score=50,
        tenant_id=test_user.tenant_id,
        created_by=test_user.id,
        tags=["enterprise"],
        custom_fields={},
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    
    response = client.get(
        f"/api/v1/tenants/{test_user.tenant_id}/leads/{lead.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(lead.id)
    assert data["name"] == "John Doe"
    assert data["email"] == "john.doe@example.com"
    assert data["company"] == "Acme Corp"
    assert data["score"] == 50


def test_update_lead(client: TestClient, db_session: Session, test_user: User):
    """Test updating a lead"""
    auth_service = AuthService()
    token = auth_service.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})
    
    # Create a lead
    lead = Lead(
        name="John Doe",
        email="john.doe@example.com",
        status="new",
        tenant_id=test_user.tenant_id,
        created_by=test_user.id,
        tags=[],
        custom_fields={},
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    
    # Update the lead
    update_data = {
        "name": "John Smith",
        "company": "New Corp",
        "job_title": "CEO",
    }
    
    response = client.put(
        f"/api/v1/tenants/{test_user.tenant_id}/leads/{lead.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Smith"
    assert data["company"] == "New Corp"
    assert data["job_title"] == "CEO"
    assert data["email"] == "john.doe@example.com"  # Unchanged


def test_update_lead_status(client: TestClient, db_session: Session, test_user: User):
    """Test updating lead status"""
    auth_service = AuthService()
    token = auth_service.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})
    
    # Create a lead
    lead = Lead(
        name="John Doe",
        email="john.doe@example.com",
        status="new",
        tenant_id=test_user.tenant_id,
        created_by=test_user.id,
        tags=[],
        custom_fields={},
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    
    # Update status to contacted
    response = client.patch(
        f"/api/v1/tenants/{test_user.tenant_id}/leads/{lead.id}/status",
        json={"status": "contacted"},
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "contacted"
    assert data["last_contacted_at"] is not None


def test_update_lead_score(client: TestClient, db_session: Session, test_user: User):
    """Test updating lead score"""
    auth_service = AuthService()
    token = auth_service.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})
    
    # Create a lead
    lead = Lead(
        name="John Doe",
        email="john.doe@example.com",
        status="new",
        score=0,
        tenant_id=test_user.tenant_id,
        created_by=test_user.id,
        tags=[],
        custom_fields={},
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    
    # Update score
    response = client.patch(
        f"/api/v1/tenants/{test_user.tenant_id}/leads/{lead.id}/score",
        json={"score": 75, "reason": "Completed assessment"},
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 75


def test_delete_lead(client: TestClient, db_session: Session, test_user: User):
    """Test deleting a lead"""
    auth_service = AuthService()
    token = auth_service.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})
    
    # Create a lead
    lead = Lead(
        name="John Doe",
        email="john.doe@example.com",
        status="new",
        tenant_id=test_user.tenant_id,
        created_by=test_user.id,
        tags=[],
        custom_fields={},
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    lead_id = lead.id
    
    # Delete the lead
    response = client.delete(
        f"/api/v1/tenants/{test_user.tenant_id}/leads/{lead_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 204
    
    # Verify lead is deleted
    response = client.get(
        f"/api/v1/tenants/{test_user.tenant_id}/leads/{lead_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_search_leads(client: TestClient, db_session: Session, test_user: User):
    """Test searching leads by name, email, or company"""
    auth_service = AuthService()
    token = auth_service.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})
    
    # Create leads
    leads_data = [
        {"name": "John Doe", "email": "john@acme.com", "company": "Acme Corp"},
        {"name": "Jane Smith", "email": "jane@techco.com", "company": "TechCo"},
        {"name": "Bob Johnson", "email": "bob@acme.com", "company": "Acme Corp"},
    ]
    
    for lead_data in leads_data:
        lead = Lead(
            **lead_data,
            status="new",
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            tags=[],
            custom_fields={},
        )
        db_session.add(lead)
    db_session.commit()
    
    # Search by name
    response = client.get(
        f"/api/v1/tenants/{test_user.tenant_id}/leads/search?q=John",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any("John" in lead["name"] for lead in data)
    
    # Search by company
    response = client.get(
        f"/api/v1/tenants/{test_user.tenant_id}/leads/search?q=Acme",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all("Acme" in lead["company"] for lead in data)


def test_get_hot_leads(client: TestClient, db_session: Session, test_user: User):
    """Test getting hot leads (score >= 61)"""
    auth_service = AuthService()
    token = auth_service.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})
    
    # Create leads with different scores
    leads_data = [
        {"name": "Cold Lead", "email": "cold@example.com", "score": 20},
        {"name": "Warm Lead", "email": "warm@example.com", "score": 50},
        {"name": "Hot Lead 1", "email": "hot1@example.com", "score": 70},
        {"name": "Hot Lead 2", "email": "hot2@example.com", "score": 90},
    ]
    
    for lead_data in leads_data:
        lead = Lead(
            **lead_data,
            status="qualified",
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            tags=[],
            custom_fields={},
        )
        db_session.add(lead)
    db_session.commit()
    
    response = client.get(
        f"/api/v1/tenants/{test_user.tenant_id}/leads/hot",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(lead["score"] >= 61 for lead in data)
    # Should be sorted by score descending
    assert data[0]["score"] >= data[1]["score"]


def test_cross_tenant_access_denied(client: TestClient, db_session: Session, test_user: User, test_tenant_2):
    """Test that users cannot access leads from other tenants (CRITICAL SECURITY TEST)"""
    auth_service = AuthService()
    token = auth_service.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})
    
    # Create a lead in a different tenant
    other_lead = Lead(
        name="Other Tenant Lead",
        email="other@example.com",
        status="new",
        tenant_id=test_tenant_2.id,  # Different tenant
        created_by=test_user.id,
        tags=[],
        custom_fields={},
    )
    db_session.add(other_lead)
    db_session.commit()
    db_session.refresh(other_lead)
    
    # Try to access the other tenant's lead
    response = client.get(
        f"/api/v1/tenants/{test_tenant_2.id}/leads/{other_lead.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 403  # Forbidden


def test_lead_email_unique_per_tenant(client: TestClient, db_session: Session, test_user: User, test_tenant_2):
    """Test that email uniqueness is enforced per tenant, not globally"""
    auth_service = AuthService()
    token_user1 = auth_service.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})
    
    # Create a lead in tenant 1
    lead_data = {
        "name": "John Doe",
        "email": "same@example.com",
        "status": "new",
    }
    
    response1 = client.post(
        f"/api/v1/tenants/{test_user.tenant_id}/leads",
        json=lead_data,
        headers={"Authorization": f"Bearer {token_user1}"},
    )
    assert response1.status_code == 201
    
    # Create user in tenant 2
    from app.models.user import User
    user2 = User(
        name="Test User 2",
        email="user2@example.com",
        password_hash="hash",
        tenant_id=test_tenant_2.id,
    )
    db_session.add(user2)
    db_session.commit()
    db_session.refresh(user2)
    
    token_user2 = auth_service.create_access_token({"sub": str(user2.id), "tenant_id": str(user2.tenant_id), "email": user2.email})
    
    # Should be able to create lead with same email in tenant 2
    response2 = client.post(
        f"/api/v1/tenants/{test_tenant_2.id}/leads",
        json=lead_data,
        headers={"Authorization": f"Bearer {token_user2}"},
    )
    assert response2.status_code == 201  # Should succeed


def test_invalid_status_transition(client: TestClient, db_session: Session, test_user: User):
    """Test that invalid status transitions are prevented"""
    auth_service = AuthService()
    token = auth_service.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})
    
    # Create a converted lead
    lead = Lead(
        name="John Doe",
        email="john@example.com",
        status="converted",  # Already converted
        tenant_id=test_user.tenant_id,
        created_by=test_user.id,
        tags=[],
        custom_fields={},
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    
    # Try to change status from converted to new (should fail)
    response = client.patch(
        f"/api/v1/tenants/{test_user.tenant_id}/leads/{lead.id}/status",
        json={"status": "new"},
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 400
    assert "converted" in response.json()["detail"].lower()


def test_get_nonexistent_lead(client: TestClient, test_user: User):
    """Test getting a non-existent lead returns 404"""
    auth_service = AuthService()
    token = auth_service.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})
    
    fake_id = uuid4()
    response = client.get(
        f"/api/v1/tenants/{test_user.tenant_id}/leads/{fake_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 404


def test_unauthorized_access(client: TestClient, test_user: User):
    """Test that unauthenticated requests are rejected"""
    response = client.get(
        f"/api/v1/tenants/{test_user.tenant_id}/leads"
    )
    
    assert response.status_code in [401, 403]
