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
from app.services.ai.lead_analysis_templates import (
    get_lead_analysis_template,
    get_recommended_action,
)


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

    def _calculate_priority_level(self, score: int, hot_lead: bool) -> str:
        """
        Calculate automatic priority level based on lead score and hot lead status.

        Args:
            score: Lead score (0-100)
            hot_lead: Whether this is a hot lead

        Returns:
            Priority level: critical|high|medium|low
        """
        if hot_lead and score >= 90:
            return "critical"
        elif score >= 80:
            return "high"
        elif score >= 60:
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

    async def analyze_lead_insights(
        self,
        assessment_responses: Dict[str, Any],
        assessment_title: str = "Assessment",
        industry: str = "general",
    ) -> Dict[str, Any]:
        """
        Analyze lead responses and generate insights using Claude AI with industry-specific context.

        Args:
            assessment_responses: Dictionary of question IDs to selected answers
            assessment_title: Name of the assessment
            industry: Target industry for context

        Returns:
            Dictionary containing:
            - insights: List of identified issues/needs
            - recommendation: Recommended action
            - score: Overall lead quality score (0-100)
            - recommended_action: Industry-specific next action
            - priority_level: Automatic priority (critical|high|medium|low)
            - follow_up_timing: When to follow up
        """
        # Get industry-specific template
        lead_template = get_lead_analysis_template(industry)
        responses_text = json.dumps(assessment_responses, indent=2, ensure_ascii=False)

        # Build enhanced prompt with industry context
        prompt = f"""あなたは{lead_template.industry}業界のセールスエキスパートです。
以下の診断回答を分析し、リード（見込み顧客）に関する詳細なインサイトをJSON形式で提供してください。

## 診断情報

**診断名**: {assessment_title}
**業界**: {lead_template.industry}
**回答データ**: {responses_text}

## 業界固有の重要シグナル（これらに注目して分析）

{chr(10).join(f"- {signal}" for signal in lead_template.key_signals)}

## リード評価基準（{lead_template.industry}業界）

{chr(10).join(f"- {criteria}" for criteria in lead_template.qualification_criteria)}

## 重点トークテーマ

{chr(10).join(f"- {theme}" for theme in lead_template.talking_points_themes)}

## 出力形式（JSON）

```json
{{
  "overall_score": "number (0-100) - 総合スコア（上記の評価基準に基づく）",
  "hot_lead": "boolean - ホットリードか（75点以上で明確なニーズあり）",
  "identified_needs": [
    {{
      "area": "string - 課題領域",
      "description": "string - 具体的な課題内容と緊急性",
      "priority": "high|medium|low"
    }}
  ],
  "recommendation": "string - 営業担当者への推奨アクション（具体的に）",
  "key_talking_points": [
    "string - 商談で使える具体的なトークポイント"
  ]
}}
```

## 分析ガイドライン

1. **スコアリング精度**: 回答内容から、予算・権限・ニーズ・タイムラインを総合的に評価
2. **ニーズの具体化**: 抽象的な「課題がある」ではなく、何がどう困っているかを明確化
3. **緊急性の判断**: 導入タイミングや課題の深刻度から優先度を判定
4. **トークポイントの実用性**: 実際の商談で使える、回答に基づいた具体的な提案ポイント
5. **業界文脈**: {lead_template.industry}業界特有の課題や用語を考慮

**重要**: 必ず有効なJSON形式で出力してください。JSON以外のテキストは一切含めないでください。"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1500,  # Increased for more detailed analysis
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

            insights_data = json.loads(response_text)

            # Add industry-specific recommended action
            score = insights_data.get("overall_score", 0)
            insights_data["recommended_action"] = get_recommended_action(score, industry)

            # Add automatic priority level
            hot_lead = insights_data.get("hot_lead", False)
            priority_level = self._calculate_priority_level(score, hot_lead)
            insights_data["priority_level"] = priority_level

            # Add follow-up timing recommendation
            insights_data["follow_up_timing"] = self._calculate_follow_up_timing(
                score, priority_level
            )

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
