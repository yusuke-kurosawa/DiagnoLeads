"""
AI Service

Handles Claude API integration for assessment generation, insights analysis, and text rephrasing.
"""

import json
from typing import Optional, List, Dict, Any
from anthropic import Anthropic

from app.core.config import settings


class AIService:
    """AI service using Claude API"""

    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-5-sonnet-20241022"

    async def generate_assessment(
        self, topic: str, industry: str, num_questions: int = 5
    ) -> Dict[str, Any]:
        """
        Generate an assessment structure using Claude AI.

        Args:
            topic: Main topic/subject for the assessment
            industry: Target industry or use case
            num_questions: Number of questions to generate (default: 5)

        Returns:
            Dictionary containing:
            - title: Assessment title
            - description: Assessment description
            - questions: List of questions with options and scoring
        """
        prompt = f"""Generate a professional assessment/quiz in JSON format with the following requirements:

Topic: {topic}
Industry: {industry}
Number of Questions: {num_questions}

The assessment should be structured as a JSON object with:
{{
  "title": "string - descriptive title",
  "description": "string - brief description",
  "questions": [
    {{
      "id": "number - question number",
      "text": "string - question text",
      "type": "single_choice|multiple_choice|text|slider",
      "options": [
        {{
          "id": "string - option id",
          "text": "string - option text",
          "score": "number - point value for this option (0-100)"
        }}
      ],
      "explanation": "string - optional explanation"
    }}
  ]
}}

Guidelines:
- Create questions that are relevant to {industry}
- Make questions engaging and professional
- Include a mix of question types
- Ensure scoring makes sense (0=low relevance, 100=high relevance)
- Use JSON-valid characters only
- Provide realistic but diverse options

Return ONLY valid JSON, no additional text."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text
            assessment_data = json.loads(response_text)

            return {
                "success": True,
                "data": assessment_data,
                "usage": {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens,
                },
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON response from Claude: {str(e)}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def analyze_lead_insights(
        self, assessment_responses: Dict[str, Any], assessment_title: str = "Assessment"
    ) -> Dict[str, Any]:
        """
        Analyze lead responses and generate insights using Claude AI.

        Args:
            assessment_responses: Dictionary of question IDs to selected answers
            assessment_title: Name of the assessment

        Returns:
            Dictionary containing:
            - insights: List of identified issues/needs
            - recommendation: Recommended action
            - score: Overall lead quality score (0-100)
        """
        responses_text = json.dumps(assessment_responses, indent=2, ensure_ascii=False)

        prompt = f"""Analyze these assessment responses and provide sales insights in JSON format:

Assessment: {assessment_title}
Responses: {responses_text}

Generate a JSON object with:
{{
  "overall_score": "number (0-100) - overall assessment score",
  "hot_lead": "boolean - is this a qualified hot lead (score >= 75)?",
  "identified_needs": [
    {{
      "area": "string - problem area",
      "description": "string - what this indicates",
      "priority": "high|medium|low"
    }}
  ],
  "recommendation": "string - suggested next action",
  "key_talking_points": [
    "string - relevant points for sales conversation"
  ]
}}

Guidelines:
- Assess lead quality based on responses
- Identify specific problems or needs
- Provide actionable recommendations
- Focus on business value and pain points
- Return ONLY valid JSON

Return ONLY valid JSON, no additional text."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text
            insights_data = json.loads(response_text)

            return {
                "success": True,
                "data": insights_data,
                "usage": {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens,
                },
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON response from Claude: {str(e)}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rephrase_content(
        self, text: str, style: str = "professional", target_audience: str = "general"
    ) -> Dict[str, Any]:
        """
        Rephrase or improve content using Claude AI.

        Args:
            text: Original text to rephrase
            style: Style to use (professional, casual, technical, simple)
            target_audience: Target audience (executives, developers, customers, etc.)

        Returns:
            Dictionary containing:
            - original: Original text
            - rephrased: Rephrased text
            - alternatives: List of alternative phrasings
        """
        prompt = f"""Rephrase the following text in a {style} style for {target_audience} audience.
Also provide 2-3 alternative phrasings.

Return JSON format:
{{
  "original": "string - original text",
  "rephrased": "string - main rephrased version",
  "alternatives": [
    "string - alternative 1",
    "string - alternative 2"
  ]
}}

Text to rephrase: {text}

Guidelines:
- Maintain the core message
- Adjust tone to match the style
- Consider the target audience
- Keep it concise and clear
- Return ONLY valid JSON

Return ONLY valid JSON, no additional text."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text
            rephrased_data = json.loads(response_text)

            return {
                "success": True,
                "data": rephrased_data,
                "usage": {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens,
                },
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON response from Claude: {str(e)}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
