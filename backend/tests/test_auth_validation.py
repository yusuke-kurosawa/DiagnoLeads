"""
Test authentication password validation
"""

from fastapi import status


class TestPasswordValidation:
    """Test password strength validation"""

    def test_register_weak_password_no_uppercase(self, client):
        """Test registration with password missing uppercase letter"""
        payload = {
            "email": "newuser@example.com",
            "password": "weakpass123",  # No uppercase
            "name": "新規ユーザー",
            "tenant_name": "新規テナント",
            "tenant_slug": "new-tenant-1",
        }

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        errors = response.json()["detail"]
        assert any("password" in str(error).lower() for error in errors)

    def test_register_weak_password_no_lowercase(self, client):
        """Test registration with password missing lowercase letter"""
        payload = {
            "email": "newuser@example.com",
            "password": "WEAKPASS123",  # No lowercase
            "name": "新規ユーザー",
            "tenant_name": "新規テナント",
            "tenant_slug": "new-tenant-2",
        }

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_weak_password_no_number(self, client):
        """Test registration with password missing number"""
        payload = {
            "email": "newuser@example.com",
            "password": "WeakPassword",  # No number
            "name": "新規ユーザー",
            "tenant_name": "新規テナント",
            "tenant_slug": "new-tenant-3",
        }

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_strong_password(self, client):
        """Test registration with strong password"""
        payload = {
            "email": "stronguser@example.com",
            "password": "StrongPass123!",  # Meets all requirements
            "name": "強力ユーザー",
            "tenant_name": "強力テナント",
            "tenant_slug": "strong-tenant",
        }

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_201_CREATED

    def test_register_password_with_special_characters(self, client):
        """Test registration with password containing special characters"""
        payload = {
            "email": "specialuser@example.com",
            "password": "Special@Pass123!",  # Includes special characters
            "name": "特殊文字ユーザー",
            "tenant_name": "特殊文字テナント",
            "tenant_slug": "special-tenant",
        }

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
