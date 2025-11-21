"""
Tests for Taxonomy API Endpoints

Test coverage for Topics and Industries API endpoints.
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.industry import Industry
from app.models.topic import Topic
from app.models.user import User
from app.services.auth import AuthService


class TestTopicsAPI:
    """Tests for Topics API endpoints"""

    def test_get_topics(self, client: TestClient, db_session: Session, test_user: User):
        """Test getting all topics for a tenant"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create test topics
        topic1 = Topic(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="Technology",
            description="Tech topics",
        )
        topic2 = Topic(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="Business",
            description="Business topics",
        )
        db_session.add_all([topic1, topic2])
        db_session.commit()

        response = client.get(
            f"/api/v1/tenants/{test_user.tenant_id}/topics",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] in ["Technology", "Business"]

    def test_get_topic_by_id(self, client: TestClient, db_session: Session, test_user: User):
        """Test getting a specific topic"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create test topic
        topic = Topic(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="Technology",
            description="Tech topics",
        )
        db_session.add(topic)
        db_session.commit()
        db_session.refresh(topic)

        response = client.get(
            f"/api/v1/tenants/{test_user.tenant_id}/topics/{topic.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Technology"
        assert data["description"] == "Tech topics"

    def test_get_topic_not_found(self, client: TestClient, test_user: User):
        """Test getting non-existent topic"""
        from uuid import uuid4

        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        response = client.get(
            f"/api/v1/tenants/{test_user.tenant_id}/topics/{uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_topic(self, client: TestClient, test_user: User):
        """Test creating a new topic"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        topic_data = {
            "name": "Marketing",
            "description": "Marketing strategies",
            "color": "#FF5733",
            "icon": "🎯",
        }

        response = client.post(
            f"/api/v1/tenants/{test_user.tenant_id}/topics",
            json=topic_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Marketing"
        assert data["description"] == "Marketing strategies"
        assert data["color"] == "#FF5733"

    def test_update_topic(self, client: TestClient, db_session: Session, test_user: User):
        """Test updating a topic"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create topic
        topic = Topic(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="Old Name",
            description="Old description",
        )
        db_session.add(topic)
        db_session.commit()
        db_session.refresh(topic)

        update_data = {"name": "New Name", "description": "New description"}

        response = client.put(
            f"/api/v1/tenants/{test_user.tenant_id}/topics/{topic.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["description"] == "New description"

    def test_delete_topic(self, client: TestClient, db_session: Session, test_user: User):
        """Test deleting a topic"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create topic
        topic = Topic(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="To Delete",
            description="Will be deleted",
        )
        db_session.add(topic)
        db_session.commit()
        db_session.refresh(topic)

        response = client.delete(
            f"/api/v1/tenants/{test_user.tenant_id}/topics/{topic.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 204

        # Verify deleted
        deleted = db_session.query(Topic).filter(Topic.id == topic.id).first()
        assert deleted is None


class TestIndustriesAPI:
    """Tests for Industries API endpoints"""

    def test_get_industries(self, client: TestClient, db_session: Session, test_user: User):
        """Test getting all industries for a tenant"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create test industries
        industry1 = Industry(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="Healthcare",
            description="Healthcare industry",
        )
        industry2 = Industry(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="Finance",
            description="Finance industry",
        )
        db_session.add_all([industry1, industry2])
        db_session.commit()

        response = client.get(
            f"/api/v1/tenants/{test_user.tenant_id}/industries",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_create_industry(self, client: TestClient, test_user: User):
        """Test creating a new industry"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        industry_data = {
            "name": "Retail",
            "description": "Retail industry",
            "color": "#00FF00",
            "icon": "🛒",
        }

        response = client.post(
            f"/api/v1/tenants/{test_user.tenant_id}/industries",
            json=industry_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Retail"

    def test_update_industry(self, client: TestClient, db_session: Session, test_user: User):
        """Test updating an industry"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create industry
        industry = Industry(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="Old Industry",
            description="Old description",
        )
        db_session.add(industry)
        db_session.commit()
        db_session.refresh(industry)

        update_data = {"name": "Updated Industry"}

        response = client.put(
            f"/api/v1/tenants/{test_user.tenant_id}/industries/{industry.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Industry"

    def test_delete_industry(self, client: TestClient, db_session: Session, test_user: User):
        """Test deleting an industry"""
        token = AuthService.create_access_token({"sub": str(test_user.id), "tenant_id": str(test_user.tenant_id), "email": test_user.email})

        # Create industry
        industry = Industry(
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
            name="To Delete",
            description="Will be deleted",
        )
        db_session.add(industry)
        db_session.commit()
        db_session.refresh(industry)

        response = client.delete(
            f"/api/v1/tenants/{test_user.tenant_id}/industries/{industry.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 204

        # Verify deleted
        deleted = db_session.query(Industry).filter(Industry.id == industry.id).first()
        assert deleted is None
