"""
Test Seed Data

Minimal data for automated testing.
"""

from uuid import uuid4

TEST_TENANT_ID = str(uuid4())
TEST_USER_ID = str(uuid4())


SEED_DATA = {
    "tenants": [
        {
            "id": TEST_TENANT_ID,
            "name": "Test Tenant",
            "slug": "test-tenant",
            "plan": "free",
            "settings": "{}",
        },
    ],
    "users": [
        {
            "id": TEST_USER_ID,
            "tenant_id": TEST_TENANT_ID,
            "email": "test@example.com",
            "password": "Test@123456",
            "name": "Test User",
            "role": "tenant_admin",
        },
    ],
    "assessments": [],
}
