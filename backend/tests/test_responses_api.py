"""
Tests for Response API Endpoints

Public API endpoints for assessment responses (embed widget).
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.models.user import User


class TestPublicAssessmentAPI:
    """Tests for public assessment endpoint"""

    def test_get_published_assessment(self, client: TestClient, db_session: Session, test_user: User):
        """Test getting a published assessment (no auth required)"""
        # Create published assessment
        assessment = Assessment(
            title="Public Assessment",
            description="Public description",
            status="published",
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
        )
        db_session.add(assessment)
        db_session.commit()
        db_session.refresh(assessment)

        # Create question
        question = Question(
            assessment_id=assessment.id,
            text="What is your goal?",
            type="multiple_choice",
            order=1,
        )
        db_session.add(question)
        db_session.commit()
        db_session.refresh(question)

        # Create options
        option1 = QuestionOption(
            question_id=question.id,
            text="Option 1",
            points=10,
            order=1,
        )
        option2 = QuestionOption(
            question_id=question.id,
            text="Option 2",
            points=20,
            order=2,
        )
        db_session.add_all([option1, option2])
        db_session.commit()

        # Call public endpoint (no auth)
        response = client.get(f"/api/v1/tenants/{test_user.tenant_id}/assessments/{assessment.id}/public")

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Public Assessment"
        assert data["description"] == "Public description"
        assert len(data["questions"]) == 1
        assert data["questions"][0]["text"] == "What is your goal?"
        assert len(data["questions"][0]["options"]) == 2

    def test_get_draft_assessment_not_found(self, client: TestClient, db_session: Session, test_user: User):
        """Test that draft assessments are not publicly accessible"""
        # Create draft assessment
        assessment = Assessment(
            title="Draft Assessment",
            description="Draft description",
            status="draft",
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
        )
        db_session.add(assessment)
        db_session.commit()
        db_session.refresh(assessment)

        # Try to access (should fail)
        response = client.get(f"/api/v1/tenants/{test_user.tenant_id}/assessments/{assessment.id}/public")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_nonexistent_assessment(self, client: TestClient, test_user: User):
        """Test getting non-existent assessment"""
        from uuid import uuid4

        response = client.get(f"/api/v1/tenants/{test_user.tenant_id}/assessments/{uuid4()}/public")

        assert response.status_code == 404


class TestResponseSessionAPI:
    """Tests for response session creation"""

    def test_create_response_session(self, client: TestClient, db_session: Session, test_user: User):
        """Test creating a new response session"""
        # Create assessment
        assessment = Assessment(
            title="Test Assessment",
            description="Test",
            status="published",
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
        )
        db_session.add(assessment)
        db_session.commit()
        db_session.refresh(assessment)

        # Create response session (public endpoint)
        response = client.post(
            "/api/v1/responses",
            params={"assessment_id": str(assessment.id)},
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] == "in_progress"
        assert "session_id" in data

    def test_create_response_for_nonexistent_assessment(self, client: TestClient):
        """Test creating response for non-existent assessment"""
        from uuid import uuid4

        response = client.post(
            "/api/v1/responses",
            params={"assessment_id": str(uuid4())},
        )

        assert response.status_code == 404
