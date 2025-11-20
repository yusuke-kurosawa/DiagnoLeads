"""
Tests for Authentication Schemas

Comprehensive test coverage for authentication Pydantic models and validators.
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.auth import (
    PasswordResetConfirm,
    PasswordResetRequest,
    RegistrationResponse,
    Token,
    TokenData,
    TokenRefresh,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)


class TestUserLogin:
    """Tests for UserLogin schema"""

    def test_valid_user_login(self):
        """Test creating valid user login"""
        login = UserLogin(
            email="user@example.com",
            password="Password123",
        )

        assert login.email == "user@example.com"
        assert login.password == "Password123"

    def test_user_login_invalid_email(self):
        """Test invalid email format"""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(email="not-an-email", password="Password123")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("email",) for error in errors)

    def test_user_login_password_too_short(self):
        """Test password too short (< 8 chars)"""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(email="user@example.com", password="Pass1")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("password",) for error in errors)

    def test_user_login_missing_email(self):
        """Test missing email field"""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(password="Password123")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("email",) for error in errors)

    def test_user_login_missing_password(self):
        """Test missing password field"""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(email="user@example.com")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("password",) for error in errors)


class TestUserCreate:
    """Tests for UserCreate schema"""

    def test_valid_user_create(self):
        """Test creating valid user creation request"""
        user = UserCreate(
            email="newuser@example.com",
            password="SecurePass123",
            name="Test User",
            tenant_name="Test Company",
            tenant_slug="test-company",
        )

        assert user.email == "newuser@example.com"
        assert user.password == "SecurePass123"
        assert user.name == "Test User"
        assert user.tenant_name == "Test Company"
        assert user.tenant_slug == "test-company"

    def test_user_create_password_no_uppercase(self):
        """Test password validation: missing uppercase letter"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="user@example.com",
                password="weakpass123",  # No uppercase
                name="User",
                tenant_name="Company",
                tenant_slug="company",
            )

        errors = exc_info.value.errors()
        assert any("password" in str(error["loc"]) for error in errors)
        assert any("英大文字" in str(error["msg"]) for error in errors)

    def test_user_create_password_no_lowercase(self):
        """Test password validation: missing lowercase letter"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="user@example.com",
                password="WEAKPASS123",  # No lowercase
                name="User",
                tenant_name="Company",
                tenant_slug="company",
            )

        errors = exc_info.value.errors()
        assert any("英小文字" in str(error["msg"]) for error in errors)

    def test_user_create_password_no_number(self):
        """Test password validation: missing number"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="user@example.com",
                password="WeakPassword",  # No number
                name="User",
                tenant_name="Company",
                tenant_slug="company",
            )

        errors = exc_info.value.errors()
        assert any("数字" in str(error["msg"]) for error in errors)

    def test_user_create_password_too_short(self):
        """Test password validation: too short"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="user@example.com",
                password="Pass1",  # Too short
                name="User",
                tenant_name="Company",
                tenant_slug="company",
            )

        errors = exc_info.value.errors()
        assert any("password" in str(error["loc"]) for error in errors)

    def test_user_create_valid_strong_password(self):
        """Test strong password passes validation"""
        user = UserCreate(
            email="user@example.com",
            password="StrongPass123!",  # Meets all requirements
            name="User",
            tenant_name="Company",
            tenant_slug="company",
        )

        assert user.password == "StrongPass123!"

    def test_user_create_name_too_short(self):
        """Test name validation: too short"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="user@example.com",
                password="SecurePass123",
                name="",  # Empty name
                tenant_name="Company",
                tenant_slug="company",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_user_create_name_too_long(self):
        """Test name validation: too long"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="user@example.com",
                password="SecurePass123",
                name="x" * 256,  # Exceeds 255 chars
                tenant_name="Company",
                tenant_slug="company",
            )

    def test_user_create_tenant_slug_invalid_chars(self):
        """Test tenant_slug pattern validation: invalid characters"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="user@example.com",
                password="SecurePass123",
                name="User",
                tenant_name="Company",
                tenant_slug="Invalid_Slug!",  # Uppercase and special chars not allowed
            )

        errors = exc_info.value.errors()
        assert any("tenant_slug" in str(error["loc"]) for error in errors)

    def test_user_create_tenant_slug_valid_patterns(self):
        """Test tenant_slug valid patterns"""
        valid_slugs = ["company", "test-company", "company123", "123company", "a-b-c-1-2-3"]

        for slug in valid_slugs:
            user = UserCreate(
                email="user@example.com",
                password="SecurePass123",
                name="User",
                tenant_name="Company",
                tenant_slug=slug,
            )
            assert user.tenant_slug == slug

    def test_user_create_tenant_slug_too_long(self):
        """Test tenant_slug max length"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="user@example.com",
                password="SecurePass123",
                name="User",
                tenant_name="Company",
                tenant_slug="a" * 101,  # Exceeds 100 chars
            )

    def test_user_create_invalid_email(self):
        """Test invalid email format"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="not-an-email",
                password="SecurePass123",
                name="User",
                tenant_name="Company",
                tenant_slug="company",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("email",) for error in errors)


class TestUserResponse:
    """Tests for UserResponse schema"""

    def test_valid_user_response(self):
        """Test creating valid user response"""
        user_id = uuid4()
        tenant_id = uuid4()
        created_at = datetime.now(timezone.utc)

        user = UserResponse(
            id=user_id,
            tenant_id=tenant_id,
            email="user@example.com",
            name="Test User",
            role="admin",
            tenant_name="Test Company",
            tenant_slug="test-company",
            tenant_plan="professional",
            created_at=created_at,
        )

        assert user.id == user_id
        assert user.tenant_id == tenant_id
        assert user.email == "user@example.com"
        assert user.name == "Test User"
        assert user.role == "admin"

    def test_user_response_optional_fields(self):
        """Test user response with optional fields as None"""
        user_id = uuid4()
        tenant_id = uuid4()

        user = UserResponse(
            id=user_id,
            tenant_id=tenant_id,
            email="user@example.com",
            name="User",
            role="user",
            tenant_name=None,
            tenant_slug=None,
            tenant_plan=None,
            created_at=datetime.now(timezone.utc),
        )

        assert user.tenant_name is None
        assert user.tenant_slug is None
        assert user.tenant_plan is None


class TestRegistrationResponse:
    """Tests for RegistrationResponse schema"""

    def test_valid_registration_response(self):
        """Test creating valid registration response"""
        user_id = uuid4()
        tenant_id = uuid4()

        response = RegistrationResponse(
            user_id=user_id,
            tenant_id=tenant_id,
        )

        assert response.user_id == user_id
        assert response.tenant_id == tenant_id
        assert response.message == "登録が完了しました。ログインしてください。"

    def test_registration_response_custom_message(self):
        """Test registration response with custom message"""
        user_id = uuid4()
        tenant_id = uuid4()

        response = RegistrationResponse(
            user_id=user_id,
            tenant_id=tenant_id,
            message="Custom registration message",
        )

        assert response.message == "Custom registration message"


class TestToken:
    """Tests for Token schema"""

    def test_valid_token(self):
        """Test creating valid token response"""
        user_id = uuid4()
        tenant_id = uuid4()

        user_response = UserResponse(
            id=user_id,
            tenant_id=tenant_id,
            email="user@example.com",
            name="User",
            role="user",
            created_at=datetime.now(timezone.utc),
        )

        token = Token(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            token_type="bearer",
            user=user_response,
        )

        assert token.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        assert token.token_type == "bearer"
        assert token.user.id == user_id

    def test_token_default_type(self):
        """Test token default type is 'bearer'"""
        user_id = uuid4()
        tenant_id = uuid4()

        user_response = UserResponse(
            id=user_id,
            tenant_id=tenant_id,
            email="user@example.com",
            name="User",
            role="user",
            created_at=datetime.now(timezone.utc),
        )

        token = Token(
            access_token="token123",
            user=user_response,
        )

        assert token.token_type == "bearer"


class TestTokenData:
    """Tests for TokenData schema"""

    def test_valid_token_data(self):
        """Test creating valid token data"""
        user_id = uuid4()
        tenant_id = uuid4()

        data = TokenData(
            user_id=user_id,
            tenant_id=tenant_id,
            email="user@example.com",
        )

        assert data.user_id == user_id
        assert data.tenant_id == tenant_id
        assert data.email == "user@example.com"

    def test_token_data_all_optional(self):
        """Test token data with all fields as None"""
        data = TokenData()

        assert data.user_id is None
        assert data.tenant_id is None
        assert data.email is None

    def test_token_data_partial(self):
        """Test token data with some fields"""
        user_id = uuid4()

        data = TokenData(user_id=user_id)

        assert data.user_id == user_id
        assert data.tenant_id is None
        assert data.email is None


class TestPasswordResetRequest:
    """Tests for PasswordResetRequest schema"""

    def test_valid_password_reset_request(self):
        """Test creating valid password reset request"""
        request = PasswordResetRequest(email="user@example.com")

        assert request.email == "user@example.com"

    def test_password_reset_request_invalid_email(self):
        """Test invalid email format"""
        with pytest.raises(ValidationError) as exc_info:
            PasswordResetRequest(email="not-an-email")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("email",) for error in errors)


class TestPasswordResetConfirm:
    """Tests for PasswordResetConfirm schema"""

    def test_valid_password_reset_confirm(self):
        """Test creating valid password reset confirmation"""
        confirm = PasswordResetConfirm(
            token="reset-token-123",
            password="NewSecure123",
        )

        assert confirm.token == "reset-token-123"
        assert confirm.password == "NewSecure123"

    def test_password_reset_confirm_weak_password_no_uppercase(self):
        """Test password validation: missing uppercase"""
        with pytest.raises(ValidationError) as exc_info:
            PasswordResetConfirm(
                token="token",
                password="weakpass123",  # No uppercase
            )

        errors = exc_info.value.errors()
        assert any("英大文字" in str(error["msg"]) for error in errors)

    def test_password_reset_confirm_weak_password_no_lowercase(self):
        """Test password validation: missing lowercase"""
        with pytest.raises(ValidationError) as exc_info:
            PasswordResetConfirm(
                token="token",
                password="WEAKPASS123",  # No lowercase
            )

        errors = exc_info.value.errors()
        assert any("英小文字" in str(error["msg"]) for error in errors)

    def test_password_reset_confirm_weak_password_no_number(self):
        """Test password validation: missing number"""
        with pytest.raises(ValidationError) as exc_info:
            PasswordResetConfirm(
                token="token",
                password="WeakPassword",  # No number
            )

        errors = exc_info.value.errors()
        assert any("数字" in str(error["msg"]) for error in errors)

    def test_password_reset_confirm_password_too_short(self):
        """Test password validation: too short"""
        with pytest.raises(ValidationError) as exc_info:
            PasswordResetConfirm(
                token="token",
                password="Pass1",  # Too short
            )

        errors = exc_info.value.errors()
        assert any("password" in str(error["loc"]) for error in errors)

    def test_password_reset_confirm_strong_password(self):
        """Test strong password passes validation"""
        confirm = PasswordResetConfirm(
            token="token",
            password="VerySecure123!",
        )

        assert confirm.password == "VerySecure123!"


class TestTokenRefresh:
    """Tests for TokenRefresh schema"""

    def test_valid_token_refresh(self):
        """Test creating valid token refresh request"""
        refresh = TokenRefresh(refresh_token="refresh-token-xyz")

        assert refresh.refresh_token == "refresh-token-xyz"

    def test_token_refresh_missing_token(self):
        """Test missing refresh_token field"""
        with pytest.raises(ValidationError) as exc_info:
            TokenRefresh()

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("refresh_token",) for error in errors)


class TestTokenResponse:
    """Tests for TokenResponse schema"""

    def test_valid_token_response(self):
        """Test creating valid token response"""
        user_id = uuid4()
        tenant_id = uuid4()

        user_response = UserResponse(
            id=user_id,
            tenant_id=tenant_id,
            email="user@example.com",
            name="User",
            role="user",
            created_at=datetime.now(timezone.utc),
        )

        response = TokenResponse(
            access_token="access-token-abc",
            refresh_token="refresh-token-xyz",
            token_type="bearer",
            expires_in=86400,
            user=user_response,
        )

        assert response.access_token == "access-token-abc"
        assert response.refresh_token == "refresh-token-xyz"
        assert response.token_type == "bearer"
        assert response.expires_in == 86400
        assert response.user.id == user_id

    def test_token_response_default_values(self):
        """Test token response default values"""
        user_id = uuid4()
        tenant_id = uuid4()

        user_response = UserResponse(
            id=user_id,
            tenant_id=tenant_id,
            email="user@example.com",
            name="User",
            role="user",
            created_at=datetime.now(timezone.utc),
        )

        response = TokenResponse(
            access_token="access-token",
            refresh_token="refresh-token",
            user=user_response,
        )

        assert response.token_type == "bearer"  # default
        assert response.expires_in == 86400  # default (24 hours)

    def test_token_response_custom_expiry(self):
        """Test token response with custom expiry time"""
        user_id = uuid4()
        tenant_id = uuid4()

        user_response = UserResponse(
            id=user_id,
            tenant_id=tenant_id,
            email="user@example.com",
            name="User",
            role="user",
            created_at=datetime.now(timezone.utc),
        )

        response = TokenResponse(
            access_token="access-token",
            refresh_token="refresh-token",
            expires_in=3600,  # 1 hour
            user=user_response,
        )

        assert response.expires_in == 3600
