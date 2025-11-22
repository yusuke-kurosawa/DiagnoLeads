"""
Tests for AI Service

Comprehensive test coverage for AIService including:
- Assessment generation
- Lead insights analysis
- Content rephrasing
- Error handling
- Validation
- Token usage logging
"""

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.core.constants import LeadScoreThreshold
from app.models.ai_usage import AIUsageLog
from app.services.ai import AIJSONParseError, AIValidationError
from app.services.ai_service import AIService


class MockMessage:
    """Mock Claude API message response"""

    def __init__(self, text: str, input_tokens: int = 100, output_tokens: int = 200):
        self.content = [Mock(text=text)]
        self.usage = Mock(input_tokens=input_tokens, output_tokens=output_tokens)


@pytest.fixture
def ai_service():
    """Create AIService instance with mocked client"""
    with patch("app.services.ai_service.AsyncAnthropic"):
        service = AIService(api_key="test-key")
        return service


class TestGenerateAssessment:
    """Tests for generate_assessment method"""

    @pytest.mark.asyncio
    async def test_generate_assessment_success(self, ai_service):
        """Test successful assessment generation"""
        # Mock Claude API response
        assessment_json = {
            "title": "Test Assessment",
            "description": "Test description",
            "questions": [
                {
                    "text": "Question 1?",
                    "options": [
                        {"text": "Option A", "score": 10},
                        {"text": "Option B", "score": 20},
                    ],
                }
            ],
        }

        mock_message = MockMessage(
            text=f"```json\n{json.dumps(assessment_json)}\n```",
            input_tokens=150,
            output_tokens=250,
        )

        ai_service._call_claude_api = AsyncMock(return_value=mock_message)

        # Call method
        result = await ai_service.generate_assessment(
            topic="Digital Marketing",
            industry="saas",
            num_questions=1,
            tenant_id=uuid4(),
        )

        # Assertions
        assert result["success"] is True
        assert result["data"]["title"] == "Test Assessment"
        assert len(result["data"]["questions"]) == 1
        assert result["usage"]["input_tokens"] == 150
        assert result["usage"]["output_tokens"] == 250
        assert "metadata" in result["data"]

    @pytest.mark.asyncio
    async def test_generate_assessment_with_db_logging(self, ai_service, db_session: Session):
        """Test assessment generation with database logging"""
        assessment_json = {
            "title": "Test",
            "description": "Test",
            "questions": [
                {
                    "text": "Q1?",
                    "options": [
                        {"text": "A", "score": 10},
                        {"text": "B", "score": 20},
                    ],
                }
            ],
        }

        mock_message = MockMessage(
            text=f"```json\n{json.dumps(assessment_json)}\n```",
            input_tokens=100,
            output_tokens=200,
        )

        ai_service._call_claude_api = AsyncMock(return_value=mock_message)

        tenant_id = uuid4()
        user_id = uuid4()

        # Call with database session
        result = await ai_service.generate_assessment(
            topic="Test",
            industry="general",
            tenant_id=tenant_id,
            user_id=user_id,
            db=db_session,
        )

        assert result["success"] is True

        # Verify usage log was created
        usage_log = db_session.query(AIUsageLog).filter(AIUsageLog.tenant_id == tenant_id).first()
        assert usage_log is not None
        assert usage_log.operation == "generate_assessment"
        assert usage_log.input_tokens == 100
        assert usage_log.output_tokens == 200

    @pytest.mark.asyncio
    async def test_generate_assessment_invalid_json(self, ai_service):
        """Test assessment generation with invalid JSON response"""
        mock_message = MockMessage(text="Invalid JSON { broken", input_tokens=100, output_tokens=50)

        ai_service._call_claude_api = AsyncMock(return_value=mock_message)

        result = await ai_service.generate_assessment(
            topic="Test",
            industry="general",
        )

        assert result["success"] is False
        assert "Invalid JSON response" in result["error"]

    @pytest.mark.asyncio
    async def test_generate_assessment_missing_title(self, ai_service):
        """Test assessment generation with missing title"""
        invalid_json = {
            "description": "No title",
            "questions": [],
        }

        mock_message = MockMessage(text=f"```json\n{json.dumps(invalid_json)}\n```")

        ai_service._call_claude_api = AsyncMock(return_value=mock_message)

        result = await ai_service.generate_assessment(
            topic="Test",
            industry="general",
        )

        assert result["success"] is False
        assert "Invalid assessment structure" in result["error"]

    @pytest.mark.asyncio
    async def test_generate_assessment_empty_questions(self, ai_service):
        """Test assessment generation with empty questions list"""
        invalid_json = {
            "title": "Test",
            "description": "Test",
            "questions": [],
        }

        mock_message = MockMessage(text=f"```json\n{json.dumps(invalid_json)}\n```")

        ai_service._call_claude_api = AsyncMock(return_value=mock_message)

        result = await ai_service.generate_assessment(
            topic="Test",
            industry="general",
        )

        assert result["success"] is False
        assert "non-empty list" in result["error"]

    @pytest.mark.asyncio
    async def test_generate_assessment_api_error(self, ai_service):
        """Test assessment generation with API error"""
        ai_service._call_claude_api = AsyncMock(side_effect=Exception("API connection failed"))

        result = await ai_service.generate_assessment(
            topic="Test",
            industry="general",
        )

        assert result["success"] is False
        assert "API connection failed" in result["error"]


class TestAnalyzeLeadInsights:
    """Tests for analyze_lead_insights method"""

    @pytest.mark.asyncio
    async def test_analyze_lead_insights_success(self, ai_service):
        """Test successful lead insights analysis"""
        insights_json = {
            "overall_score": 85,
            "hot_lead": True,
            "pain_points": ["Cost reduction", "Scalability"],
            "talking_points": ["ROI discussion", "Case studies"],
        }

        mock_message = MockMessage(
            text=f"```json\n{json.dumps(insights_json)}\n```",
            input_tokens=200,
            output_tokens=300,
        )

        ai_service._call_claude_api = AsyncMock(return_value=mock_message)

        assessment_responses = {
            "q1": {"question": "Budget?", "answer": "High"},
            "q2": {"question": "Timeline?", "answer": "Urgent"},
        }

        result = await ai_service.analyze_lead_insights(
            assessment_responses=assessment_responses,
            assessment_title="Test Assessment",
            industry="saas",
            tenant_id=uuid4(),
        )

        assert result["success"] is True
        assert result["data"]["overall_score"] == 85
        assert result["data"]["hot_lead"] is True
        assert "recommended_action" in result["data"]
        assert "priority_level" in result["data"]
        assert "follow_up_timing" in result["data"]

    @pytest.mark.asyncio
    async def test_analyze_lead_insights_with_db_logging(self, ai_service, db_session: Session):
        """Test lead analysis with database logging"""
        insights_json = {
            "overall_score": 75,
            "hot_lead": False,
            "pain_points": ["Integration"],
            "talking_points": ["API capabilities"],
        }

        mock_message = MockMessage(text=f"```json\n{json.dumps(insights_json)}\n```")

        ai_service._call_claude_api = AsyncMock(return_value=mock_message)

        tenant_id = uuid4()
        lead_id = uuid4()

        result = await ai_service.analyze_lead_insights(
            assessment_responses={"q1": {"question": "Test", "answer": "Test"}},
            tenant_id=tenant_id,
            lead_id=lead_id,
            db=db_session,
        )

        assert result["success"] is True

        # Verify usage log
        usage_log = (
            db_session.query(AIUsageLog)
            .filter(AIUsageLog.tenant_id == tenant_id, AIUsageLog.lead_id == lead_id)
            .first()
        )
        assert usage_log is not None
        assert usage_log.operation == "analyze_lead_insights"

    @pytest.mark.asyncio
    async def test_analyze_lead_insights_json_error(self, ai_service):
        """Test lead analysis with JSON parsing error"""
        mock_message = MockMessage(text="Not JSON at all!")

        ai_service._call_claude_api = AsyncMock(return_value=mock_message)

        result = await ai_service.analyze_lead_insights(
            assessment_responses={"q1": {"question": "Test", "answer": "Test"}},
        )

        assert result["success"] is False
        assert "Invalid JSON response" in result["error"]


class TestRephraseContent:
    """Tests for rephrase_content method"""

    @pytest.mark.asyncio
    async def test_rephrase_content_success(self, ai_service):
        """Test successful content rephrasing"""
        rephrased_json = {
            "original": "Old text",
            "rephrased": "Improved professional text",
            "improvements": ["Better tone", "Clearer message"],
        }

        mock_message = MockMessage(text=f"```json\n{json.dumps(rephrased_json)}\n```")

        ai_service._call_claude_api = AsyncMock(return_value=mock_message)

        result = await ai_service.rephrase_content(
            text="Old text",
            style="professional",
            target_audience="executives",
            tenant_id=uuid4(),
        )

        assert result["success"] is True
        assert result["data"]["rephrased"] == "Improved professional text"
        assert "improvements" in result["data"]

    @pytest.mark.asyncio
    async def test_rephrase_content_with_db_logging(self, ai_service, db_session: Session):
        """Test content rephrasing with database logging"""
        rephrased_json = {
            "original": "Test",
            "rephrased": "Professional test",
        }

        mock_message = MockMessage(text=f"```json\n{json.dumps(rephrased_json)}\n```")

        ai_service._call_claude_api = AsyncMock(return_value=mock_message)

        tenant_id = uuid4()

        result = await ai_service.rephrase_content(
            text="Test",
            tenant_id=tenant_id,
            db=db_session,
        )

        assert result["success"] is True

        # Verify usage log
        usage_log = db_session.query(AIUsageLog).filter(AIUsageLog.tenant_id == tenant_id).first()
        assert usage_log is not None
        assert usage_log.operation == "rephrase_content"

    @pytest.mark.asyncio
    async def test_rephrase_content_json_error(self, ai_service):
        """Test content rephrasing with JSON error"""
        mock_message = MockMessage(text="Plain text response")

        ai_service._call_claude_api = AsyncMock(return_value=mock_message)

        result = await ai_service.rephrase_content(text="Test")

        assert result["success"] is False
        assert "Invalid JSON response" in result["error"]


class TestValidateAssessment:
    """Tests for _validate_assessment method"""

    def test_validate_assessment_valid(self, ai_service):
        """Test validation of valid assessment"""
        assessment = {
            "title": "Test",
            "description": "Description",
            "questions": [
                {
                    "text": "Q1?",
                    "options": [
                        {"text": "A", "score": 10},
                        {"text": "B", "score": 20},
                    ],
                }
            ],
        }

        result = ai_service._validate_assessment(assessment)

        assert result["valid"] is True
        assert result["error"] is None

    def test_validate_assessment_missing_title(self, ai_service):
        """Test validation fails for missing title"""
        assessment = {
            "description": "Description",
            "questions": [],
        }

        result = ai_service._validate_assessment(assessment)

        assert result["valid"] is False
        assert "Missing 'title'" in result["error"]

    def test_validate_assessment_missing_description(self, ai_service):
        """Test validation fails for missing description"""
        assessment = {
            "title": "Test",
            "questions": [],
        }

        result = ai_service._validate_assessment(assessment)

        assert result["valid"] is False
        assert "Missing 'description'" in result["error"]

    def test_validate_assessment_empty_questions(self, ai_service):
        """Test validation fails for empty questions"""
        assessment = {
            "title": "Test",
            "description": "Description",
            "questions": [],
        }

        result = ai_service._validate_assessment(assessment)

        assert result["valid"] is False
        assert "non-empty list" in result["error"]

    def test_validate_assessment_question_missing_text(self, ai_service):
        """Test validation fails for question missing text"""
        assessment = {
            "title": "Test",
            "description": "Description",
            "questions": [
                {
                    "options": [{"text": "A", "score": 10}],
                }
            ],
        }

        result = ai_service._validate_assessment(assessment)

        assert result["valid"] is False
        assert "Missing 'text'" in result["error"]

    def test_validate_assessment_question_missing_options(self, ai_service):
        """Test validation fails for question missing options"""
        assessment = {
            "title": "Test",
            "description": "Description",
            "questions": [
                {
                    "text": "Q1?",
                }
            ],
        }

        result = ai_service._validate_assessment(assessment)

        assert result["valid"] is False
        assert "Missing 'options'" in result["error"]

    def test_validate_assessment_insufficient_options(self, ai_service):
        """Test validation fails for insufficient options"""
        assessment = {
            "title": "Test",
            "description": "Description",
            "questions": [
                {
                    "text": "Q1?",
                    "options": [{"text": "Only one", "score": 10}],
                }
            ],
        }

        result = ai_service._validate_assessment(assessment)

        assert result["valid"] is False
        assert "at least 2 options" in result["error"]

    def test_validate_assessment_invalid_scores(self, ai_service):
        """Test validation fails for invalid score values"""
        assessment = {
            "title": "Test",
            "description": "Description",
            "questions": [
                {
                    "text": "Q1?",
                    "options": [
                        {"text": "A", "score": -10},
                        {"text": "B", "score": 20},
                    ],
                }
            ],
        }

        result = ai_service._validate_assessment(assessment)

        assert result["valid"] is False
        assert "between 0 and 100" in result["error"]

    def test_validate_assessment_score_too_high(self, ai_service):
        """Test validation fails for scores above 100"""
        assessment = {
            "title": "Test",
            "description": "Description",
            "questions": [
                {
                    "text": "Q1?",
                    "options": [
                        {"text": "A", "score": 50},
                        {"text": "B", "score": 150},
                    ],
                }
            ],
        }

        result = ai_service._validate_assessment(assessment)

        assert result["valid"] is False
        assert "between 0 and 100" in result["error"]


class TestPriorityCalculation:
    """Tests for _calculate_priority_level method"""

    def test_calculate_priority_critical(self, ai_service):
        """Test critical priority calculation"""
        priority = ai_service._calculate_priority_level(
            score=LeadScoreThreshold.CRITICAL, hot_lead=True
        )
        assert priority == "critical"

    def test_calculate_priority_high(self, ai_service):
        """Test high priority calculation"""
        priority = ai_service._calculate_priority_level(
            score=LeadScoreThreshold.HIGH, hot_lead=False
        )
        assert priority == "high"

    def test_calculate_priority_medium(self, ai_service):
        """Test medium priority calculation"""
        priority = ai_service._calculate_priority_level(
            score=LeadScoreThreshold.MEDIUM, hot_lead=False
        )
        assert priority == "medium"

    def test_calculate_priority_low(self, ai_service):
        """Test low priority calculation"""
        priority = ai_service._calculate_priority_level(score=30, hot_lead=False)
        assert priority == "low"


class TestFollowUpTiming:
    """Tests for _calculate_follow_up_timing method"""

    def test_follow_up_timing_critical(self, ai_service):
        """Test follow-up timing for critical priority"""
        timing = ai_service._calculate_follow_up_timing(score=90, priority_level="critical")
        assert "1時間以内" in timing

    def test_follow_up_timing_high(self, ai_service):
        """Test follow-up timing for high priority"""
        timing = ai_service._calculate_follow_up_timing(score=75, priority_level="high")
        assert "24時間以内" in timing

    def test_follow_up_timing_medium(self, ai_service):
        """Test follow-up timing for medium priority"""
        timing = ai_service._calculate_follow_up_timing(score=55, priority_level="medium")
        assert "3-5営業日以内" in timing

    def test_follow_up_timing_low(self, ai_service):
        """Test follow-up timing for low priority"""
        timing = ai_service._calculate_follow_up_timing(score=30, priority_level="low")
        assert "2週間以内" in timing or "次回キャンペーン" in timing


class TestTokenUsageLogging:
    """Tests for _log_token_usage method"""

    def test_log_token_usage_without_db(self, ai_service):
        """Test token usage logging without database"""
        # Should not raise exception
        ai_service._log_token_usage(
            operation="test",
            usage={"input_tokens": 100, "output_tokens": 200},
            tenant_id=uuid4(),
        )

    def test_log_token_usage_with_db(self, ai_service, db_session: Session):
        """Test token usage logging with database"""
        tenant_id = uuid4()
        user_id = uuid4()

        ai_service._log_token_usage(
            operation="test_operation",
            usage={"input_tokens": 100, "output_tokens": 200},
            tenant_id=tenant_id,
            user_id=user_id,
            db=db_session,
            duration_ms=1500,
            success=True,
        )

        # Verify log was created
        usage_log = db_session.query(AIUsageLog).filter(AIUsageLog.tenant_id == tenant_id).first()
        assert usage_log is not None
        assert usage_log.operation == "test_operation"
        assert usage_log.input_tokens == 100
        assert usage_log.output_tokens == 200
        assert usage_log.total_tokens == 300
        assert usage_log.duration_ms == 1500
        assert usage_log.success == "success"

    def test_log_token_usage_db_error_does_not_fail(self, ai_service, db_session: Session):
        """Test that database logging error doesn't fail the operation"""
        # Mock db.commit to raise exception
        db_session.commit = Mock(side_effect=Exception("DB error"))

        # Should not raise exception
        ai_service._log_token_usage(
            operation="test",
            usage={"input_tokens": 100, "output_tokens": 200},
            tenant_id=uuid4(),
            db=db_session,
        )


class TestEdgeCases:
    """Tests for edge cases and error scenarios"""

    @pytest.mark.asyncio
    async def test_generate_assessment_with_sanitization(self, ai_service):
        """Test that input sanitization works"""
        assessment_json = {
            "title": "Safe Assessment",
            "description": "Safe",
            "questions": [
                {
                    "text": "Q?",
                    "options": [
                        {"text": "A", "score": 10},
                        {"text": "B", "score": 20},
                    ],
                }
            ],
        }

        mock_message = MockMessage(text=f"```json\n{json.dumps(assessment_json)}\n```")
        ai_service._call_claude_api = AsyncMock(return_value=mock_message)

        # Input with potentially problematic content
        result = await ai_service.generate_assessment(
            topic="Test <script>alert('xss')</script>",
            industry="general",
        )

        # Should still succeed with sanitized input
        assert result["success"] is True

    def test_validate_assessment_with_exception(self, ai_service):
        """Test validation handles unexpected exceptions"""
        # Invalid structure that causes exception during validation
        invalid_assessment = {"questions": "not a list"}

        result = ai_service._validate_assessment(invalid_assessment)

        assert result["valid"] is False
        assert "Validation error" in result["error"]
