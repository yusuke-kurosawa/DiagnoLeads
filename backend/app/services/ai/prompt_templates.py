"""
AI Prompt Templates

Centralized prompt templates for consistency and version control.
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class IndustryTemplateData:
    """Data structure for industry template information"""

    name: str
    description: str
    common_pain_points: List[str]
    question_themes: List[str]
    scoring_guidelines: str
    example_questions: List[str]


@dataclass
class LeadAnalysisTemplateData:
    """Data structure for lead analysis template information"""

    industry: str
    key_signals: List[str]
    qualification_criteria: List[str]
    talking_points_themes: List[str]


class PromptTemplates:
    """Centralized prompt templates for AI operations"""

    VERSION = "2.1"

    @staticmethod
    def build_assessment_generation_prompt(
        topic: str,
        num_questions: int,
        industry_template: IndustryTemplateData,
    ) -> str:
        """
        Build prompt for assessment generation.

        Args:
            topic: Sanitized topic string
            num_questions: Number of questions to generate
            industry_template: Industry-specific template data

        Returns:
            Formatted prompt string
        """
        return f"""あなたは{industry_template.name}業界のエキスパートです。以下の要件に基づいて、プロフェッショナルな診断（Assessment）をJSON形式で生成してください。

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

    @staticmethod
    def build_lead_analysis_prompt(
        assessment_responses: Dict[str, Any],
        assessment_title: str,
        lead_template: LeadAnalysisTemplateData,
    ) -> str:
        """
        Build prompt for lead analysis.

        Args:
            assessment_responses: Sanitized response data
            assessment_title: Assessment title
            lead_template: Lead analysis template data

        Returns:
            Formatted prompt string
        """
        import json

        responses_text = json.dumps(assessment_responses, indent=2, ensure_ascii=False)

        return f"""あなたは{lead_template.industry}業界のセールスエキスパートです。
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

    @staticmethod
    def build_rephrase_prompt(
        text: str,
        style: str,
        target_audience: str,
    ) -> str:
        """
        Build prompt for content rephrasing.

        Args:
            text: Sanitized text to rephrase
            style: Writing style
            target_audience: Target audience

        Returns:
            Formatted prompt string
        """
        return f"""Rephrase the following text in a {style} style for {target_audience} audience.
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
