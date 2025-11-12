#!/usr/bin/env python3
"""
Sample Taxonomies Creation Script - Topics and Industries

Creates sample topics and industries for demo tenants.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from uuid import uuid4
from app.core.config import settings

# Database setup
engine = create_engine(settings.DATABASE_URL)

def create_sample_taxonomies():
    """Create sample topics and industries"""
    
    # Sample topics
    sample_topics = [
        {
            "name": "マーケティング",
            "description": "マーケティング戦略と施策に関するトピック",
            "color": "#3B82F6",
            "icon": "Target"
        },
        {
            "name": "営業",
            "description": "営業プロセスと営業戦略に関するトピック",
            "color": "#10B981",
            "icon": "TrendingUp"
        },
        {
            "name": "カスタマーサクセス",
            "description": "顧客満足度と成功事例に関するトピック",
            "color": "#F59E0B",
            "icon": "Users"
        },
        {
            "name": "DX・デジタル化",
            "description": "デジタルトランスフォーメーションと技術導入に関するトピック",
            "color": "#8B5CF6",
            "icon": "Zap"
        },
        {
            "name": "組織・人材",
            "description": "組織開発と人材育成に関するトピック",
            "color": "#EC4899",
            "icon": "Users2"
        },
    ]
    
    # Sample industries
    sample_industries = [
        {
            "name": "IT・ソフトウェア",
            "description": "情報技術とソフトウェア開発企業向け",
            "color": "#3B82F6",
            "icon": "Code"
        },
        {
            "name": "金融・銀行",
            "description": "金融機関と銀行業向け",
            "color": "#10B981",
            "icon": "DollarSign"
        },
        {
            "name": "医療・ヘルスケア",
            "description": "医療機関と健康関連企業向け",
            "color": "#EF4444",
            "icon": "Heart"
        },
        {
            "name": "製造業",
            "description": "製造業と生産企業向け",
            "color": "#F59E0B",
            "icon": "Factory"
        },
        {
            "name": "小売・E-コマース",
            "description": "小売業とオンライン販売企業向け",
            "color": "#8B5CF6",
            "icon": "ShoppingCart"
        },
        {
            "name": "教育・研修",
            "description": "教育機関と研修企業向け",
            "color": "#EC4899",
            "icon": "BookOpen"
        },
    ]
    
    try:
        with engine.connect() as conn:
            # Get demo tenants
            tenants_result = conn.execute(text(
                "SELECT id FROM tenants WHERE slug IN ('demo-admin', 'demo-user', 'demo-system')"
            ))
            tenant_ids = [row[0] for row in tenants_result]
            
            if not tenant_ids:
                print("❌ Demo tenants not found. Creating sample data cancelled.")
                return
            
            # Get a system admin user for created_by
            users_result = conn.execute(text(
                "SELECT id FROM users WHERE role = 'system_admin' LIMIT 1"
            ))
            user_row = users_result.first()
            
            if not user_row:
                print("❌ System admin user not found. Creating sample data cancelled.")
                return
            
            created_by_id = user_row[0]
            
            print(f"📊 Creating sample taxonomies for {len(tenant_ids)} tenants...")
            
            # Insert topics for each tenant
            for idx, tenant_id in enumerate(tenant_ids):
                print(f"\n🏢 Tenant {idx + 1}: {tenant_id}")
                
                for topic in sample_topics:
                    topic_id = str(uuid4())
                    conn.execute(text("""
                        INSERT INTO topics (id, tenant_id, created_by, name, description, color, icon, sort_order, is_active, created_at, updated_at)
                        VALUES (:id, :tenant_id, :created_by, :name, :description, :color, :icon, :sort_order, :is_active, NOW(), NOW())
                        ON CONFLICT DO NOTHING
                    """), {
                        "id": topic_id,
                        "tenant_id": tenant_id,
                        "created_by": created_by_id,
                        "name": topic.get("name"),
                        "description": topic.get("description"),
                        "color": topic.get("color"),
                        "icon": topic.get("icon"),
                        "sort_order": sample_topics.index(topic),
                        "is_active": True,
                    })
                    print(f"  ✓ Topic: {topic['name']}")
                
                # Insert industries for each tenant
                for industry in sample_industries:
                    industry_id = str(uuid4())
                    conn.execute(text("""
                        INSERT INTO industries (id, tenant_id, created_by, name, description, color, icon, sort_order, is_active, created_at, updated_at)
                        VALUES (:id, :tenant_id, :created_by, :name, :description, :color, :icon, :sort_order, :is_active, NOW(), NOW())
                        ON CONFLICT DO NOTHING
                    """), {
                        "id": industry_id,
                        "tenant_id": tenant_id,
                        "created_by": created_by_id,
                        "name": industry.get("name"),
                        "description": industry.get("description"),
                        "color": industry.get("color"),
                        "icon": industry.get("icon"),
                        "sort_order": sample_industries.index(industry),
                        "is_active": True,
                    })
                    print(f"  ✓ Industry: {industry['name']}")
            
            conn.commit()
            
            print("\n✅ Sample taxonomies created successfully!")
            print(f"\n📋 Summary:")
            print(f"   - {len(tenant_ids)} tenants")
            print(f"   - {len(sample_topics)} topics per tenant = {len(tenant_ids) * len(sample_topics)} total topics")
            print(f"   - {len(sample_industries)} industries per tenant = {len(tenant_ids) * len(sample_industries)} total industries")
        
    except Exception as e:
        print(f"❌ Error creating sample taxonomies: {e}")
        raise

if __name__ == "__main__":
    create_sample_taxonomies()
