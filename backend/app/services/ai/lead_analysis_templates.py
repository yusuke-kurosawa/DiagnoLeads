"""
Lead Analysis Templates for AI-powered insights

Provides industry-specific templates for analyzing lead responses and generating insights.
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class LeadAnalysisTemplate:
    """Industry-specific template for lead analysis"""

    industry: str
    key_signals: List[str]  # What to look for in responses
    qualification_criteria: List[str]  # What makes a high-quality lead
    recommended_actions: Dict[str, str]  # Score range -> recommended action
    talking_points_themes: List[str]  # Key themes for sales conversations


# Industry-specific lead analysis templates
LEAD_ANALYSIS_TEMPLATES: Dict[str, LeadAnalysisTemplate] = {
    "it_saas": LeadAnalysisTemplate(
        industry="IT/SaaS",
        key_signals=[
            "現在のシステムの課題や不満",
            "技術スタックとツールの成熟度",
            "予算規模と承認プロセス",
            "導入タイムライン",
            "セキュリティ・コンプライアンス要件",
            "チームサイズと技術力",
        ],
        qualification_criteria=[
            "明確な課題を認識している",
            "予算と決裁権限がある",
            "3ヶ月以内の導入を検討",
            "競合製品と比較検討中",
            "技術的な理解度が高い",
        ],
        recommended_actions={
            "80-100": "即座にデモを提案。意思決定者との商談を設定。ROI試算を準備。",
            "60-79": "詳細な資料を送付。ユースケースを共有。1週間以内にフォローアップ。",
            "40-59": "ナーチャリングメールシーケンスに追加。成功事例を定期的に共有。",
            "0-39": "情報提供のみ。四半期ごとのチェックイン。",
        },
        talking_points_themes=[
            "システム統合のシンプルさ",
            "スケーラビリティとパフォーマンス",
            "セキュリティ認証とコンプライアンス",
            "TCO削減とROI",
            "導入事例と成功ストーリー",
        ],
    ),
    "consulting": LeadAnalysisTemplate(
        industry="コンサルティング",
        key_signals=[
            "プロジェクト管理の課題",
            "クライアント獲得コスト",
            "品質管理とナレッジ共有",
            "チームのスキルギャップ",
            "成長目標と制約",
        ],
        qualification_criteria=[
            "明確な業務課題がある",
            "年間10プロジェクト以上",
            "品質向上に投資意欲あり",
            "チームが10名以上",
            "デジタル化に前向き",
        ],
        recommended_actions={
            "80-100": "具体的なワークショップを提案。ROI試算を提示。",
            "60-79": "ベストプラクティスガイドを提供。ウェビナーに招待。",
            "40-59": "事例研究を定期配信。業界動向レポートを共有。",
            "0-39": "ニュースレター登録を提案。",
        },
        talking_points_themes=[
            "プロジェクト効率化",
            "品質標準化",
            "ナレッジマネジメント",
            "チーム協業",
            "クライアント満足度向上",
        ],
    ),
    "manufacturing": LeadAnalysisTemplate(
        industry="製造業",
        key_signals=[
            "生産効率と稼働率",
            "品質不良率",
            "設備保全の課題",
            "在庫管理の問題",
            "デジタル化の進捗",
        ],
        qualification_criteria=[
            "生産ライン数が3以上",
            "年間売上10億円以上",
            "IoT/DX投資予算あり",
            "品質改善に課題感",
            "経営層の理解あり",
        ],
        recommended_actions={
            "80-100": "工場視察を提案。PoC（概念実証）を提案。",
            "60-79": "デモンストレーション実施。投資回収シミュレーション提供。",
            "40-59": "成功事例の詳細を共有。業界セミナーに招待。",
            "0-39": "情報収集フェーズ。定期的なタッチポイント維持。",
        },
        talking_points_themes=[
            "生産性向上",
            "品質安定化",
            "予知保全",
            "在庫最適化",
            "スマートファクトリー",
        ],
    ),
    "ecommerce": LeadAnalysisTemplate(
        industry="EC/小売",
        key_signals=[
            "月間売上規模",
            "カート放棄率",
            "顧客獲得コスト",
            "リピート率",
            "マルチチャネル対応",
        ],
        qualification_criteria=[
            "月商1000万円以上",
            "CVR改善に課題感",
            "データ活用に前向き",
            "成長フェーズにある",
            "マーケティング予算あり",
        ],
        recommended_actions={
            "80-100": "無料トライアルを提案。CVR改善施策を提示。",
            "60-79": "A/Bテスト事例を共有。コンサルティング提案。",
            "40-59": "EC最適化ガイドを提供。定期的なヒント配信。",
            "0-39": "業界トレンドレポート配信。",
        },
        talking_points_themes=[
            "CVR向上",
            "LTV最大化",
            "パーソナライゼーション",
            "オムニチャネル",
            "データドリブン経営",
        ],
    ),
    "marketing": LeadAnalysisTemplate(
        industry="マーケティング",
        key_signals=[
            "マーケティング予算規模",
            "ROI測定の課題",
            "ツールスタックの成熟度",
            "リード獲得数とCV率",
            "データ統合の課題",
        ],
        qualification_criteria=[
            "月間予算100万円以上",
            "ROI測定に課題感",
            "MA導入検討中",
            "チーム5名以上",
            "データ活用意欲あり",
        ],
        recommended_actions={
            "80-100": "マーケティング監査を提案。ROI改善プランを提示。",
            "60-79": "ツール比較資料を提供。デモアカウント発行。",
            "40-59": "ベストプラクティスガイド配信。ウェビナー招待。",
            "0-39": "マーケティングトレンドレポート配信。",
        },
        talking_points_themes=[
            "ROI測定と最適化",
            "マーケティングオートメーション",
            "データ統合と可視化",
            "リード育成",
            "アトリビューション分析",
        ],
    ),
}


def get_lead_analysis_template(industry: str) -> LeadAnalysisTemplate:
    """
    Get lead analysis template by industry.

    Args:
        industry: Industry identifier

    Returns:
        LeadAnalysisTemplate object, defaults to general template if not found
    """
    industry_key = industry.lower().replace(" ", "_").replace("/", "_")

    # Default template for unknown industries
    if industry_key not in LEAD_ANALYSIS_TEMPLATES:
        return LeadAnalysisTemplate(
            industry="一般",
            key_signals=[
                "現在の課題認識",
                "予算と承認プロセス",
                "導入タイムライン",
                "意思決定者の関与",
                "競合比較状況",
            ],
            qualification_criteria=[
                "明確な課題がある",
                "予算がある",
                "6ヶ月以内の導入",
                "意思決定権限あり",
                "情報収集が進んでいる",
            ],
            recommended_actions={
                "80-100": "即座に商談を設定。提案書を準備。",
                "60-79": "詳細資料を送付。1週間以内にフォローアップ。",
                "40-59": "ナーチャリングシーケンスに追加。",
                "0-39": "定期的な情報提供のみ。",
            },
            talking_points_themes=[
                "課題解決の具体的アプローチ",
                "投資対効果",
                "導入の容易さ",
                "サポート体制",
                "成功事例",
            ],
        )

    return LEAD_ANALYSIS_TEMPLATES[industry_key]


def get_recommended_action(score: int, industry: str) -> str:
    """
    Get recommended action based on lead score and industry.

    Args:
        score: Lead score (0-100)
        industry: Industry identifier

    Returns:
        Recommended action string
    """
    template = get_lead_analysis_template(industry)

    if score >= 80:
        return template.recommended_actions["80-100"]
    elif score >= 60:
        return template.recommended_actions["60-79"]
    elif score >= 40:
        return template.recommended_actions["40-59"]
    else:
        return template.recommended_actions["0-39"]
