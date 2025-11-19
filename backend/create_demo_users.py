#!/usr/bin/env python3
"""
Demo Users Creation Script - Using Direct SQL
"""

import os
import sys

sys.path.append(os.path.dirname(__file__))

from uuid import uuid4

from sqlalchemy import create_engine, text

from app.core.config import settings
from app.services.auth import AuthService

# Database setup
engine = create_engine(settings.DATABASE_URL)


def create_demo_users():
    demo_accounts = [
        {
            "tenant_name": "Demo Tenant - Admin",
            "tenant_slug": "demo-admin",
            "tenant_plan": "enterprise",
            "email": "admin@demo.example.com",
            "password": "Admin@Demo123",
            "name": "管理者ユーザー",
            "role": "tenant_admin",
        },
        {
            "tenant_name": "Demo Tenant - User",
            "tenant_slug": "demo-user",
            "tenant_plan": "pro",
            "email": "user@demo.example.com",
            "password": "User@Demo123",
            "name": "一般ユーザー",
            "role": "user",
        },
        {
            "tenant_name": "Demo Tenant - System",
            "tenant_slug": "demo-system",
            "tenant_plan": "enterprise",
            "email": "system@demo.example.com",
            "password": "System@Demo123",
            "name": "システム管理者",
            "role": "system_admin",
        },
    ]

    try:
        with engine.connect() as conn:
            print("🔍 Checking for existing demo users...")

            # Delete existing demo users and tenants
            for account in demo_accounts:
                # Delete existing user
                conn.execute(
                    text("DELETE FROM users WHERE email = :email"),
                    {"email": account["email"]},
                )
                # Delete existing tenant
                conn.execute(
                    text("DELETE FROM tenants WHERE slug = :slug"),
                    {"slug": account["tenant_slug"]},
                )

            conn.commit()

            # Create demo accounts
            for account in demo_accounts:
                tenant_id = str(uuid4())
                user_id = str(uuid4())

                print(f"🏢 Creating tenant: {account['tenant_name']}")
                # Create tenant
                conn.execute(
                    text(
                        """
                    INSERT INTO tenants (id, name, slug, plan, settings, created_at, updated_at)
                    VALUES (:id, :name, :slug, :plan, '{}', NOW(), NOW())
                """
                    ),
                    {
                        "id": tenant_id,
                        "name": account["tenant_name"],
                        "slug": account["tenant_slug"],
                        "plan": account["tenant_plan"],
                    },
                )

                print(f"👤 Creating user: {account['name']} ({account['role']})")
                # Create user
                password_hash = AuthService.hash_password(account["password"])
                conn.execute(
                    text(
                        """
                    INSERT INTO users (id, tenant_id, email, password_hash, name, role, failed_login_attempts, created_at, updated_at)
                    VALUES (:id, :tenant_id, :email, :password_hash, :name, :role, 0, NOW(), NOW())
                """
                    ),
                    {
                        "id": user_id,
                        "tenant_id": tenant_id,
                        "email": account["email"],
                        "password_hash": password_hash,
                        "name": account["name"],
                        "role": account["role"],
                    },
                )

            conn.commit()

            print("\n✅ Demo users created successfully!")
            print("\n📋 Demo Account Credentials:\n")
            for account in demo_accounts:
                print(f"【{account['name']}】({account['role']})")
                print(f"  Email: {account['email']}")
                print(f"  Password: {account['password']}")
                print(f"  Tenant: {account['tenant_name']}")
                print()

    except Exception as e:
        print(f"❌ Error creating demo users: {e}")
        raise


if __name__ == "__main__":
    create_demo_users()
