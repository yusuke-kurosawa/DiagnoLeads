"""
AI Service

Handles Claude API integration for assessment generation, insights analysis, and text rephrasing.
Enhanced with industry templates and improved prompt engineering.
"""

import json
from typing import Optional, List, Dict, Any
from anthropic import Anthropic

from app.core.config import settings
from app.services.ai.industry_templates import get_industry_template, list_available_industries


class AIService:
    """AI service using Claude API with enhanced assessment generation"""

    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-5-sonnet-20241022"

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
                    return {"valid": False, "error": f"Question {i+1}: Missing 'text' field"}
                if "options" not in question:
                    return {"valid": False, "error": f"Question {i+1}: Missing 'options' field"}

                # Validate options
                options = question["options"]
                if not isinstance(options, list) or len(options) < 2:
                    return {
                        "valid": False,
                        "error": f"Question {i+1}: Must have at least 2 options",
                    }

                # Check scoring
                scores = [opt.get("score", 0) for opt in options]
                if not all(isinstance(s, (int, float)) for s in scores):
                    return {
                        "valid": False,
                        "error": f"Question {i+1}: All scores must be numbers",
                    }
                if not (min(scores) >= 0 and max(scores) <= 100):
                    return {
                        "valid": False,
                        "error": f"Question {i+1}: Scores must be between 0 and 100",
                    }

            return {"valid": True, "error": None}

        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}

    async def generate_assessment(
        self, topic: str, industry: str, num_questions: int = 5
    ) -> Dict[str, Any]:
        """
        Generate an assessment structure using Claude AI with industry-specific templates.

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
        # Get industry-specific template
        industry_template = get_industry_template(industry)

        # Build enhanced prompt with industry context
        prompt = f"""あなたは{industry_template.name}業界のエキスパートです。以下の要件に基づいて、プロフェッショナルな診断（Assessment）をJSON形式で生成してください。

## 診断の要件

**トピック**: {topic}
**業界**: {industry_template.name} - {industry_template.description}
**質問数**: {num_questions}問

## 業界特有の課題（参考情報）
{chr(10).join(f"- {pain}" for pain in industry_template.common_pain_points)}

## 質問テーマ（これらを参考に質問を作成）
{chr(10).join(f"- {theme}" for theme in industry_template.question_themes)}

## スコアリングガイドライン
{industry_template.scoring_guidelines}

## 出力形式（JSON）

```json
{{
  "title": "string - 魅力的で具体的なタイトル（例：マーケティングオートメーション成熟度診断）",
  "description": "string - 診断の目的と対象者を明確に説明（100-200文字程度）",
  "questions": [
    {{
      "id": 1,
      "text": "string - 明確で具体的な質問文（曖昧な表現を避ける）",
      "type": "single_choice",
      "options": [
        {{
          "id": "option_1",
          "text": "string - 選択肢のテキスト",
          "score": 0,
          "explanation": "string - なぜこのスコアなのかの簡単な説明"
        }},
        {{
          "id": "option_2",
          "text": "string - 選択肢のテキスト",
          "score": 33,
          "explanation": "string - なぜこのスコアなのかの簡単な説明"
        }},
        {{
          "id": "option_3",
          "text": "string - 選択肢のテキスト",
          "score": 67,
          "explanation": "string - なぜこのスコアなのかの簡単な説明"
        }},
        {{
          "id": "option_4",
          "text": "string - 選択肢のテキスト",
          "score": 100,
          "explanation": "string - なぜこのスコアなのかの簡単な説明"
        }}
      ],
      "category": "string - 質問のカテゴリー（例：現状把握、予算、優先順位など）",
      "weight": 1.0
    }}
  ]
}}
```

## 質問作成の重要なガイドライン

1. **具体性**: 曖昧な質問を避け、回答者が明確に答えられる質問にする
2. **段階的な選択肢**: 選択肢は段階的で、現実的な状況を反映する
3. **スコアリングロジック**:
   - 0点: 課題が深刻、または全く対応できていない状態
   - 33点: 基本的な対応はしているが改善の余地が大きい
   - 67点: かなり良い状態だが、さらに最適化できる
   - 100点: ベストプラクティスを実践している理想的な状態
4. **バランス**: 技術的な質問と戦略的な質問のバランスを取る
5. **カテゴリー分類**: 質問を論理的なカテゴリーに分類する
6. **重み付け**: 重要度に応じて質問の重みを設定（1.0が標準、重要な質問は1.5など）

## 質の高い質問の例（{industry_template.name}業界）

{chr(10).join(f"{i+1}. {q}" for i, q in enumerate(industry_template.example_questions[:3]))}

**重要**: 必ず有効なJSON形式で出力してください。JSON以外のテキストは一切含めないでください。"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,  # Increased for more detailed assessments
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text

            # Extract JSON from markdown code blocks if present
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            assessment_data = json.loads(response_text)

            # Validate assessment structure
            validation_result = self._validate_assessment(assessment_data)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Invalid assessment structure: {validation_result['error']}",
                }

            # Add metadata
            assessment_data["metadata"] = {
                "industry": industry,
                "industry_template": industry_template.name,
                "topic": topic,
                "generated_at": "auto",
                "version": "2.0",
            }

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
