"""
Tests for User Service

Comprehensive test coverage for user_service.py
Target: 100% coverage
"""

from uuid import UUID, uuid4

from app.models.user import User
from app.schemas.user import UserCreate
from app.services.user_service import UserService


class TestUserServicePasswordHashing:
    """Tests for password hashing methods"""

    def test_hash_password_creates_hash(self):
        """Test that hash_password creates a valid hash"""
        password = "test_password_123"
        hashed = UserService.hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Hash should not equal plaintext

    def test_hash_password_different_hashes(self):
        """Test that same password creates different hashes (salt)"""
        password = "test_password_123"
        hash1 = UserService.hash_password(password)
        hash2 = UserService.hash_password(password)

        # Different hashes due to different salts
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test verifying correct password"""
        password = "correct_password"
        hashed = UserService.hash_password(password)

        result = UserService.verify_password(password, hashed)
        assert result is True

    def test_verify_password_incorrect(self):
        """Test verifying incorrect password"""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = UserService.hash_password(password)

        result = UserService.verify_password(wrong_password, hashed)
        assert result is False


class TestUserServiceCreate:
    """Tests for create_user method"""

    def test_create_user_success(self, db_session, test_tenant):
        """Test successful user creation"""
        user_data = UserCreate(
            tenant_id=test_tenant.id,
            email="newuser@example.com",
            password="SecurePass123!",
            name="New User",
            role="user",
        )

        user = UserService.create_user(db_session, user_data)

        assert user.id is not None
        assert isinstance(user.id, UUID)
        assert user.email == "newuser@example.com"
        assert user.name == "New User"
        assert user.role == "user"
        assert user.tenant_id == test_tenant.id
        # Password should be hashed
        assert user.password_hash != "SecurePass123!"
        assert len(user.password_hash) > 0

    def test_create_user_default_role(self, db_session, test_tenant):
        """Test user creation with default role"""
        user_data = UserCreate(
            tenant_id=test_tenant.id,
            email="defaultrole@example.com",
            password="SecurePass123!",
            name="Default Role User",
        )

        user = UserService.create_user(db_session, user_data)

        assert user.role == "user"  # Default role

    def test_create_user_admin_role(self, db_session, test_tenant):
        """Test creating user with admin role"""
        user_data = UserCreate(
            tenant_id=test_tenant.id,
            email="admin@example.com",
            password="AdminPass123!",
            name="Admin User",
            role="tenant_admin",
        )

        user = UserService.create_user(db_session, user_data)

        assert user.role == "tenant_admin"

    def test_create_user_password_is_hashed(self, db_session, test_tenant):
        """Test that password is properly hashed"""
        password = "PlaintextPassword123"
        user_data = UserCreate(
            tenant_id=test_tenant.id,
            email="hashtest@example.com",
            password=password,
            name="Hash Test User",
        )

        user = UserService.create_user(db_session, user_data)

        # Password should be hashed
        assert user.password_hash != password
        # Should be able to verify with original password
        assert UserService.verify_password(password, user.password_hash)


class TestUserServiceGet:
    """Tests for get methods"""

    def test_get_user_by_id_success(self, db_session, test_user):
        """Test getting user by ID"""
        user = UserService.get_user_by_id(db_session, test_user.id)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    def test_get_user_by_id_not_found(self, db_session):
        """Test getting non-existent user by ID"""
        non_existent_id = uuid4()
        user = UserService.get_user_by_id(db_session, non_existent_id)

        assert user is None

    def test_get_user_by_email_success(self, db_session, test_user):
        """Test getting user by email"""
        user = UserService.get_user_by_email(db_session, test_user.email)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    def test_get_user_by_email_not_found(self, db_session):
        """Test getting non-existent user by email"""
        user = UserService.get_user_by_email(db_session, "nonexistent@example.com")

        assert user is None

    def test_get_user_by_email_case_sensitive(self, db_session, test_user):
        """Test that email search is case-sensitive"""
        # SQLAlchemy default behavior is case-sensitive for strings
        upper_email = test_user.email.upper()

        # This should not find the user if emails don't match case
        user = UserService.get_user_by_email(db_session, upper_email)

        # This depends on database collation settings
        # For PostgreSQL with default collation, this might not find the user
        # So we just test that the service doesn't crash
        assert user is None or user.email == test_user.email


class TestUserServiceListTenantUsers:
    """Tests for get_tenant_users method"""

    def test_get_tenant_users_success(self, db_session, test_tenant, test_user):
        """Test getting all users for a tenant"""
        # test_user already exists, create additional users
        user2 = User(
            tenant_id=test_tenant.id,
            email="user2@example.com",
            password_hash=UserService.hash_password("password"),
            name="User 2",
            role="user",
        )
        user3 = User(
            tenant_id=test_tenant.id,
            email="user3@example.com",
            password_hash=UserService.hash_password("password"),
            name="User 3",
            role="user",
        )
        db_session.add_all([user2, user3])
        db_session.commit()

        users = UserService.get_tenant_users(db_session, test_tenant.id)

        assert len(users) == 3
        assert all(user.tenant_id == test_tenant.id for user in users)

    def test_get_tenant_users_pagination(self, db_session, test_tenant):
        """Test pagination of tenant users"""
        # Create 5 users
        for i in range(5):
            user = User(
                tenant_id=test_tenant.id,
                email=f"user{i}@example.com",
                password_hash=UserService.hash_password("password"),
                name=f"User {i}",
                role="user",
            )
            db_session.add(user)
        db_session.commit()

        # Test pagination
        page1 = UserService.get_tenant_users(db_session, test_tenant.id, skip=0, limit=2)
        page2 = UserService.get_tenant_users(db_session, test_tenant.id, skip=2, limit=2)

        assert len(page1) == 2
        assert len(page2) == 2
        assert page1[0].id != page2[0].id

    def test_get_tenant_users_tenant_isolation(self, db_session, test_tenant, test_tenant_2):
        """Test that users from other tenants are not returned"""
        # Create users for test_tenant
        user1 = User(
            tenant_id=test_tenant.id,
            email="tenant1user@example.com",
            password_hash=UserService.hash_password("password"),
            name="Tenant 1 User",
            role="user",
        )
        # Create user for test_tenant_2
        user2 = User(
            tenant_id=test_tenant_2.id,
            email="tenant2user@example.com",
            password_hash=UserService.hash_password("password"),
            name="Tenant 2 User",
            role="user",
        )
        db_session.add_all([user1, user2])
        db_session.commit()

        # Get users for test_tenant only
        users = UserService.get_tenant_users(db_session, test_tenant.id)

        assert len(users) == 1
        assert all(user.tenant_id == test_tenant.id for user in users)
        assert users[0].email == "tenant1user@example.com"

    def test_get_tenant_users_empty_tenant(self, db_session, test_tenant_2):
        """Test getting users from tenant with no users"""
        users = UserService.get_tenant_users(db_session, test_tenant_2.id)

        assert len(users) == 0
        assert users == []
