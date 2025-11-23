"""
Database Seeding Utilities

Provides tools to seed the database with initial data for development and testing.
"""

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.auth import AuthService

logger = logging.getLogger(__name__)


class DatabaseSeeder:
    """Manages database seeding operations"""

    def __init__(self, db: Session):
        self.db = db

    def seed_all(self, data: Dict[str, List[Dict[str, Any]]], clean: bool = False):
        """
        Seed all data from configuration

        Args:
            data: Dictionary with keys 'tenants', 'users', 'assessments', etc.
            clean: If True, clean existing data before seeding
        """
        if clean:
            logger.info("🧹 Cleaning existing data...")
            self.clean_all()

        logger.info("🌱 Starting database seeding...")

        # Seed in order (respecting foreign key constraints)
        if "tenants" in data:
            self.seed_tenants(data["tenants"])

        if "users" in data:
            self.seed_users(data["users"])

        if "assessments" in data:
            self.seed_assessments(data["assessments"])

        if "questions" in data:
            self.seed_questions(data["questions"])

        if "question_options" in data:
            self.seed_question_options(data["question_options"])

        if "leads" in data:
            self.seed_leads(data["leads"])

        if "topics" in data:
            self.seed_topics(data["topics"])

        if "industries" in data:
            self.seed_industries(data["industries"])

        logger.info("✅ Database seeding completed!")

    def clean_all(self):
        """Remove all data (useful for fresh seeding)"""
        # Delete in reverse order of dependencies
        tables = [
            "ai_usage_logs",
            "error_logs",
            "answers",
            "responses",
            "question_options",
            "questions",
            "leads",
            "industries",
            "topics",
            "assessments",
            "users",
            "tenants",
        ]

        for table in tables:
            try:
                self.db.execute(text(f"DELETE FROM {table}"))
                logger.info(f"  Cleaned table: {table}")
            except Exception as e:
                logger.warning(f"  Could not clean {table}: {str(e)}")

        self.db.commit()

    def seed_tenants(self, tenants: List[Dict[str, Any]]):
        """Seed tenants"""
        logger.info("🏢 Seeding tenants...")

        for tenant_data in tenants:
            # Check if tenant already exists
            result = self.db.execute(
                text("SELECT id FROM tenants WHERE slug = :slug"),
                {"slug": tenant_data["slug"]},
            )
            existing = result.fetchone()

            if existing:
                logger.info(f"  ⏭️  Tenant '{tenant_data['name']}' already exists")
                continue

            # Insert tenant
            self.db.execute(
                text(
                    """
                INSERT INTO tenants (id, name, slug, plan, settings, created_at, updated_at)
                VALUES (:id, :name, :slug, :plan, :settings, NOW(), NOW())
            """
                ),
                {
                    "id": tenant_data["id"],
                    "name": tenant_data["name"],
                    "slug": tenant_data["slug"],
                    "plan": tenant_data.get("plan", "free"),
                    "settings": tenant_data.get("settings", "{}"),
                },
            )
            logger.info(f"  ✅ Created tenant: {tenant_data['name']}")

        self.db.commit()

    def seed_users(self, users: List[Dict[str, Any]]):
        """Seed users"""
        logger.info("👤 Seeding users...")

        for user_data in users:
            # Check if user already exists
            result = self.db.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": user_data["email"]},
            )
            existing = result.fetchone()

            if existing:
                logger.info(f"  ⏭️  User '{user_data['email']}' already exists")
                continue

            # Hash password
            password_hash = AuthService.hash_password(user_data["password"])

            # Insert user
            self.db.execute(
                text(
                    """
                INSERT INTO users (id, tenant_id, email, password_hash, name, role,
                                   failed_login_attempts, created_at, updated_at)
                VALUES (:id, :tenant_id, :email, :password_hash, :name, :role, 0, NOW(), NOW())
            """
                ),
                {
                    "id": user_data["id"],
                    "tenant_id": user_data["tenant_id"],
                    "email": user_data["email"],
                    "password_hash": password_hash,
                    "name": user_data["name"],
                    "role": user_data.get("role", "user"),
                },
            )
            logger.info(f"  ✅ Created user: {user_data['name']} ({user_data['email']})")

        self.db.commit()

    def seed_assessments(self, assessments: List[Dict[str, Any]]):
        """Seed assessments"""
        logger.info("📋 Seeding assessments...")

        for assessment_data in assessments:
            # Check if assessment already exists
            result = self.db.execute(
                text("SELECT id FROM assessments WHERE title = :title AND tenant_id = :tenant_id"),
                {"title": assessment_data["title"], "tenant_id": assessment_data["tenant_id"]},
            )
            existing = result.fetchone()

            if existing:
                logger.info(f"  ⏭️  Assessment '{assessment_data['title']}' already exists")
                continue

            # Insert assessment
            self.db.execute(
                text(
                    """
                INSERT INTO assessments (id, tenant_id, title, description, status,
                                        ai_generated, scoring_logic,
                                        created_by, updated_by, created_at, updated_at)
                VALUES (:id, :tenant_id, :title, :description, :status,
                        :ai_generated, :scoring_logic,
                        :created_by, :updated_by, NOW(), NOW())
            """
                ),
                {
                    "id": assessment_data["id"],
                    "tenant_id": assessment_data["tenant_id"],
                    "title": assessment_data["title"],
                    "description": assessment_data.get("description", ""),
                    "status": assessment_data.get("status", "draft"),
                    "ai_generated": assessment_data.get("ai_generated", "none"),
                    "scoring_logic": assessment_data.get("scoring_logic", "{}"),
                    "created_by": assessment_data["created_by"],
                    "updated_by": assessment_data["created_by"],
                },
            )
            logger.info(f"  ✅ Created assessment: {assessment_data['title']}")

        self.db.commit()
    def seed_questions(self, questions: List[Dict[str, Any]]):
        """Seed questions"""
        logger.info("❓ Seeding questions...")
    
        for question_data in questions:
            # Check if question already exists
            result = self.db.execute(
                text("SELECT id FROM questions WHERE id = :id"),
                {"id": question_data["id"]},
            )
            existing = result.fetchone()
    
            if existing:
                logger.info(f"  ⏭️  Question '{question_data['text'][:50]}...' already exists")
                continue
    
            # Insert question
            self.db.execute(
                text(
                    """
                INSERT INTO questions (id, assessment_id, text, type, "order", points, explanation, created_at)
                VALUES (:id, :assessment_id, :text, :type, :order, :points, :explanation, NOW())
            """
                ),
                {
                    "id": question_data["id"],
                    "assessment_id": question_data["assessment_id"],
                    "text": question_data["text"],
                    "type": question_data.get("type", "single_choice"),
                    "order": question_data["order"],
                    "points": question_data.get("points", 0),
                    "explanation": question_data.get("explanation", ""),
                },
            )
            logger.info(f"  ✅ Created question: {question_data['text'][:50]}...")
    
        self.db.commit()
    
    
    def seed_question_options(self, options: List[Dict[str, Any]]):
        """Seed question options"""
        logger.info("📝 Seeding question options...")
    
        for option_data in options:
            # Check if option already exists
            result = self.db.execute(
                text("SELECT id FROM question_options WHERE id = :id"),
                {"id": option_data["id"]},
            )
            existing = result.fetchone()
    
            if existing:
                logger.info(f"  ⏭️  Option '{option_data['text'][:30]}...' already exists")
                continue
    
            # Insert option
            self.db.execute(
                text(
                    """
                INSERT INTO question_options (id, question_id, text, points, "order")
                VALUES (:id, :question_id, :text, :points, :order)
            """
                ),
                {
                    "id": option_data["id"],
                    "question_id": option_data["question_id"],
                    "text": option_data["text"],
                    "points": option_data.get("points", 0),
                    "order": option_data["order"],
                },
            )
            logger.info(f"  ✅ Created option: {option_data['text'][:30]}...")
    
        self.db.commit()
    
    
    def seed_leads(self, leads: List[Dict[str, Any]]):
        """Seed leads"""
        logger.info("🎯 Seeding leads...")
    
        for lead_data in leads:
            # Check if lead already exists
            result = self.db.execute(
                text("SELECT id FROM leads WHERE email = :email AND tenant_id = :tenant_id"),
                {"email": lead_data["email"], "tenant_id": lead_data["tenant_id"]},
            )
            existing = result.fetchone()
    
            if existing:
                logger.info(f"  ⏭️  Lead '{lead_data['email']}' already exists")
                continue
    
            # Insert lead
            self.db.execute(
                text(
                    """
                INSERT INTO leads (id, tenant_id, name, email, company, job_title, phone,
                                  status, score, notes, tags, custom_fields,
                                  created_by, updated_by, assigned_to, created_at, updated_at)
                VALUES (:id, :tenant_id, :name, :email, :company, :job_title, :phone,
                        :status, :score, :notes, :tags, :custom_fields,
                        :created_by, :updated_by, :assigned_to, NOW(), NOW())
            """
                ),
                {
                    "id": lead_data["id"],
                    "tenant_id": lead_data["tenant_id"],
                    "name": lead_data["name"],
                    "email": lead_data["email"],
                    "company": lead_data.get("company", ""),
                    "job_title": lead_data.get("job_title", ""),
                    "phone": lead_data.get("phone", ""),
                    "status": lead_data.get("status", "new"),
                    "score": lead_data.get("score", 0),
                    "notes": lead_data.get("notes", ""),
                    "tags": lead_data.get("tags", "[]"),
                    "custom_fields": lead_data.get("custom_fields", "{}"),
                    "created_by": lead_data["created_by"],
                    "updated_by": lead_data.get("updated_by", lead_data["created_by"]),
                    "assigned_to": lead_data.get("assigned_to"),
                },
            )
            logger.info(f"  ✅ Created lead: {lead_data['name']} ({lead_data['email']})")

        self.db.commit()


    def seed_topics(self, topics: List[Dict[str, Any]]):
        """Seed topics"""
        logger.info("🏷️  Seeding topics...")

        for topic_data in topics:
            # Check if topic already exists
            result = self.db.execute(
                text("SELECT id FROM topics WHERE tenant_id = :tenant_id AND name = :name"),
                {"tenant_id": topic_data["tenant_id"], "name": topic_data["name"]},
            )
            existing = result.fetchone()

            if existing:
                logger.info(f"  ⏭️  Topic '{topic_data['name']}' already exists")
                continue

            # Insert topic
            self.db.execute(
                text(
                    """
                INSERT INTO topics (id, tenant_id, created_by, name, description, color, icon, sort_order, is_active, created_at, updated_at)
                VALUES (:id, :tenant_id, :created_by, :name, :description, :color, :icon, :sort_order, :is_active, NOW(), NOW())
            """
                ),
                {
                    "id": topic_data["id"],
                    "tenant_id": topic_data["tenant_id"],
                    "created_by": topic_data["created_by"],
                    "name": topic_data["name"],
                    "description": topic_data.get("description", ""),
                    "color": topic_data.get("color"),
                    "icon": topic_data.get("icon"),
                    "sort_order": topic_data.get("sort_order", 999),
                    "is_active": topic_data.get("is_active", True),
                },
            )
            logger.info(f"  ✅ Created topic: {topic_data['name']}")

        self.db.commit()


    def seed_industries(self, industries: List[Dict[str, Any]]):
        """Seed industries"""
        logger.info("🏭 Seeding industries...")

        for industry_data in industries:
            # Check if industry already exists
            result = self.db.execute(
                text("SELECT id FROM industries WHERE tenant_id = :tenant_id AND name = :name"),
                {"tenant_id": industry_data["tenant_id"], "name": industry_data["name"]},
            )
            existing = result.fetchone()

            if existing:
                logger.info(f"  ⏭️  Industry '{industry_data['name']}' already exists")
                continue

            # Insert industry
            self.db.execute(
                text(
                    """
                INSERT INTO industries (id, tenant_id, created_by, name, description, color, icon, sort_order, is_active, created_at, updated_at)
                VALUES (:id, :tenant_id, :created_by, :name, :description, :color, :icon, :sort_order, :is_active, NOW(), NOW())
            """
                ),
                {
                    "id": industry_data["id"],
                    "tenant_id": industry_data["tenant_id"],
                    "created_by": industry_data["created_by"],
                    "name": industry_data["name"],
                    "description": industry_data.get("description", ""),
                    "color": industry_data.get("color"),
                    "icon": industry_data.get("icon"),
                    "sort_order": industry_data.get("sort_order", 999),
                    "is_active": industry_data.get("is_active", True),
                },
            )
            logger.info(f"  ✅ Created industry: {industry_data['name']}")

        self.db.commit()
