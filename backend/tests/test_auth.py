"""
Test authentication endpoints
"""

from fastapi import status


class TestRegistration:
    """Test user registration"""

    def test_register_new_user_success(self, client, db_session):
        """Test successful user registration"""
        payload = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "name": "新規ユーザー",
            "tenant_name": "新規テナント株式会社",
            "tenant_slug": "new-tenant",
        }

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Check token is returned
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # Check user data
        assert "user" in data
        user = data["user"]
        assert user["email"] == payload["email"]
        assert user["name"] == payload["name"]
        assert user["role"] == "tenant_admin"
        assert "id" in user
        assert "tenant_id" in user

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email"""
        payload = {
            "email": test_user.email,  # Already exists
            "password": "SecurePass123!",
            "name": "重複ユーザー",
            "tenant_name": "重複テナント",
            "tenant_slug": "duplicate-tenant",
        }

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "メールアドレス" in response.json()["detail"]

    def test_register_duplicate_tenant_slug(self, client, test_tenant):
        """Test registration with duplicate tenant slug"""
        payload = {
            "email": "another@example.com",
            "password": "SecurePass123!",
            "name": "別のユーザー",
            "tenant_name": "別のテナント",
            "tenant_slug": test_tenant.slug,  # Already exists
        }

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "テナント" in response.json()["detail"]

    def test_register_short_password(self, client):
        """Test registration with short password"""
        payload = {
            "email": "newuser@example.com",
            "password": "short",  # Too short
            "name": "新規ユーザー",
            "tenant_name": "新規テナント",
            "tenant_slug": "new-tenant",
        }

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        payload = {
            "email": "not-an-email",  # Invalid
            "password": "SecurePass123!",
            "name": "新規ユーザー",
            "tenant_name": "新規テナント",
            "tenant_slug": "new-tenant",
        }

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_invalid_tenant_slug(self, client):
        """Test registration with invalid tenant slug"""
        payload = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "name": "新規ユーザー",
            "tenant_name": "新規テナント",
            "tenant_slug": "Invalid Slug!",  # Should be lowercase with hyphens only
        }

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    """Test user login"""

    def test_login_success(self, client, test_user):
        """Test successful login"""
        payload = {"email": test_user.email, "password": "password123"}

        response = client.post("/api/v1/auth/login/json", json=payload)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == test_user.email

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        payload = {"email": test_user.email, "password": "wrongpassword"}

        response = client.post("/api/v1/auth/login/json", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        payload = {"email": "nonexistent@example.com", "password": "password123"}

        response = client.post("/api/v1/auth/login/json", json=payload)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCurrentUser:
    """Test getting current user info"""

    def test_get_current_user_success(self, client, test_user):
        """Test getting current user with valid token"""
        from app.services.auth import AuthService

        # Create token
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_user.tenant_id),
                "email": test_user.email,
            }
        )

        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["email"] == test_user.email
        assert data["name"] == test_user.name

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid-token"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_no_token(self, client):
        """Test getting current user without token"""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
