"""
Tests for Response API Endpoints

Public API endpoints for assessment responses (embed widget).
"""

from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.lead import Lead
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.models.response import Response
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
        response = client.post(
            "/api/v1/responses",
            params={"assessment_id": str(uuid4())},
        )

        assert response.status_code == 404


class TestSubmitAnswersAPI:
    """Tests for submitting answers to response"""

    def test_submit_single_answer(self, client: TestClient, db_session: Session, test_user: User):
        """Test submitting a single answer"""
        # Create assessment and question
        assessment = Assessment(
            title="Test Assessment",
            status="published",
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
        )
        db_session.add(assessment)
        db_session.commit()
        db_session.refresh(assessment)

        question = Question(
            assessment_id=assessment.id,
            text="Question 1?",
            type="multiple_choice",
            order=1,
        )
        db_session.add(question)
        db_session.commit()
        db_session.refresh(question)

        # Create response session
        response_obj = Response(
            assessment_id=assessment.id,
            session_id=str(uuid4()),
            status="in_progress",
        )
        db_session.add(response_obj)
        db_session.commit()
        db_session.refresh(response_obj)

        # Submit answer
        payload = {
            "answers": [
                {
                    "question_id": str(question.id),
                    "answer_text": "Option A",
                    "points_awarded": 10,
                }
            ]
        }

        response = client.post(
            f"/api/v1/responses/{response_obj.id}/answers",
            json=payload,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_score"] == 10
        assert data["status"] == "in_progress"

    def test_submit_multiple_answers(self, client: TestClient, db_session: Session, test_user: User):
        """Test submitting multiple answers at once"""
        # Create assessment
        assessment = Assessment(
            title="Test",
            status="published",
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
        )
        db_session.add(assessment)
        db_session.commit()
        db_session.refresh(assessment)

        # Create questions
        q1 = Question(assessment_id=assessment.id, text="Q1?", type="multiple_choice", order=1)
        q2 = Question(assessment_id=assessment.id, text="Q2?", type="multiple_choice", order=2)
        db_session.add_all([q1, q2])
        db_session.commit()
        db_session.refresh(q1)
        db_session.refresh(q2)

        # Create response
        response_obj = Response(
            assessment_id=assessment.id,
            session_id=str(uuid4()),
            status="in_progress",
        )
        db_session.add(response_obj)
        db_session.commit()
        db_session.refresh(response_obj)

        # Submit multiple answers
        payload = {
            "answers": [
                {"question_id": str(q1.id), "answer_text": "A", "points_awarded": 10},
                {"question_id": str(q2.id), "answer_text": "B", "points_awarded": 20},
            ]
        }

        response = client.post(f"/api/v1/responses/{response_obj.id}/answers", json=payload)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_score"] == 30

    def test_update_existing_answer(self, client: TestClient, db_session: Session, test_user: User):
        """Test updating an existing answer"""
        # Create assessment and question
        assessment = Assessment(
            title="Test",
            status="published",
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
        )
        db_session.add(assessment)
        db_session.commit()
        db_session.refresh(assessment)

        question = Question(assessment_id=assessment.id, text="Q?", type="multiple_choice", order=1)
        db_session.add(question)
        db_session.commit()
        db_session.refresh(question)

        # Create response
        response_obj = Response(
            assessment_id=assessment.id,
            session_id=str(uuid4()),
            status="in_progress",
        )
        db_session.add(response_obj)
        db_session.commit()
        db_session.refresh(response_obj)

        # Submit initial answer
        payload = {"answers": [{"question_id": str(question.id), "answer_text": "Option A", "points_awarded": 10}]}
        client.post(f"/api/v1/responses/{response_obj.id}/answers", json=payload)

        # Update answer
        updated_payload = {"answers": [{"question_id": str(question.id), "answer_text": "Option B", "points_awarded": 20}]}
        response = client.post(f"/api/v1/responses/{response_obj.id}/answers", json=updated_payload)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_score"] == 20  # Score should be updated

    def test_submit_answer_with_email_and_name(self, client: TestClient, db_session: Session, test_user: User):
        """Test submitting answer with email and name"""
        # Create assessment and question
        assessment = Assessment(
            title="Test",
            status="published",
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
        )
        db_session.add(assessment)
        db_session.commit()
        db_session.refresh(assessment)

        question = Question(assessment_id=assessment.id, text="Q?", type="multiple_choice", order=1)
        db_session.add(question)
        db_session.commit()
        db_session.refresh(question)

        # Create response
        response_obj = Response(
            assessment_id=assessment.id,
            session_id=str(uuid4()),
            status="in_progress",
        )
        db_session.add(response_obj)
        db_session.commit()
        db_session.refresh(response_obj)

        # Submit answer with contact info
        payload = {
            "answers": [{"question_id": str(question.id), "answer_text": "A", "points_awarded": 10}],
            "email": "test@example.com",
            "name": "Test User",
        }

        response = client.post(f"/api/v1/responses/{response_obj.id}/answers", json=payload)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"

    def test_submit_to_nonexistent_response(self, client: TestClient):
        """Test submitting answer to non-existent response"""
        payload = {"answers": [{"question_id": str(uuid4()), "answer_text": "A", "points_awarded": 10}]}

        response = client.post(f"/api/v1/responses/{uuid4()}/answers", json=payload)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_submit_to_completed_response(self, client: TestClient, db_session: Session, test_user: User):
        """Test that submitting to completed response fails"""
        # Create assessment and question
        assessment = Assessment(
            title="Test",
            status="published",
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
        )
        db_session.add(assessment)
        db_session.commit()
        db_session.refresh(assessment)

        question = Question(assessment_id=assessment.id, text="Q?", type="multiple_choice", order=1)
        db_session.add(question)
        db_session.commit()
        db_session.refresh(question)

        # Create completed response
        response_obj = Response(
            assessment_id=assessment.id,
            session_id=str(uuid4()),
            status="completed",  # Already completed
        )
        db_session.add(response_obj)
        db_session.commit()
        db_session.refresh(response_obj)

        # Try to submit answer
        payload = {"answers": [{"question_id": str(question.id), "answer_text": "A", "points_awarded": 10}]}

        response = client.post(f"/api/v1/responses/{response_obj.id}/answers", json=payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already completed" in response.json()["detail"].lower()


class TestCompleteResponseAPI:
    """Tests for completing responses and creating leads"""

    def test_complete_response_with_lead_creation(self, client: TestClient, db_session: Session, test_user: User):
        """Test completing response and creating new lead"""
        # Create assessment and question
        assessment = Assessment(
            title="Test",
            status="published",
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
        )
        db_session.add(assessment)
        db_session.commit()
        db_session.refresh(assessment)

        question = Question(assessment_id=assessment.id, text="Q?", type="multiple_choice", order=1)
        db_session.add(question)
        db_session.commit()
        db_session.refresh(question)

        # Create response
        response_obj = Response(
            assessment_id=assessment.id,
            session_id=str(uuid4()),
            status="in_progress",
        )
        db_session.add(response_obj)
        db_session.commit()
        db_session.refresh(response_obj)

        # Complete with lead data
        payload = {
            "answers": [{"question_id": str(question.id), "answer_text": "A", "points_awarded": 85}],
            "email": "newlead@example.com",
            "name": "New Lead",
            "company": "Test Company",
            "job_title": "Manager",
            "phone": "+1234567890",
        }

        response = client.post(f"/api/v1/responses/{response_obj.id}/complete", json=payload)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "completed"
        assert data["total_score"] == 85
        assert data["completed_at"] is not None

        # Verify lead was created
        lead = db_session.query(Lead).filter(Lead.email == "newlead@example.com").first()
        assert lead is not None
        assert lead.name == "New Lead"
        assert lead.company == "Test Company"
        assert lead.score == 85

    def test_complete_response_update_existing_lead(self, client: TestClient, db_session: Session, test_user: User):
        """Test completing response updates existing lead with higher score"""
        # Create assessment
        assessment = Assessment(
            title="Test",
            status="published",
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
        )
        db_session.add(assessment)
        db_session.commit()
        db_session.refresh(assessment)

        question = Question(assessment_id=assessment.id, text="Q?", type="multiple_choice", order=1)
        db_session.add(question)
        db_session.commit()
        db_session.refresh(question)

        # Create existing lead with lower score
        existing_lead = Lead(
            tenant_id=test_user.tenant_id,
            email="existing@example.com",
            name="Existing Lead",
            score=50,
            status="new",
            created_by=test_user.id,
        )
        db_session.add(existing_lead)
        db_session.commit()

        # Create response
        response_obj = Response(
            assessment_id=assessment.id,
            session_id=str(uuid4()),
            status="in_progress",
        )
        db_session.add(response_obj)
        db_session.commit()
        db_session.refresh(response_obj)

        # Complete with higher score
        payload = {
            "answers": [{"question_id": str(question.id), "answer_text": "A", "points_awarded": 90}],
            "email": "existing@example.com",
            "name": "Existing Lead Updated",
            "company": "Updated Company",
        }

        response = client.post(f"/api/v1/responses/{response_obj.id}/complete", json=payload)

        assert response.status_code == status.HTTP_200_OK

        # Verify lead was updated
        db_session.refresh(existing_lead)
        assert existing_lead.score == 90  # Score should be updated to max
        assert existing_lead.company == "Updated Company"

    def test_complete_response_without_lead_data(self, client: TestClient, db_session: Session, test_user: User):
        """Test completing response without creating lead"""
        # Create assessment and question
        assessment = Assessment(
            title="Test",
            status="published",
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
        )
        db_session.add(assessment)
        db_session.commit()
        db_session.refresh(assessment)

        question = Question(assessment_id=assessment.id, text="Q?", type="multiple_choice", order=1)
        db_session.add(question)
        db_session.commit()
        db_session.refresh(question)

        # Create response
        response_obj = Response(
            assessment_id=assessment.id,
            session_id=str(uuid4()),
            status="in_progress",
        )
        db_session.add(response_obj)
        db_session.commit()
        db_session.refresh(response_obj)

        # Complete without lead data
        payload = {"answers": [{"question_id": str(question.id), "answer_text": "A", "points_awarded": 50}]}

        response = client.post(f"/api/v1/responses/{response_obj.id}/complete", json=payload)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "completed"

        # Verify no lead was created
        lead_count = db_session.query(Lead).count()
        assert lead_count == 0

    def test_complete_nonexistent_response(self, client: TestClient):
        """Test completing non-existent response"""
        payload = {
            "answers": [],
            "email": "test@example.com",
            "name": "Test",
        }

        response = client.post(f"/api/v1/responses/{uuid4()}/complete", json=payload)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_complete_already_completed_response(self, client: TestClient, db_session: Session, test_user: User):
        """Test that completing already completed response fails"""
        # Create assessment
        assessment = Assessment(
            title="Test",
            status="published",
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
        )
        db_session.add(assessment)
        db_session.commit()
        db_session.refresh(assessment)

        # Create completed response
        response_obj = Response(
            assessment_id=assessment.id,
            session_id=str(uuid4()),
            status="completed",
        )
        db_session.add(response_obj)
        db_session.commit()
        db_session.refresh(response_obj)

        # Try to complete again
        payload = {
            "answers": [],
            "email": "test@example.com",
            "name": "Test",
        }

        response = client.post(f"/api/v1/responses/{response_obj.id}/complete", json=payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already completed" in response.json()["detail"].lower()

    def test_complete_with_partial_lead_data(self, client: TestClient, db_session: Session, test_user: User):
        """Test completing with only email (no name) doesn't create lead"""
        # Create assessment and question
        assessment = Assessment(
            title="Test",
            status="published",
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
        )
        db_session.add(assessment)
        db_session.commit()
        db_session.refresh(assessment)

        question = Question(assessment_id=assessment.id, text="Q?", type="multiple_choice", order=1)
        db_session.add(question)
        db_session.commit()
        db_session.refresh(question)

        # Create response
        response_obj = Response(
            assessment_id=assessment.id,
            session_id=str(uuid4()),
            status="in_progress",
        )
        db_session.add(response_obj)
        db_session.commit()
        db_session.refresh(response_obj)

        # Complete with only email (missing name)
        payload = {
            "answers": [{"question_id": str(question.id), "answer_text": "A", "points_awarded": 50}],
            "email": "onlyemail@example.com",
        }

        response = client.post(f"/api/v1/responses/{response_obj.id}/complete", json=payload)

        assert response.status_code == status.HTTP_200_OK

        # Verify no lead was created (both email and name required)
        lead = db_session.query(Lead).filter(Lead.email == "onlyemail@example.com").first()
        assert lead is None


class TestResponseScoring:
    """Tests for score calculation logic"""

    def test_score_accumulation_across_multiple_submissions(self, client: TestClient, db_session: Session, test_user: User):
        """Test that scores accumulate correctly across multiple submissions"""
        # Create assessment
        assessment = Assessment(
            title="Test",
            status="published",
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
        )
        db_session.add(assessment)
        db_session.commit()
        db_session.refresh(assessment)

        # Create questions
        q1 = Question(assessment_id=assessment.id, text="Q1?", type="multiple_choice", order=1)
        q2 = Question(assessment_id=assessment.id, text="Q2?", type="multiple_choice", order=2)
        q3 = Question(assessment_id=assessment.id, text="Q3?", type="multiple_choice", order=3)
        db_session.add_all([q1, q2, q3])
        db_session.commit()
        db_session.refresh(q1)
        db_session.refresh(q2)
        db_session.refresh(q3)

        # Create response
        response_obj = Response(
            assessment_id=assessment.id,
            session_id=str(uuid4()),
            status="in_progress",
        )
        db_session.add(response_obj)
        db_session.commit()
        db_session.refresh(response_obj)

        # Submit first answer
        payload1 = {"answers": [{"question_id": str(q1.id), "answer_text": "A", "points_awarded": 10}]}
        client.post(f"/api/v1/responses/{response_obj.id}/answers", json=payload1)

        # Submit second answer
        payload2 = {"answers": [{"question_id": str(q2.id), "answer_text": "B", "points_awarded": 20}]}
        client.post(f"/api/v1/responses/{response_obj.id}/answers", json=payload2)

        # Complete with third answer
        payload3 = {
            "answers": [{"question_id": str(q3.id), "answer_text": "C", "points_awarded": 30}],
            "email": "test@example.com",
            "name": "Test User",
        }
        response = client.post(f"/api/v1/responses/{response_obj.id}/complete", json=payload3)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_score"] == 60  # 10 + 20 + 30


class TestPublicAssessmentEdgeCases:
    """Tests for edge cases in public assessment endpoint"""

    def test_get_assessment_with_no_questions(self, client: TestClient, db_session: Session, test_user: User):
        """Test getting published assessment with no questions"""
        assessment = Assessment(
            title="No Questions",
            description="Empty assessment",
            status="published",
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
        )
        db_session.add(assessment)
        db_session.commit()
        db_session.refresh(assessment)

        response = client.get(f"/api/v1/tenants/{test_user.tenant_id}/assessments/{assessment.id}/public")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["questions"]) == 0

    def test_get_assessment_with_multiple_questions_ordered(self, client: TestClient, db_session: Session, test_user: User):
        """Test that questions are returned in correct order"""
        assessment = Assessment(
            title="Ordered Test",
            status="published",
            tenant_id=test_user.tenant_id,
            created_by=test_user.id,
        )
        db_session.add(assessment)
        db_session.commit()
        db_session.refresh(assessment)

        # Create questions in random order
        q3 = Question(assessment_id=assessment.id, text="Q3?", type="multiple_choice", order=3)
        q1 = Question(assessment_id=assessment.id, text="Q1?", type="multiple_choice", order=1)
        q2 = Question(assessment_id=assessment.id, text="Q2?", type="multiple_choice", order=2)
        db_session.add_all([q3, q1, q2])
        db_session.commit()

        response = client.get(f"/api/v1/tenants/{test_user.tenant_id}/assessments/{assessment.id}/public")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["questions"]) == 3
        assert data["questions"][0]["text"] == "Q1?"
        assert data["questions"][1]["text"] == "Q2?"
        assert data["questions"][2]["text"] == "Q3?"
