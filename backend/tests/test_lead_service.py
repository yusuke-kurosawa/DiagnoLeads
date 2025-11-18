"""
Tests for Lead Service

Comprehensive test coverage for lead_service.py
Target: 80%+ coverage
"""

import pytest
from uuid import uuid4
from fastapi import HTTPException

from app.services.lead_service import LeadService
from app.schemas.lead import LeadCreate, LeadUpdate, LeadStatusUpdate, LeadScoreUpdate
from app.models.lead import Lead


class TestLeadServiceList:
    """Tests for list_by_tenant method"""

    def test_list_by_tenant_basic(self, db_session, test_tenant, test_user):
        """Test basic lead listing by tenant"""
        service = LeadService(db_session)
        
        # Create test leads
        lead1 = Lead(
            tenant_id=test_tenant.id,
            name="John Doe",
            email="john@example.com",
            score=80,
            status="new",
            created_by=test_user.id
        )
        lead2 = Lead(
            tenant_id=test_tenant.id,
            name="Jane Smith",
            email="jane@example.com",
            score=60,
            status="qualified",
            created_by=test_user.id
        )
        db_session.add_all([lead1, lead2])
        db_session.commit()

        # Test listing
        leads = service.list_by_tenant(tenant_id=test_tenant.id)
        
        assert len(leads) == 2
        assert leads[0].score >= leads[1].score  # Check sorting by score desc

    def test_list_by_tenant_with_filters(self, db_session, test_tenant, test_user):
        """Test lead listing with filters"""
        service = LeadService(db_session)
        
        # Create test leads with different attributes
        lead1 = Lead(
            tenant_id=test_tenant.id,
            name="High Score Lead",
            email="high@example.com",
            score=90,
            status="new",
            created_by=test_user.id
        )
        lead2 = Lead(
            tenant_id=test_tenant.id,
            name="Low Score Lead",
            email="low@example.com",
            score=30,
            status="contacted",
            created_by=test_user.id
        )
        db_session.add_all([lead1, lead2])
        db_session.commit()

        # Test status filter
        new_leads = service.list_by_tenant(tenant_id=test_tenant.id, status="new")
        assert len(new_leads) == 1
        assert new_leads[0].email == "high@example.com"

        # Test score filter
        high_score_leads = service.list_by_tenant(
            tenant_id=test_tenant.id, 
            min_score=50
        )
        assert len(high_score_leads) == 1
        assert high_score_leads[0].score == 90

    def test_list_by_tenant_pagination(self, db_session, test_tenant, test_user):
        """Test pagination"""
        service = LeadService(db_session)
        
        # Create 5 test leads
        for i in range(5):
            lead = Lead(
                tenant_id=test_tenant.id,
                name=f"Lead {i}",
                email=f"lead{i}@example.com",
                score=i * 10,
                status="new",
                created_by=test_user.id
            )
            db_session.add(lead)
        db_session.commit()

        # Test pagination
        page1 = service.list_by_tenant(tenant_id=test_tenant.id, skip=0, limit=2)
        page2 = service.list_by_tenant(tenant_id=test_tenant.id, skip=2, limit=2)
        
        assert len(page1) == 2
        assert len(page2) == 2
        assert page1[0].id != page2[0].id

    def test_list_by_tenant_isolation(self, db_session, test_tenant, test_tenant_2, test_user):
        """Test tenant isolation - should not see other tenant's leads"""
        service = LeadService(db_session)
        
        # Create leads for different tenants
        lead1 = Lead(
            tenant_id=test_tenant.id,
            name="Our Lead",
            email="our@example.com",
            score=80,
            status="new",
            created_by=test_user.id
        )
        lead2 = Lead(
            tenant_id=test_tenant_2.id,  # Use test_tenant_2 instead of random UUID
            name="Other Lead",
            email="other@example.com",
            score=90,
            status="new",
            created_by=test_user.id
        )
        db_session.add_all([lead1, lead2])
        db_session.commit()

        # Should only see our tenant's leads
        leads = service.list_by_tenant(tenant_id=test_tenant.id)
        
        assert len(leads) == 1
        assert leads[0].email == "our@example.com"


class TestLeadServiceGet:
    """Tests for get methods"""

    def test_get_by_id_success(self, db_session, test_tenant, test_user):
        """Test getting lead by ID"""
        service = LeadService(db_session)
        
        lead = Lead(
            tenant_id=test_tenant.id,
            name="Test Lead",
            email="test@example.com",
            score=70,
            status="new",
            created_by=test_user.id
        )
        db_session.add(lead)
        db_session.commit()

        retrieved = service.get_by_id(lead_id=lead.id, tenant_id=test_tenant.id)
        
        assert retrieved is not None
        assert retrieved.id == lead.id
        assert retrieved.email == "test@example.com"

    def test_get_by_id_wrong_tenant(self, db_session, test_tenant, test_user):
        """Test tenant isolation in get_by_id"""
        service = LeadService(db_session)
        
        lead = Lead(
            tenant_id=test_tenant.id,
            name="Test Lead",
            email="test@example.com",
            score=70,
            status="new",
            created_by=test_user.id
        )
        db_session.add(lead)
        db_session.commit()

        # Try to get with wrong tenant_id
        wrong_tenant_id = uuid4()
        retrieved = service.get_by_id(lead_id=lead.id, tenant_id=wrong_tenant_id)
        
        assert retrieved is None

    def test_get_by_email_success(self, db_session, test_tenant, test_user):
        """Test getting lead by email"""
        service = LeadService(db_session)
        
        lead = Lead(
            tenant_id=test_tenant.id,
            name="Test Lead",
            email="unique@example.com",
            score=70,
            status="new",
            created_by=test_user.id
        )
        db_session.add(lead)
        db_session.commit()

        retrieved = service.get_by_email(email="unique@example.com", tenant_id=test_tenant.id)
        
        assert retrieved is not None
        assert retrieved.email == "unique@example.com"


class TestLeadServiceCreate:
    """Tests for create method"""

    def test_create_lead_success(self, db_session, test_tenant, test_user):
        """Test successful lead creation"""
        service = LeadService(db_session)
        
        lead_data = LeadCreate(
            name="New Lead",
            email="new@example.com",
            company="ACME Corp",
            phone="+1234567890",
            status="new"
        )

        lead = service.create(
            data=lead_data,
            tenant_id=test_tenant.id,
            created_by=test_user.id
        )

        assert lead.id is not None
        assert lead.name == "New Lead"
        assert lead.email == "new@example.com"
        assert lead.tenant_id == test_tenant.id
        assert lead.score == 0  # Initial score

    def test_create_lead_duplicate_email(self, db_session, test_tenant, test_user):
        """Test creating lead with duplicate email in same tenant"""
        service = LeadService(db_session)
        
        # Create first lead
        lead_data = LeadCreate(
            name="First Lead",
            email="duplicate@example.com",
            status="new"
        )
        service.create(data=lead_data, tenant_id=test_tenant.id, created_by=test_user.id)

        # Try to create second lead with same email
        lead_data2 = LeadCreate(
            name="Second Lead",
            email="duplicate@example.com",
            status="new"
        )

        with pytest.raises(HTTPException) as exc_info:
            service.create(data=lead_data2, tenant_id=test_tenant.id, created_by=test_user.id)
        
        assert exc_info.value.status_code == 400
        assert "already exists" in str(exc_info.value.detail)


class TestLeadServiceUpdate:
    """Tests for update methods"""

    def test_update_lead_success(self, db_session, test_tenant, test_user):
        """Test successful lead update"""
        service = LeadService(db_session)
        
        # Create lead
        lead = Lead(
            tenant_id=test_tenant.id,
            name="Old Name",
            email="old@example.com",
            score=50,
            status="new",
            created_by=test_user.id
        )
        db_session.add(lead)
        db_session.commit()

        # Update lead
        update_data = LeadUpdate(name="New Name", company="New Company")
        updated_lead = service.update(
            lead_id=lead.id,
            data=update_data,
            tenant_id=test_tenant.id,
            updated_by=test_user.id
        )

        assert updated_lead.name == "New Name"
        assert updated_lead.company == "New Company"
        assert updated_lead.email == "old@example.com"  # Unchanged

    def test_update_status_success(self, db_session, test_tenant, test_user):
        """Test status update"""
        service = LeadService(db_session)
        
        lead = Lead(
            tenant_id=test_tenant.id,
            name="Test Lead",
            email="test@example.com",
            score=70,
            status="new",
            created_by=test_user.id
        )
        db_session.add(lead)
        db_session.commit()

        # Update status
        status_update = LeadStatusUpdate(status="contacted")
        updated = service.update_status(
            lead_id=lead.id,
            data=status_update,
            tenant_id=test_tenant.id,
            updated_by=test_user.id
        )

        assert updated.status == "contacted"
        assert updated.last_contacted_at is not None

    def test_update_status_from_converted_fails(self, db_session, test_tenant, test_user):
        """Test that converted status cannot be changed"""
        service = LeadService(db_session)
        
        lead = Lead(
            tenant_id=test_tenant.id,
            name="Converted Lead",
            email="converted@example.com",
            score=90,
            status="converted",
            created_by=test_user.id
        )
        db_session.add(lead)
        db_session.commit()

        # Try to change status from converted
        status_update = LeadStatusUpdate(status="qualified")
        
        with pytest.raises(HTTPException) as exc_info:
            service.update_status(
                lead_id=lead.id,
                data=status_update,
                tenant_id=test_tenant.id,
                updated_by=test_user.id
            )
        
        assert exc_info.value.status_code == 400
        assert "converted" in str(exc_info.value.detail)

    def test_update_score(self, db_session, test_tenant, test_user):
        """Test score update"""
        service = LeadService(db_session)
        
        lead = Lead(
            tenant_id=test_tenant.id,
            name="Test Lead",
            email="test@example.com",
            score=50,
            status="new",
            created_by=test_user.id
        )
        db_session.add(lead)
        db_session.commit()

        # Update score
        score_update = LeadScoreUpdate(score=85)
        updated = service.update_score(
            lead_id=lead.id,
            data=score_update,
            tenant_id=test_tenant.id
        )

        assert updated.score == 85


class TestLeadServiceDelete:
    """Tests for delete method"""

    def test_delete_lead_success(self, db_session, test_tenant, test_user):
        """Test successful lead deletion"""
        service = LeadService(db_session)
        
        lead = Lead(
            tenant_id=test_tenant.id,
            name="To Delete",
            email="delete@example.com",
            score=60,
            status="new",
            created_by=test_user.id
        )
        db_session.add(lead)
        db_session.commit()
        lead_id = lead.id

        # Delete
        result = service.delete(lead_id=lead_id, tenant_id=test_tenant.id)
        
        assert result is True
        
        # Verify deletion
        deleted = service.get_by_id(lead_id=lead_id, tenant_id=test_tenant.id)
        assert deleted is None

    def test_delete_nonexistent_lead(self, db_session, test_tenant):
        """Test deleting non-existent lead"""
        service = LeadService(db_session)
        
        result = service.delete(lead_id=uuid4(), tenant_id=test_tenant.id)
        
        assert result is False


class TestLeadServiceSearch:
    """Tests for search and count methods"""

    def test_search_by_name(self, db_session, test_tenant, test_user):
        """Test searching leads by name"""
        service = LeadService(db_session)
        
        # Create test leads
        lead1 = Lead(
            tenant_id=test_tenant.id,
            name="Alice Johnson",
            email="alice@example.com",
            score=80,
            status="new",
            created_by=test_user.id
        )
        lead2 = Lead(
            tenant_id=test_tenant.id,
            name="Bob Smith",
            email="bob@example.com",
            score=60,
            status="new",
            created_by=test_user.id
        )
        db_session.add_all([lead1, lead2])
        db_session.commit()

        # Search by name
        results = service.search(tenant_id=test_tenant.id, query="Alice")
        
        assert len(results) == 1
        assert results[0].name == "Alice Johnson"

    def test_search_by_email(self, db_session, test_tenant, test_user):
        """Test searching leads by email"""
        service = LeadService(db_session)
        
        lead = Lead(
            tenant_id=test_tenant.id,
            name="Test Lead",
            email="searchable@example.com",
            score=70,
            status="new",
            created_by=test_user.id
        )
        db_session.add(lead)
        db_session.commit()

        # Search by email
        results = service.search(tenant_id=test_tenant.id, query="searchable")
        
        assert len(results) == 1
        assert results[0].email == "searchable@example.com"

    def test_count_by_tenant(self, db_session, test_tenant, test_user):
        """Test counting leads"""
        service = LeadService(db_session)
        
        # Create test leads
        for i in range(3):
            lead = Lead(
                tenant_id=test_tenant.id,
                name=f"Lead {i}",
                email=f"lead{i}@example.com",
                score=i * 20,
                status="new",
                created_by=test_user.id
            )
            db_session.add(lead)
        db_session.commit()

        # Count all
        count = service.count_by_tenant(tenant_id=test_tenant.id)
        assert count == 3

        # Count by status
        count_new = service.count_by_tenant(tenant_id=test_tenant.id, status="new")
        assert count_new == 3

    def test_get_hot_leads(self, db_session, test_tenant, test_user):
        """Test getting hot leads"""
        service = LeadService(db_session)
        
        # Create leads with various scores
        lead1 = Lead(
            tenant_id=test_tenant.id,
            name="Hot Lead 1",
            email="hot1@example.com",
            score=85,
            status="new",
            created_by=test_user.id
        )
        lead2 = Lead(
            tenant_id=test_tenant.id,
            name="Hot Lead 2",
            email="hot2@example.com",
            score=70,
            status="qualified",
            created_by=test_user.id
        )
        lead3 = Lead(
            tenant_id=test_tenant.id,
            name="Cold Lead",
            email="cold@example.com",
            score=30,
            status="new",
            created_by=test_user.id
        )
        db_session.add_all([lead1, lead2, lead3])
        db_session.commit()

        # Get hot leads (threshold=61)
        hot_leads = service.get_hot_leads(tenant_id=test_tenant.id, threshold=61)
        
        assert len(hot_leads) == 2
        assert all(lead.score >= 61 for lead in hot_leads)
        assert hot_leads[0].score >= hot_leads[1].score  # Sorted by score desc
