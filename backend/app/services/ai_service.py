"""
AI Service (Refactored)

Enhanced AI service with improved error handling, async support, and multi-tenant capabilities.

Improvements:
- Async/await with AsyncAnthropic client
- Structured error handling with retry logic
- Robust JSON extraction
- Prompt injection protection
- Multi-tenant support with context tracking
- Token usage logging
- Standardized prompt templates
"""

import time
from typing import Any, Dict, Optional
from uuid import UUID

from anthropic import AsyncAnthropic
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.constants import AIConfig, LeadScoreThreshold
from app.core.logging_config import get_logger
from app.models.ai_usage import AIUsageLog
from app.services.ai import (
    AIJSONParseError,
    AIValidationError,
    JSONExtractor,
    PromptSanitizer,
    PromptTemplates,
    get_industry_template,
    get_lead_analysis_template,
    get_recommended_action,
    retry_with_backoff,
)
from app.services.ai.prompt_templates import (
    IndustryTemplateData,
    LeadAnalysisTemplateData,
)

logger = get_logger(__name__)


class AIService:
    """
    Enhanced AI service using Claude API.

    Features:
    - Async operations with retry logic
    - Structured error handling
    - Prompt injection protection
    - Multi-tenant context tracking
    - Token usage logging
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI service.

        Args:
            api_key: Optional API key override (defaults to settings)
        """
        self.client = AsyncAnthropic(api_key=api_key or settings.ANTHROPIC_API_KEY)
        self.model = AIConfig.MODEL_ASSESSMENT
        self.json_extractor = JSONExtractor()
        self.sanitizer = PromptSanitizer()
        logger.info(f"AIService initialized with model: {self.model}")

    async def generate_assessment(
        self,
        topic: str,
        industry: str,
        num_questions: int = 5,
        tenant_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        Generate an assessment structure using Claude AI.

        Args:
            topic: Assessment topic
            industry: Target industry
            num_questions: Number of questions (default: 5)
            tenant_id: Optional tenant ID for logging/tracking

        Returns:
            Dictionary with success, data, usage, and optional tenant_id

        Raises:
            AIPromptInjectionError: If input contains suspicious patterns
            AIJSONParseError: If response cannot be parsed
            AIAPIError: If API call fails after retries
        """
        logger.info(f"Generating assessment: topic='{topic[:50]}...', industry={industry}, num_questions={num_questions}, tenant_id={tenant_id}")

        # Sanitize inputs
        safe_topic = self.sanitizer.sanitize_topic(topic)

        # Get industry template
        industry_template = get_industry_template(industry)
        template_data = IndustryTemplateData(
            name=industry_template.name,
            description=industry_template.description,
            common_pain_points=industry_template.common_pain_points,
            question_themes=industry_template.question_themes,
            scoring_guidelines=industry_template.scoring_guidelines,
            example_questions=industry_template.example_questions,
        )

        # Build prompt using template
        prompt = PromptTemplates.build_assessment_generation_prompt(
            topic=safe_topic,
            num_questions=num_questions,
            industry_template=template_data,
        )

        # Call Claude API with retry logic
        start_time = time.time()
        try:
            message = await retry_with_backoff(
                self._call_claude_api,
                prompt=prompt,
                max_tokens=AIConfig.MAX_TOKENS_ASSESSMENT,
            )
            duration_ms = int((time.time() - start_time) * 1000)

            # Extract and parse JSON response
            response_text = message.content[0].text
            assessment_data = self.json_extractor.extract(response_text)

            # Validate assessment structure
            validation_result = self._validate_assessment(assessment_data)
            if not validation_result["valid"]:
                raise AIValidationError(f"Invalid assessment structure: {validation_result['error']}")

            # Add metadata
            assessment_data["metadata"] = {
                "industry": industry,
                "industry_template": industry_template.name,
                "topic": topic,
                "generated_at": "auto",
                "version": PromptTemplates.VERSION,
            }

            # Log token usage
            usage_info = {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
            }
            self._log_token_usage(
                operation="generate_assessment",
                tenant_id=tenant_id,
                user_id=user_id,
                usage=usage_info,
                db=db,
                duration_ms=duration_ms,
                success=True,
            )

            logger.info(f"Assessment generated successfully: {usage_info['input_tokens']} input tokens, {usage_info['output_tokens']} output tokens")

            result = {
                "success": True,
                "data": assessment_data,
                "usage": usage_info,
            }
            if tenant_id:
                result["tenant_id"] = str(tenant_id)

            return result

        except AIJSONParseError as e:
            logger.error(f"JSON parsing failed: {e}")
            return {
                "success": False,
                "error": f"Invalid JSON response from Claude: {str(e)}",
            }
        except AIValidationError as e:
            logger.error(f"Validation failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }
        except Exception as e:
            logger.error(f"Assessment generation failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    async def analyze_lead_insights(
        self,
        assessment_responses: Dict[str, Any],
        assessment_title: str = "Assessment",
        industry: str = "general",
        tenant_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        lead_id: Optional[UUID] = None,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        Analyze lead responses and generate insights using Claude AI.

        Args:
            assessment_responses: Response data dictionary
            assessment_title: Assessment name
            industry: Target industry
            tenant_id: Optional tenant ID for logging/tracking

        Returns:
            Dictionary with success, data, usage, and optional tenant_id

        Raises:
            AIPromptInjectionError: If input contains suspicious patterns
            AIJSONParseError: If response cannot be parsed
            AIAPIError: If API call fails after retries
        """
        logger.info(f"Analyzing lead insights: assessment='{assessment_title}', industry={industry}, tenant_id={tenant_id}")

        # Sanitize inputs
        safe_responses = self.sanitizer.sanitize_responses(assessment_responses)

        # Get lead analysis template
        lead_template = get_lead_analysis_template(industry)
        template_data = LeadAnalysisTemplateData(
            industry=lead_template.industry,
            key_signals=lead_template.key_signals,
            qualification_criteria=lead_template.qualification_criteria,
            talking_points_themes=lead_template.talking_points_themes,
        )

        # Build prompt using template
        prompt = PromptTemplates.build_lead_analysis_prompt(
            assessment_responses=safe_responses,
            assessment_title=assessment_title,
            lead_template=template_data,
        )

        # Call Claude API with retry logic
        start_time = time.time()
        try:
            message = await retry_with_backoff(
                self._call_claude_api,
                prompt=prompt,
                max_tokens=AIConfig.MAX_TOKENS_ANALYSIS,
            )
            duration_ms = int((time.time() - start_time) * 1000)

            # Extract and parse JSON response
            response_text = message.content[0].text
            insights_data = self.json_extractor.extract(response_text)

            # Add industry-specific recommended action
            score = insights_data.get("overall_score", 0)
            insights_data["recommended_action"] = get_recommended_action(score, industry)

            # Add automatic priority level
            hot_lead = insights_data.get("hot_lead", False)
            priority_level = self._calculate_priority_level(score, hot_lead)
            insights_data["priority_level"] = priority_level

            # Add follow-up timing recommendation
            insights_data["follow_up_timing"] = self._calculate_follow_up_timing(score, priority_level)

            # Log token usage
            usage_info = {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
            }
            self._log_token_usage(
                operation="analyze_lead_insights",
                tenant_id=tenant_id,
                user_id=user_id,
                lead_id=lead_id,
                usage=usage_info,
                db=db,
                duration_ms=duration_ms,
                success=True,
            )

            logger.info(f"Lead insights analyzed successfully: score={score}, hot_lead={hot_lead}, priority={priority_level}")

            result = {
                "success": True,
                "data": insights_data,
                "usage": usage_info,
            }
            if tenant_id:
                result["tenant_id"] = str(tenant_id)

            return result

        except AIJSONParseError as e:
            logger.error(f"JSON parsing failed: {e}")
            return {
                "success": False,
                "error": f"Invalid JSON response from Claude: {str(e)}",
            }
        except Exception as e:
            logger.error(f"Lead analysis failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    async def rephrase_content(
        self,
        text: str,
        style: str = "professional",
        target_audience: str = "general",
        tenant_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        Rephrase or improve content using Claude AI.

        Args:
            text: Original text to rephrase
            style: Writing style
            target_audience: Target audience
            tenant_id: Optional tenant ID for logging/tracking

        Returns:
            Dictionary with success, data, usage, and optional tenant_id

        Raises:
            AIPromptInjectionError: If input contains suspicious patterns
            AIJSONParseError: If response cannot be parsed
            AIAPIError: If API call fails after retries
        """
        logger.info(f"Rephrasing content: style={style}, audience={target_audience}, tenant_id={tenant_id}")

        # Sanitize inputs
        safe_text = self.sanitizer.sanitize_text(text)

        # Build prompt using template
        prompt = PromptTemplates.build_rephrase_prompt(
            text=safe_text,
            style=style,
            target_audience=target_audience,
        )

        # Call Claude API with retry logic
        start_time = time.time()
        try:
            message = await retry_with_backoff(
                self._call_claude_api,
                prompt=prompt,
                max_tokens=AIConfig.MAX_TOKENS_REPHRASE,
            )
            duration_ms = int((time.time() - start_time) * 1000)

            # Extract and parse JSON response
            response_text = message.content[0].text
            rephrased_data = self.json_extractor.extract(response_text)

            # Log token usage
            usage_info = {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
            }
            self._log_token_usage(
                operation="rephrase_content",
                tenant_id=tenant_id,
                user_id=user_id,
                usage=usage_info,
                db=db,
                duration_ms=duration_ms,
                success=True,
            )

            logger.info("Content rephrased successfully")

            result = {
                "success": True,
                "data": rephrased_data,
                "usage": usage_info,
            }
            if tenant_id:
                result["tenant_id"] = str(tenant_id)

            return result

        except AIJSONParseError as e:
            logger.error(f"JSON parsing failed: {e}")
            return {
                "success": False,
                "error": f"Invalid JSON response from Claude: {str(e)}",
            }
        except Exception as e:
            logger.error(f"Content rephrasing failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    async def _call_claude_api(self, prompt: str, max_tokens: int) -> Any:
        """
        Internal method to call Claude API.

        Args:
            prompt: Prompt string
            max_tokens: Maximum tokens to generate

        Returns:
            Claude API message response
        """
        return await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )

    def _validate_assessment(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate assessment structure and content quality.

        Args:
            assessment_data: Generated assessment data

        Returns:
            Dictionary with 'valid' (bool) and 'error' (str) fields
        """
        try:
            # Check required fields
            if "title" not in assessment_data:
                return {"valid": False, "error": "Missing 'title' field"}
            if "description" not in assessment_data:
                return {"valid": False, "error": "Missing 'description' field"}
            if "questions" not in assessment_data:
                return {"valid": False, "error": "Missing 'questions' field"}

            # Validate questions
            questions = assessment_data["questions"]
            if not isinstance(questions, list) or len(questions) == 0:
                return {"valid": False, "error": "Questions must be a non-empty list"}

            for i, question in enumerate(questions):
                # Check question structure
                if "text" not in question:
                    return {
                        "valid": False,
                        "error": f"Question {i + 1}: Missing 'text' field",
                    }
                if "options" not in question:
                    return {
                        "valid": False,
                        "error": f"Question {i + 1}: Missing 'options' field",
                    }

                # Validate options
                options = question["options"]
                if not isinstance(options, list) or len(options) < 2:
                    return {
                        "valid": False,
                        "error": f"Question {i + 1}: Must have at least 2 options",
                    }

                # Check scoring
                scores = [opt.get("score", 0) for opt in options]
                if not all(isinstance(s, (int, float)) for s in scores):
                    return {
                        "valid": False,
                        "error": f"Question {i + 1}: All scores must be numbers",
                    }
                if not (min(scores) >= 0 and max(scores) <= 100):
                    return {
                        "valid": False,
                        "error": f"Question {i + 1}: Scores must be between 0 and 100",
                    }

            return {"valid": True, "error": None}

        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}

    def _calculate_priority_level(self, score: int, hot_lead: bool) -> str:
        """
        Calculate automatic priority level based on lead score and hot lead status.

        Args:
            score: Lead score (0-100)
            hot_lead: Whether this is a hot lead

        Returns:
            Priority level: critical|high|medium|low
        """
        if hot_lead and score >= LeadScoreThreshold.CRITICAL:
            return "critical"
        elif score >= LeadScoreThreshold.HIGH:
            return "high"
        elif score >= LeadScoreThreshold.MEDIUM:
            return "medium"
        else:
            return "low"

    def _calculate_follow_up_timing(self, score: int, priority_level: str) -> str:
        """
        Calculate recommended follow-up timing based on score and priority.

        Args:
            score: Lead score (0-100)
            priority_level: Priority level

        Returns:
            Follow-up timing recommendation
        """
        if priority_level == "critical":
            return "即座に（1時間以内）"
        elif priority_level == "high":
            return "24時間以内"
        elif priority_level == "medium":
            return "3-5営業日以内"
        else:
            return "2週間以内または次回キャンペーン時"

    def _log_token_usage(
        self,
        operation: str,
        usage: Dict[str, int],
        tenant_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        assessment_id: Optional[UUID] = None,
        lead_id: Optional[UUID] = None,
        db: Optional[Session] = None,
        duration_ms: Optional[int] = None,
        success: bool = True,
    ) -> None:
        """
        Log token usage for monitoring and billing.

        Args:
            operation: Operation name
            usage: Usage dictionary with input/output tokens
            tenant_id: Optional tenant ID
            user_id: Optional user ID
            assessment_id: Optional assessment ID
            lead_id: Optional lead ID
            db: Optional database session for persistence
            duration_ms: Optional request duration in milliseconds
            success: Whether the operation succeeded
        """
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        total_tokens = input_tokens + output_tokens

        logger.info(
            f"Token usage - operation={operation}, tenant_id={tenant_id}, "
            f"input={input_tokens}, output={output_tokens}, total={total_tokens}"
        )

        # Store in database if session provided
        if db and tenant_id:
            try:
                usage_log = AIUsageLog(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    operation=operation,
                    model=self.model,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    assessment_id=assessment_id,
                    lead_id=lead_id,
                    duration_ms=duration_ms,
                    success="success" if success else "failure",
                )
                usage_log.update_cost()  # Calculate cost
                db.add(usage_log)
                db.commit()
                logger.debug(
                    f"Saved AI usage log: id={usage_log.id}, cost=${usage_log.cost_usd}"
                )
            except Exception as e:
                logger.error(f"Failed to save AI usage log: {e}", exc_info=True)
                # Don't fail the main operation if logging fails
                db.rollback()
