"""
Development Seed Data

Initial data for local development environment.
Includes demo users, sample tenants, and test assessments.
"""

from uuid import uuid4

# Generate consistent UUIDs for relationships
TENANT_ADMIN_ID = "c31fe212-59c8-4265-b2e3-5491891e2764"
TENANT_USER_ID = "a7b8c9d0-e1f2-4a5b-8c9d-0e1f2a3b4c5d"
TENANT_SYSTEM_ID = "d8e9f0a1-b2c3-4d5e-9f0a-1b2c3d4e5f6a"

USER_ADMIN_ID = "745a335c-dc01-4189-9b0e-6c36fb51ac41"
USER_USER_ID = "b3c4d5e6-f7a8-4b9c-a5d6-e7f8a9b0c1d2"
USER_SYSTEM_ID = "e5f6a7b8-c9d0-4e1f-b7a8-c9d0e1f2a3b4"

# Use fixed UUIDs for assessments (these are created by the assessment seed)
# If running seed for the first time with --clean, these will be the IDs
# If assessments already exist, we'll use their existing IDs
ASSESSMENT_1_ID = "29fceac3-0f73-4217-b420-dbffb8fbdce5"  # 営業力診断
ASSESSMENT_2_ID = "9f207884-2f1c-4d47-ab79-80a991801a3f"  # マーケティング成熟度

# Questions for Assessment 1
Q1_ID = str(uuid4())
Q2_ID = str(uuid4())
Q3_ID = str(uuid4())

# Question Options
Q1_OPT1_ID = str(uuid4())
Q1_OPT2_ID = str(uuid4())
Q1_OPT3_ID = str(uuid4())
Q2_OPT1_ID = str(uuid4())
Q2_OPT2_ID = str(uuid4())
Q2_OPT3_ID = str(uuid4())
Q3_OPT1_ID = str(uuid4())
Q3_OPT2_ID = str(uuid4())
Q3_OPT3_ID = str(uuid4())

# Leads
LEAD_1_ID = str(uuid4())
LEAD_2_ID = str(uuid4())
LEAD_3_ID = str(uuid4())

# Topics and Industries (Master Data)
# Topics for Admin Tenant
TOPIC_1_ID = str(uuid4())
TOPIC_2_ID = str(uuid4())
TOPIC_3_ID = str(uuid4())
TOPIC_4_ID = str(uuid4())
TOPIC_5_ID = str(uuid4())

# Industries for Admin Tenant
INDUSTRY_1_ID = str(uuid4())
INDUSTRY_2_ID = str(uuid4())
INDUSTRY_3_ID = str(uuid4())
INDUSTRY_4_ID = str(uuid4())
INDUSTRY_5_ID = str(uuid4())
INDUSTRY_6_ID = str(uuid4())


SEED_DATA = {
    "tenants": [
        {
            "id": TENANT_ADMIN_ID,
            "name": "Demo Tenant - Admin",
            "slug": "demo-admin",
            "plan": "enterprise",
            "settings": "{}",
        },
        {
            "id": TENANT_USER_ID,
            "name": "Demo Tenant - User",
            "slug": "demo-user",
            "plan": "pro",
            "settings": "{}",
        },
        {
            "id": TENANT_SYSTEM_ID,
            "name": "Demo Tenant - System",
            "slug": "demo-system",
            "plan": "enterprise",
            "settings": "{}",
        },
    ],
    "users": [
        {
            "id": USER_ADMIN_ID,
            "tenant_id": TENANT_ADMIN_ID,
            "email": "admin@demo.example.com",
            "password": "Admin@Demo123",
            "name": "管理者ユーザー",
            "role": "tenant_admin",
        },
        {
            "id": USER_USER_ID,
            "tenant_id": TENANT_USER_ID,
            "email": "user@demo.example.com",
            "password": "User@Demo123",
            "name": "一般ユーザー",
            "role": "user",
        },
        {
            "id": USER_SYSTEM_ID,
            "tenant_id": TENANT_SYSTEM_ID,
            "email": "system@demo.example.com",
            "password": "System@Demo123",
            "name": "システム管理者",
            "role": "system_admin",
        },
    ],
    "assessments": [
        {
            "id": ASSESSMENT_1_ID,  # Fixed UUID
            "tenant_id": TENANT_ADMIN_ID,
            "title": "サンプル診断：営業力診断",
            "description": "営業チームの強みと改善点を診断します",
            "status": "published",
            "ai_generated": "none",
            "scoring_logic": "{}",
            "created_by": USER_ADMIN_ID,
        },
        {
            "id": ASSESSMENT_2_ID,  # Fixed UUID
            "tenant_id": TENANT_ADMIN_ID,
            "title": "サンプル診断：マーケティング成熟度",
            "description": "マーケティング活動の成熟度を評価します",
            "status": "draft",
            "ai_generated": "none",
            "scoring_logic": "{}",
            "created_by": USER_ADMIN_ID,
        },
    ],
    "questions": [
        {
            "id": Q1_ID,
            "assessment_id": ASSESSMENT_1_ID,
            "text": "あなたの営業チームの規模を教えてください",
            "type": "single_choice",
            "order": 1,
            "points": 10,
            "explanation": "チーム規模によって最適な営業戦略が異なります",
        },
        {
            "id": Q2_ID,
            "assessment_id": ASSESSMENT_1_ID,
            "text": "営業プロセスはどの程度標準化されていますか？",
            "type": "single_choice",
            "order": 2,
            "points": 10,
            "explanation": "プロセスの標準化は営業効率に直結します",
        },
        {
            "id": Q3_ID,
            "assessment_id": ASSESSMENT_1_ID,
            "text": "CRMツールを活用していますか？",
            "type": "single_choice",
            "order": 3,
            "points": 10,
            "explanation": "CRM活用は顧客管理の鍵です",
        },
    ],
    "question_options": [
        # Question 1 Options
        {
            "id": Q1_OPT1_ID,
            "question_id": Q1_ID,
            "text": "1-5名",
            "points": 5,
            "order": 1,
        },
        {
            "id": Q1_OPT2_ID,
            "question_id": Q1_ID,
            "text": "6-20名",
            "points": 10,
            "order": 2,
        },
        {
            "id": Q1_OPT3_ID,
            "question_id": Q1_ID,
            "text": "21名以上",
            "points": 15,
            "order": 3,
        },
        # Question 2 Options
        {
            "id": Q2_OPT1_ID,
            "question_id": Q2_ID,
            "text": "全く標準化されていない",
            "points": 0,
            "order": 1,
        },
        {
            "id": Q2_OPT2_ID,
            "question_id": Q2_ID,
            "text": "部分的に標準化されている",
            "points": 10,
            "order": 2,
        },
        {
            "id": Q2_OPT3_ID,
            "question_id": Q2_ID,
            "text": "完全に標準化されている",
            "points": 20,
            "order": 3,
        },
        # Question 3 Options
        {
            "id": Q3_OPT1_ID,
            "question_id": Q3_ID,
            "text": "使用していない",
            "points": 0,
            "order": 1,
        },
        {
            "id": Q3_OPT2_ID,
            "question_id": Q3_ID,
            "text": "一部で使用している",
            "points": 10,
            "order": 2,
        },
        {
            "id": Q3_OPT3_ID,
            "question_id": Q3_ID,
            "text": "全社で活用している",
            "points": 20,
            "order": 3,
        },
    ],
    "leads": [
        {
            "id": LEAD_1_ID,
            "tenant_id": TENANT_ADMIN_ID,
            "name": "山田 太郎",
            "email": "yamada@example.com",
            "company": "株式会社サンプル",
            "job_title": "営業部長",
            "phone": "03-1234-5678",
            "status": "qualified",
            "score": 85,
            "notes": "診断結果が良好。フォローアップ推奨",
            "tags": '["ホットリード", "大企業"]',
            "custom_fields": '{"industry": "IT", "employees": "500+"}',
            "created_by": USER_ADMIN_ID,
            "assigned_to": USER_ADMIN_ID,
        },
        {
            "id": LEAD_2_ID,
            "tenant_id": TENANT_ADMIN_ID,
            "name": "佐藤 花子",
            "email": "sato@demo.co.jp",
            "company": "デモ株式会社",
            "job_title": "マーケティングマネージャー",
            "phone": "06-9876-5432",
            "status": "new",
            "score": 65,
            "notes": "初回コンタクト待ち",
            "tags": '["中小企業"]',
            "custom_fields": '{"industry": "製造業", "employees": "50-100"}',
            "created_by": USER_ADMIN_ID,
            "assigned_to": USER_ADMIN_ID,
        },
        {
            "id": LEAD_3_ID,
            "tenant_id": TENANT_ADMIN_ID,
            "name": "鈴木 一郎",
            "email": "suzuki@testcorp.jp",
            "company": "テスト商事",
            "job_title": "代表取締役",
            "phone": "03-5555-7777",
            "status": "contacted",
            "score": 75,
            "notes": "次回ミーティング予定",
            "tags": '["エンタープライズ", "決裁者"]',
            "custom_fields": '{"industry": "商社", "employees": "200+"}',
            "created_by": USER_ADMIN_ID,
            "assigned_to": USER_ADMIN_ID,
        },
    ],
    "topics": [
        {
            "id": TOPIC_1_ID,
            "tenant_id": TENANT_ADMIN_ID,
            "created_by": USER_ADMIN_ID,
            "name": "マーケティング",
            "description": "マーケティング戦略と施策に関するトピック",
            "color": "#3B82F6",
            "icon": "Target",
            "sort_order": 0,
            "is_active": True,
        },
        {
            "id": TOPIC_2_ID,
            "tenant_id": TENANT_ADMIN_ID,
            "created_by": USER_ADMIN_ID,
            "name": "営業",
            "description": "営業プロセスと営業戦略に関するトピック",
            "color": "#10B981",
            "icon": "TrendingUp",
            "sort_order": 1,
            "is_active": True,
        },
        {
            "id": TOPIC_3_ID,
            "tenant_id": TENANT_ADMIN_ID,
            "created_by": USER_ADMIN_ID,
            "name": "カスタマーサクセス",
            "description": "顧客満足度と成功事例に関するトピック",
            "color": "#F59E0B",
            "icon": "Users",
            "sort_order": 2,
            "is_active": True,
        },
        {
            "id": TOPIC_4_ID,
            "tenant_id": TENANT_ADMIN_ID,
            "created_by": USER_ADMIN_ID,
            "name": "DX・デジタル化",
            "description": "デジタルトランスフォーメーションと技術導入に関するトピック",
            "color": "#8B5CF6",
            "icon": "Zap",
            "sort_order": 3,
            "is_active": True,
        },
        {
            "id": TOPIC_5_ID,
            "tenant_id": TENANT_ADMIN_ID,
            "created_by": USER_ADMIN_ID,
            "name": "組織・人材",
            "description": "組織開発と人材育成に関するトピック",
            "color": "#EC4899",
            "icon": "Users2",
            "sort_order": 4,
            "is_active": True,
        },
    ],
    "industries": [
        {
            "id": INDUSTRY_1_ID,
            "tenant_id": TENANT_ADMIN_ID,
            "created_by": USER_ADMIN_ID,
            "name": "IT・ソフトウェア",
            "description": "情報技術とソフトウェア開発企業向け",
            "color": "#3B82F6",
            "icon": "Code",
            "sort_order": 0,
            "is_active": True,
        },
        {
            "id": INDUSTRY_2_ID,
            "tenant_id": TENANT_ADMIN_ID,
            "created_by": USER_ADMIN_ID,
            "name": "金融・銀行",
            "description": "金融機関と銀行業向け",
            "color": "#10B981",
            "icon": "DollarSign",
            "sort_order": 1,
            "is_active": True,
        },
        {
            "id": INDUSTRY_3_ID,
            "tenant_id": TENANT_ADMIN_ID,
            "created_by": USER_ADMIN_ID,
            "name": "医療・ヘルスケア",
            "description": "医療機関と健康関連企業向け",
            "color": "#EF4444",
            "icon": "Heart",
            "sort_order": 2,
            "is_active": True,
        },
        {
            "id": INDUSTRY_4_ID,
            "tenant_id": TENANT_ADMIN_ID,
            "created_by": USER_ADMIN_ID,
            "name": "製造業",
            "description": "製造業と生産企業向け",
            "color": "#F59E0B",
            "icon": "Factory",
            "sort_order": 3,
            "is_active": True,
        },
        {
            "id": INDUSTRY_5_ID,
            "tenant_id": TENANT_ADMIN_ID,
            "created_by": USER_ADMIN_ID,
            "name": "小売・E-コマース",
            "description": "小売業とオンライン販売企業向け",
            "color": "#8B5CF6",
            "icon": "ShoppingCart",
            "sort_order": 4,
            "is_active": True,
        },
        {
            "id": INDUSTRY_6_ID,
            "tenant_id": TENANT_ADMIN_ID,
            "created_by": USER_ADMIN_ID,
            "name": "教育・研修",
            "description": "教育機関と研修企業向け",
            "color": "#EC4899",
            "icon": "BookOpen",
            "sort_order": 5,
            "is_active": True,
        },
    ],
}
