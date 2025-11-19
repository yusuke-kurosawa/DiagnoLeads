"""
Tests for Lead CRUD, Scoring, and Search Services

Comprehensive test coverage for leads submodules
"""

from uuid import uuid4

from app.models.lead import Lead
from app.schemas.lead import LeadUpdate
from app.services.leads.lead_crud import LeadCRUDService
from app.services.leads.lead_scoring import LeadScoringService
from app.services.leads.lead_search import LeadSearchService


class TestLeadCRUDService:
    """Tests for LeadCRUDService"""

    def test_list_by_tenant(self, db_session, test_tenant, test_user):
        """Test listing leads by tenant"""
        service = LeadCRUDService(db_session)

        # Create test leads
        lead1 = Lead(
            tenant_id=test_tenant.id,
            name="John Doe",
            email="john@example.com",
            score=80,
            status="new",
            created_by=test_user.id,
        )
        lead2 = Lead(
            tenant_id=test_tenant.id,
            name="Jane Smith",
            email="jane@example.com",
            score=60,
            status="qualified",
            created_by=test_user.id,
        )
        db_session.add_all([lead1, lead2])
        db_session.commit()

        leads = service.list_by_tenant(test_tenant.id)

        assert len(leads) == 2
        # Should be sorted by score descending
        assert leads[0].score >= leads[1].score

    def test_list_by_tenant_with_filters(self, db_session, test_tenant, test_user):
        """Test listing with filters"""
        service = LeadCRUDService(db_session)

        lead1 = Lead(
            tenant_id=test_tenant.id,
            name="High Score",
            email="high@example.com",
            score=90,
            status="new",
            created_by=test_user.id,
        )
        lead2 = Lead(
            tenant_id=test_tenant.id,
            name="Low Score",
            email="low@example.com",
            score=30,
            status="contacted",
            created_by=test_user.id,
        )
        db_session.add_all([lead1, lead2])
        db_session.commit()

        # Test status filter
        new_leads = service.list_by_tenant(test_tenant.id, status="new")
        assert len(new_leads) == 1
        assert new_leads[0].status == "new"

        # Test min_score filter
        high_score = service.list_by_tenant(test_tenant.id, min_score=50)
        assert len(high_score) == 1
        assert high_score[0].score >= 50

        # Test max_score filter
        low_score = service.list_by_tenant(test_tenant.id, max_score=50)
        assert len(low_score) == 1
        assert low_score[0].score <= 50

    def test_list_by_tenant_with_assigned_to(self, db_session, test_tenant, test_user):
        """Test listing with assigned_to filter"""
        service = LeadCRUDService(db_session)

        lead = Lead(
            tenant_id=test_tenant.id,
            name="Assigned Lead",
            email="assigned@example.com",
            score=75,
            status="new",
            assigned_to=test_user.id,
            created_by=test_user.id,
        )
        db_session.add(lead)
        db_session.commit()

        leads = service.list_by_tenant(test_tenant.id, assigned_to=test_user.id)
        assert len(leads) == 1
        assert leads[0].assigned_to == test_user.id

    def test_get_by_id(self, db_session, test_tenant, test_user):
        """Test getting lead by ID"""
        service = LeadCRUDService(db_session)

        lead = Lead(
            tenant_id=test_tenant.id,
            name="Test Lead",
            email="test@example.com",
            score=70,
            status="new",
            created_by=test_user.id,
        )
        db_session.add(lead)
        db_session.commit()

        retrieved = service.get_by_id(lead.id, test_tenant.id)
        assert retrieved is not None
        assert retrieved.id == lead.id

    def test_get_by_id_wrong_tenant(self, db_session, test_tenant, test_user):
        """Test tenant isolation in get_by_id"""
        service = LeadCRUDService(db_session)

        lead = Lead(
            tenant_id=test_tenant.id,
            name="Test Lead",
            email="test@example.com",
            score=70,
            status="new",
            created_by=test_user.id,
        )
        db_session.add(lead)
        db_session.commit()

        wrong_tenant_id = uuid4()
        retrieved = service.get_by_id(lead.id, wrong_tenant_id)
        assert retrieved is None

    def test_get_by_email(self, db_session, test_tenant, test_user):
        """Test getting lead by email"""
        service = LeadCRUDService(db_session)

        lead = Lead(
            tenant_id=test_tenant.id,
            name="Test Lead",
            email="unique@example.com",
            score=70,
            status="new",
            created_by=test_user.id,
        )
        db_session.add(lead)
        db_session.commit()

        retrieved = service.get_by_email("unique@example.com", test_tenant.id)
        assert retrieved is not None
        assert retrieved.email == "unique@example.com"

    def test_update(self, db_session, test_tenant, test_user):
        """Test updating a lead"""
        service = LeadCRUDService(db_session)

        lead = Lead(
            tenant_id=test_tenant.id,
            name="Old Name",
            email="old@example.com",
            score=50,
            status="new",
            created_by=test_user.id,
        )
        db_session.add(lead)
        db_session.commit()

        update_data = LeadUpdate(name="New Name", company="New Company")
        updated = service.update(lead.id, update_data, test_tenant.id, test_user.id)

        assert updated is not None
        assert updated.name == "New Name"
        assert updated.company == "New Company"
        assert updated.updated_by == test_user.id

    def test_delete(self, db_session, test_tenant, test_user):
        """Test deleting a lead"""
        service = LeadCRUDService(db_session)

        lead = Lead(
            tenant_id=test_tenant.id,
            name="To Delete",
            email="delete@example.com",
            score=60,
            status="new",
            created_by=test_user.id,
        )
        db_session.add(lead)
        db_session.commit()
        lead_id = lead.id

        result = service.delete(lead_id, test_tenant.id)
        assert result is True

        deleted = service.get_by_id(lead_id, test_tenant.id)
        assert deleted is None

    def test_count_by_tenant(self, db_session, test_tenant, test_user):
        """Test counting leads"""
        service = LeadCRUDService(db_session)

        for i in range(3):
            lead = Lead(
                tenant_id=test_tenant.id,
                name=f"Lead {i}",
                email=f"lead{i}@example.com",
                score=i * 20,
                status="new",
                created_by=test_user.id,
            )
            db_session.add(lead)
        db_session.commit()

        count = service.count_by_tenant(test_tenant.id)
        assert count == 3

        count_new = service.count_by_tenant(test_tenant.id, status="new")
        assert count_new == 3


class TestLeadScoringService:
    """Tests for LeadScoringService"""

    def test_get_hot_leads(self, db_session, test_tenant, test_user):
        """Test getting hot leads"""
        service = LeadScoringService(db_session)

        # Create leads with various scores
        lead1 = Lead(
            tenant_id=test_tenant.id,
            name="Hot Lead 1",
            email="hot1@example.com",
            score=85,
            status="new",
            created_by=test_user.id,
        )
        lead2 = Lead(
            tenant_id=test_tenant.id,
            name="Hot Lead 2",
            email="hot2@example.com",
            score=70,
            status="qualified",
            created_by=test_user.id,
        )
        lead3 = Lead(
            tenant_id=test_tenant.id,
            name="Cold Lead",
            email="cold@example.com",
            score=30,
            status="new",
            created_by=test_user.id,
        )
        db_session.add_all([lead1, lead2, lead3])
        db_session.commit()

        hot_leads = service.get_hot_leads(test_tenant.id, threshold=61)

        assert len(hot_leads) == 2
        assert all(lead.score >= 61 for lead in hot_leads)
        # Should be sorted by score descending
        assert hot_leads[0].score >= hot_leads[1].score

    def test_get_hot_leads_excludes_converted(self, db_session, test_tenant, test_user):
        """Test that converted leads are excluded from hot leads"""
        service = LeadScoringService(db_session)

        # Create high score converted lead
        converted_lead = Lead(
            tenant_id=test_tenant.id,
            name="Converted Lead",
            email="converted@example.com",
            score=95,
            status="converted",
            created_by=test_user.id,
        )
        # Create high score new lead
        new_lead = Lead(
            tenant_id=test_tenant.id,
            name="New Lead",
            email="new@example.com",
            score=85,
            status="new",
            created_by=test_user.id,
        )
        db_session.add_all([converted_lead, new_lead])
        db_session.commit()

        hot_leads = service.get_hot_leads(test_tenant.id)

        # Converted lead should not be included
        assert len(hot_leads) == 1
        assert hot_leads[0].status != "converted"


class TestLeadSearchService:
    """Tests for LeadSearchService"""

    def test_search_by_name(self, db_session, test_tenant, test_user):
        """Test searching leads by name"""
        service = LeadSearchService(db_session)

        lead = Lead(
            tenant_id=test_tenant.id,
            name="Alice Johnson",
            email="alice@example.com",
            score=80,
            status="new",
            created_by=test_user.id,
        )
        db_session.add(lead)
        db_session.commit()

        results = service.search(test_tenant.id, "Alice")

        assert len(results) == 1
        assert results[0].name == "Alice Johnson"

    def test_search_by_email(self, db_session, test_tenant, test_user):
        """Test searching leads by email"""
        service = LeadSearchService(db_session)

        lead = Lead(
            tenant_id=test_tenant.id,
            name="Test User",
            email="searchable@example.com",
            score=70,
            status="new",
            created_by=test_user.id,
        )
        db_session.add(lead)
        db_session.commit()

        results = service.search(test_tenant.id, "searchable")

        assert len(results) == 1
        assert results[0].email == "searchable@example.com"

    def test_search_by_company(self, db_session, test_tenant, test_user):
        """Test searching leads by company"""
        service = LeadSearchService(db_session)

        lead = Lead(
            tenant_id=test_tenant.id,
            name="Test User",
            email="user@example.com",
            company="ACME Corporation",
            score=70,
            status="new",
            created_by=test_user.id,
        )
        db_session.add(lead)
        db_session.commit()

        results = service.search(test_tenant.id, "ACME")

        assert len(results) == 1
        assert results[0].company == "ACME Corporation"

    def test_search_case_insensitive(self, db_session, test_tenant, test_user):
        """Test that search is case-insensitive"""
        service = LeadSearchService(db_session)

        lead = Lead(
            tenant_id=test_tenant.id,
            name="John Doe",
            email="john@example.com",
            score=70,
            status="new",
            created_by=test_user.id,
        )
        db_session.add(lead)
        db_session.commit()

        # Search with different case
        results = service.search(test_tenant.id, "JOHN")

        assert len(results) == 1
        assert results[0].name == "John Doe"

    def test_search_with_limit(self, db_session, test_tenant, test_user):
        """Test search respects limit"""
        service = LeadSearchService(db_session)

        # Create 5 leads with similar names
        for i in range(5):
            lead = Lead(
                tenant_id=test_tenant.id,
                name=f"Test User {i}",
                email=f"test{i}@example.com",
                score=70,
                status="new",
                created_by=test_user.id,
            )
            db_session.add(lead)
        db_session.commit()

        # Search with limit=3
        results = service.search(test_tenant.id, "Test", limit=3)

        assert len(results) == 3
