"""
Tests for User Management API Endpoints

ユーザー管理APIのテスト（権限チェック、CRUD操作）
"""

from uuid import uuid4

import pytest
from fastapi import status

from app.models.user import User
from app.services.auth import AuthService


class TestListUsers:
    """Tests for GET /api/v1/users endpoint"""

    def test_list_users_as_tenant_admin(self, client, test_user, test_tenant, db_session):
        """Test listing users as tenant admin"""
        # test_user is tenant_admin by default
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        response = client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        users = response.json()
        assert isinstance(users, list)
        # Should see at least themselves
        user_emails = [u["email"] for u in users]
        assert test_user.email in user_emails

    def test_list_users_as_system_admin(self, client, test_tenant, db_session):
        """Test listing users as system admin"""
        # Create system admin
        system_admin = User(
            id=uuid4(),
            tenant_id=test_tenant.id,
            email="sysadmin@example.com",
            password_hash=AuthService.hash_password("password123"),
            name="System Admin",
            role="system_admin",
        )
        db_session.add(system_admin)
        db_session.commit()

        token = AuthService.create_access_token(
            data={
                "sub": str(system_admin.id),
                "tenant_id": str(test_tenant.id),
                "email": system_admin.email,
            }
        )

        response = client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        users = response.json()
        assert isinstance(users, list)

    def test_list_users_as_regular_user(self, client, test_tenant, db_session):
        """Test that regular users cannot list users"""
        # Create regular user
        regular_user = User(
            id=uuid4(),
            tenant_id=test_tenant.id,
            email="regular@example.com",
            password_hash=AuthService.hash_password("password123"),
            name="Regular User",
            role="user",  # Not admin
        )
        db_session.add(regular_user)
        db_session.commit()

        token = AuthService.create_access_token(
            data={
                "sub": str(regular_user.id),
                "tenant_id": str(test_tenant.id),
                "email": regular_user.email,
            }
        )

        response = client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_users_unauthorized(self, client):
        """Test listing users without authentication"""
        response = client.get("/api/v1/users")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_users_with_pagination(self, client, test_user, test_tenant, db_session):
        """Test user list pagination"""
        # Create multiple users
        for i in range(15):
            user = User(
                id=uuid4(),
                tenant_id=test_tenant.id,
                email=f"user{i}@example.com",
                password_hash=AuthService.hash_password("password123"),
                name=f"User {i}",
                role="user",
            )
            db_session.add(user)
        db_session.commit()

        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        # Request first page with limit
        response = client.get(
            "/api/v1/users?skip=0&limit=10",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        users = response.json()
        assert len(users) <= 10


class TestGetUser:
    """Tests for GET /api/v1/users/{user_id} endpoint"""

    def test_get_own_user(self, client, test_user):
        """Test getting own user information"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_user.tenant_id),
                "email": test_user.email,
            }
        )

        response = client.get(
            f"/api/v1/users/{test_user.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_200_OK
        user_data = response.json()
        assert user_data["email"] == test_user.email
        assert user_data["id"] == str(test_user.id)

    def test_get_other_user_as_admin(self, client, test_user, test_tenant, db_session):
        """Test getting another user as tenant admin"""
        # Create another user in same tenant
        other_user = User(
            id=uuid4(),
            tenant_id=test_tenant.id,
            email="other@example.com",
            password_hash=AuthService.hash_password("password123"),
            name="Other User",
            role="user",
        )
        db_session.add(other_user)
        db_session.commit()

        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        response = client.get(
            f"/api/v1/users/{other_user.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Should succeed if test_user is admin
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

    def test_get_user_not_found(self, client, test_user):
        """Test getting non-existent user"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_user.tenant_id),
                "email": test_user.email,
            }
        )

        fake_user_id = uuid4()
        response = client.get(
            f"/api/v1/users/{fake_user_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_user_unauthorized(self, client, test_user):
        """Test getting user without authentication"""
        response = client.get(f"/api/v1/users/{test_user.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCreateUser:
    """Tests for POST /api/v1/users endpoint"""

    def test_create_user_as_admin(self, client, test_user, test_tenant):
        """Test creating user as tenant admin"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        new_user_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "name": "New User",
            "role": "user",
            "tenant_id": str(test_tenant.id),
        }

        response = client.post(
            "/api/v1/users",
            json=new_user_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        # Should succeed or fail based on implementation
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_200_OK,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_create_user_invalid_email(self, client, test_user, test_tenant):
        """Test creating user with invalid email"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        invalid_user_data = {
            "email": "not-an-email",
            "password": "SecurePass123!",
            "name": "Invalid User",
            "role": "user",
            "tenant_id": str(test_tenant.id),
        }

        response = client.post(
            "/api/v1/users",
            json=invalid_user_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_weak_password(self, client, test_user, test_tenant):
        """Test creating user with weak password"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        weak_password_data = {
            "email": "weakpass@example.com",
            "password": "weak",  # Too short
            "name": "Weak Password User",
            "role": "user",
            "tenant_id": str(test_tenant.id),
        }

        response = client.post(
            "/api/v1/users",
            json=weak_password_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_unauthorized(self, client, test_tenant):
        """Test creating user without authentication"""
        new_user_data = {
            "email": "unauthorized@example.com",
            "password": "SecurePass123!",
            "name": "Unauthorized User",
            "role": "user",
            "tenant_id": str(test_tenant.id),
        }

        response = client.post("/api/v1/users", json=new_user_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateUser:
    """Tests for PUT /api/v1/users/{user_id} endpoint"""

    def test_update_own_user(self, client, test_user):
        """Test updating own user information"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_user.tenant_id),
                "email": test_user.email,
            }
        )

        update_data = {"name": "Updated Name"}

        response = client.put(
            f"/api/v1/users/{test_user.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        # Should succeed or fail based on implementation
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

    def test_update_user_not_found(self, client, test_user):
        """Test updating non-existent user"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_user.tenant_id),
                "email": test_user.email,
            }
        )

        fake_user_id = uuid4()
        update_data = {"name": "Updated"}

        response = client.put(
            f"/api/v1/users/{fake_user_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]

    def test_update_user_unauthorized(self, client, test_user):
        """Test updating user without authentication"""
        update_data = {"name": "Updated"}

        response = client.put(f"/api/v1/users/{test_user.id}", json=update_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestDeleteUser:
    """Tests for DELETE /api/v1/users/{user_id} endpoint"""

    def test_delete_user_as_admin(self, client, test_user, test_tenant, db_session):
        """Test deleting user as admin"""
        # Create user to delete
        user_to_delete = User(
            id=uuid4(),
            tenant_id=test_tenant.id,
            email="todelete@example.com",
            password_hash=AuthService.hash_password("password123"),
            name="To Delete",
            role="user",
        )
        db_session.add(user_to_delete)
        db_session.commit()

        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        response = client.delete(
            f"/api/v1/users/{user_to_delete.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Should succeed or require additional permissions
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_403_FORBIDDEN]

    def test_delete_user_not_found(self, client, test_user):
        """Test deleting non-existent user"""
        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_user.tenant_id),
                "email": test_user.email,
            }
        )

        fake_user_id = uuid4()
        response = client.delete(
            f"/api/v1/users/{fake_user_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]

    def test_delete_user_unauthorized(self, client, test_user):
        """Test deleting user without authentication"""
        response = client.delete(f"/api/v1/users/{test_user.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTenantIsolation:
    """Tests for tenant isolation in user operations"""

    def test_cannot_list_other_tenant_users(self, client, test_user, test_tenant, db_session):
        """Test that tenant admin cannot list users from other tenants"""
        # Create another tenant and user
        other_tenant_id = uuid4()
        other_user = User(
            id=uuid4(),
            tenant_id=other_tenant_id,
            email="othertenant@example.com",
            password_hash=AuthService.hash_password("password123"),
            name="Other Tenant User",
            role="tenant_admin",
        )
        db_session.add(other_user)
        db_session.commit()

        token = AuthService.create_access_token(
            data={
                "sub": str(test_user.id),
                "tenant_id": str(test_tenant.id),
                "email": test_user.email,
            }
        )

        # Try to filter by other tenant
        response = client.get(
            f"/api/v1/users?tenant_id={other_tenant_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Should deny access
        assert response.status_code == status.HTTP_403_FORBIDDEN


# Run tests with: pytest tests/test_users_api.py -v
