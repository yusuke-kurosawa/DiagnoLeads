"""
Industry Templates for AI Assessment Generation

Provides industry-specific templates and guidelines for generating high-quality assessments.
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class IndustryTemplate:
    """Industry-specific template for assessment generation"""

    name: str
    description: str
    common_pain_points: List[str]
    question_themes: List[str]
    scoring_guidelines: str
    example_questions: List[str]


# Industry templates
INDUSTRY_TEMPLATES: Dict[str, IndustryTemplate] = {
    "it_saas": IndustryTemplate(
        name="IT/SaaS",
        description="Software as a Service and IT solutions",
        common_pain_points=[
            "スケーラビリティの課題",
            "セキュリティとコンプライアンス",
            "システム統合の複雑性",
            "コスト最適化",
            "ユーザー採用率",
        ],
        question_themes=[
            "現在使用しているツールとその課題",
            "チームのサイズと技術スタック",
            "セキュリティ要件とコンプライアンス基準",
            "予算とROI期待値",
            "導入スケジュールと優先順位",
        ],
        scoring_guidelines="技術的な成熟度、緊急性、予算規模、意思決定権限に基づいてスコアリング",
        example_questions=[
            "現在のITインフラで最も大きな課題は何ですか？",
            "御社のチーム規模はどのくらいですか？",
            "セキュリティ認証（ISO27001、SOC2など）の取得状況は？",
        ],
    ),
    "consulting": IndustryTemplate(
        name="コンサルティング",
        description="Business consulting and professional services",
        common_pain_points=[
            "クライアント獲得コスト",
            "プロジェクト管理の効率化",
            "知識共有とナレッジマネジメント",
            "リソース配分の最適化",
            "品質管理と標準化",
        ],
        question_themes=[
            "現在のプロジェクト管理手法",
            "クライアント満足度の測定方法",
            "チームのスキルセットと専門性",
            "案件獲得のプロセス",
            "成長目標と課題",
        ],
        scoring_guidelines="組織規模、成長意欲、現状の課題の深刻度、予算感に基づいてスコアリング",
        example_questions=[
            "年間のプロジェクト数はどのくらいですか？",
            "プロジェクト管理で最も時間がかかっているのは？",
            "新規クライアント獲得の主なチャネルは？",
        ],
    ),
    "manufacturing": IndustryTemplate(
        name="製造業",
        description="Manufacturing and production industries",
        common_pain_points=[
            "生産効率と稼働率",
            "品質管理とトレーサビリティ",
            "サプライチェーン管理",
            "在庫最適化",
            "設備保全とダウンタイム削減",
        ],
        question_themes=[
            "生産ラインの現状と課題",
            "品質管理体制",
            "IoT/スマートファクトリーへの取り組み",
            "在庫管理と需要予測",
            "人材育成と技能継承",
        ],
        scoring_guidelines="生産規模、デジタル化の進捗度、課題の緊急性、投資意欲に基づいてスコアリング",
        example_questions=[
            "現在の生産ラインの稼働率は？",
            "品質不良率はどのくらいですか？",
            "IoTやスマートファクトリーへの取り組み状況は？",
        ],
    ),
    "ecommerce": IndustryTemplate(
        name="EC/小売",
        description="E-commerce and retail businesses",
        common_pain_points=[
            "顧客獲得コスト（CAC）の上昇",
            "カート放棄率の高さ",
            "在庫管理と物流最適化",
            "顧客ロイヤルティとリテンション",
            "マルチチャネル対応",
        ],
        question_themes=[
            "現在のEC売上と成長率",
            "主要な販売チャネル",
            "顧客獲得戦略",
            "物流とフルフィルメント",
            "データ活用とパーソナライゼーション",
        ],
        scoring_guidelines="売上規模、成長率、顧客基盤の大きさ、デジタルマーケティングの成熟度に基づいてスコアリング",
        example_questions=[
            "月間のオンライン売上高はどのくらいですか？",
            "カート放棄率の改善に取り組んでいますか？",
            "顧客データをどのように活用していますか？",
        ],
    ),
    "healthcare": IndustryTemplate(
        name="ヘルスケア",
        description="Healthcare and medical services",
        common_pain_points=[
            "患者データの管理とセキュリティ",
            "予約管理と患者満足度",
            "医療スタッフの効率化",
            "規制コンプライアンス",
            "診療記録のデジタル化",
        ],
        question_themes=[
            "電子カルテの導入状況",
            "患者管理システム",
            "HIPAA/個人情報保護対応",
            "スタッフの業務効率",
            "遠隔医療への対応",
        ],
        scoring_guidelines="施設規模、患者数、デジタル化の進捗度、コンプライアンス要件に基づいてスコアリング",
        example_questions=[
            "1日あたりの患者数はどのくらいですか？",
            "電子カルテシステムは導入済みですか？",
            "遠隔医療サービスの提供状況は？",
        ],
    ),
    "education": IndustryTemplate(
        name="教育",
        description="Education and e-learning",
        common_pain_points=[
            "学習効果の測定",
            "オンライン学習への対応",
            "学生エンゲージメント",
            "コンテンツ管理",
            "進捗管理と評価",
        ],
        question_themes=[
            "学習管理システムの利用状況",
            "オンライン/ハイブリッド授業の実施",
            "学習効果の測定方法",
            "教材のデジタル化",
            "学生サポート体制",
        ],
        scoring_guidelines="学生数、オンライン化の進捗度、予算規模、教育効果への関心度に基づいてスコアリング",
        example_questions=[
            "在籍学生数はどのくらいですか？",
            "LMS（学習管理システム）は導入していますか？",
            "学習効果をどのように測定していますか？",
        ],
    ),
    "marketing": IndustryTemplate(
        name="マーケティング",
        description="Marketing and advertising",
        common_pain_points=[
            "ROI測定の難しさ",
            "データ統合と分析",
            "マーケティングオートメーション",
            "コンテンツ制作の効率化",
            "チャネル横断での最適化",
        ],
        question_themes=[
            "現在のマーケティングツールスタック",
            "データ分析と可視化",
            "リード獲得とナーチャリング",
            "コンテンツ戦略",
            "マーケティング予算とROI",
        ],
        scoring_guidelines="マーケティング予算規模、ツール成熟度、データ活用レベル、成長目標に基づいてスコアリング",
        example_questions=[
            "月間のマーケティング予算はどのくらいですか？",
            "MAツールは導入していますか？",
            "マーケティングROIをどのように測定していますか？",
        ],
    ),
    "hr": IndustryTemplate(
        name="人事・採用",
        description="Human resources and recruitment",
        common_pain_points=[
            "優秀な人材の獲得難",
            "採用プロセスの長期化",
            "従業員エンゲージメント",
            "人事データの活用",
            "リモートワーク対応",
        ],
        question_themes=[
            "採用チャネルと手法",
            "ATS（採用管理システム）の利用",
            "従業員満足度の測定",
            "人事データの分析",
            "タレントマネジメント",
        ],
        scoring_guidelines="企業規模、採用人数、HR技術の成熟度、課題の緊急性に基づいてスコアリング",
        example_questions=[
            "年間の採用予定人数はどのくらいですか？",
            "採用管理システムは導入していますか？",
            "従業員エンゲージメントをどのように測定していますか？",
        ],
    ),
    "finance": IndustryTemplate(
        name="金融・FinTech",
        description="Financial services and FinTech",
        common_pain_points=[
            "規制対応とコンプライアンス",
            "セキュリティと不正検知",
            "顧客体験のデジタル化",
            "レガシーシステムの刷新",
            "データ分析とAI活用",
        ],
        question_themes=[
            "デジタルトランスフォーメーションの進捗",
            "セキュリティとコンプライアンス体制",
            "顧客オンボーディング",
            "データ分析とリスク管理",
            "API連携とオープンバンキング",
        ],
        scoring_guidelines="資産規模、顧客数、デジタル化の進捗度、規制要件に基づいてスコアリング",
        example_questions=[
            "顧客のオンボーディングプロセスは完全デジタル化されていますか？",
            "AI/機械学習を活用したサービスはありますか？",
            "オープンAPIを提供していますか？",
        ],
    ),
    "general": IndustryTemplate(
        name="一般企業",
        description="General business (fallback template)",
        common_pain_points=[
            "業務効率化",
            "コスト削減",
            "売上向上",
            "顧客満足度向上",
            "デジタル化の推進",
        ],
        question_themes=[
            "現在の事業課題",
            "組織規模と体制",
            "予算と優先順位",
            "ITシステムの現状",
            "改善目標",
        ],
        scoring_guidelines="企業規模、課題の深刻度、予算感、意思決定の速さに基づいてスコアリング",
        example_questions=[
            "現在の最優先課題は何ですか？",
            "従業員数はどのくらいですか？",
            "今期の重要な目標は何ですか？",
        ],
    ),
}


def get_industry_template(industry: str) -> IndustryTemplate:
    """
    Get industry template by name.

    Args:
        industry: Industry identifier (lowercase with underscores)

    Returns:
        IndustryTemplate object, defaults to 'general' if not found
    """
    industry_key = industry.lower().replace(" ", "_").replace("/", "_")
    return INDUSTRY_TEMPLATES.get(industry_key, INDUSTRY_TEMPLATES["general"])


def list_available_industries() -> List[Dict[str, str]]:
    """
    List all available industries with their descriptions.

    Returns:
        List of dictionaries with 'key', 'name', and 'description'
    """
    return [
        {"key": key, "name": template.name, "description": template.description}
        for key, template in INDUSTRY_TEMPLATES.items()
    ]
