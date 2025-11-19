"""
Advanced Tests for Auth Service

Test coverage for password reset, login attempts, and refresh tokens
"""

from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings
from app.models.user import User
from app.services.auth import AuthService


class TestAuthRefreshTokens:
    """Tests for refresh token functionality"""

    def test_create_refresh_token(self):
        """Test creating a refresh token"""
        data = {"sub": "test-user-id", "tenant_id": "test-tenant-id"}
        token = AuthService.create_refresh_token(data)

        assert token is not None
        assert isinstance(token, str)

        # Decode and verify
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "test-user-id"
        assert payload["tenant_id"] == "test-tenant-id"
        assert payload["type"] == "refresh"

        # Verify expiration is about 7 days
        exp_timestamp = payload["exp"]
        exp_date = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        expected_exp = datetime.now(timezone.utc) + timedelta(days=7)
        # Allow 1 minute tolerance
        assert abs((exp_date - expected_exp).total_seconds()) < 60


class TestAuthPasswordReset:
    """Tests for password reset functionality"""

    def test_create_password_reset_token(self):
        """Test creating a password reset token"""
        token1 = AuthService.create_password_reset_token()
        token2 = AuthService.create_password_reset_token()

        assert token1 is not None
        assert token2 is not None
        assert isinstance(token1, str)
        assert isinstance(token2, str)
        # Tokens should be unique
        assert token1 != token2
        # Tokens should be URL-safe
        assert "/" not in token1
        assert "+" not in token1

    def test_create_password_reset_request_success(self, db_session, test_user):
        """Test creating a password reset request"""
        result = AuthService.create_password_reset_request(db_session, test_user.email)

        assert result is not None
        user, token = result
        assert user.id == test_user.id
        assert token is not None
        assert isinstance(token, str)
        assert user.password_reset_token == token
        assert user.password_reset_expires_at is not None
        # Token should expire in about 1 hour
        expected_exp = datetime.now(timezone.utc) + timedelta(hours=1)
        assert abs((user.password_reset_expires_at - expected_exp).total_seconds()) < 60

    def test_create_password_reset_request_nonexistent_user(self, db_session):
        """Test password reset request for non-existent user"""
        result = AuthService.create_password_reset_request(db_session, "nonexistent@example.com")

        assert result is None

    def test_verify_password_reset_token_valid(self, db_session, test_user):
        """Test verifying a valid password reset token"""
        # Create reset request
        user, token = AuthService.create_password_reset_request(db_session, test_user.email)

        # Verify token
        verified_user = AuthService.verify_password_reset_token(db_session, token)

        assert verified_user is not None
        assert verified_user.id == test_user.id

    def test_verify_password_reset_token_expired(self, db_session, test_user):
        """Test verifying an expired password reset token"""
        # Manually set expired token
        token = "expired-token-123"
        test_user.password_reset_token = token
        test_user.password_reset_expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        db_session.commit()

        # Try to verify
        verified_user = AuthService.verify_password_reset_token(db_session, token)

        assert verified_user is None

    def test_verify_password_reset_token_invalid(self, db_session):
        """Test verifying an invalid token"""
        verified_user = AuthService.verify_password_reset_token(db_session, "invalid-token")

        assert verified_user is None

    def test_reset_password(self, db_session, test_user):
        """Test resetting user password"""
        old_password_hash = test_user.password_hash
        new_password = "NewSecurePassword123!"

        # Set reset token
        test_user.password_reset_token = "some-token"
        test_user.password_reset_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        db_session.commit()

        # Reset password
        updated_user = AuthService.reset_password(db_session, test_user, new_password)

        assert updated_user.password_hash != old_password_hash
        assert updated_user.password_reset_token is None
        assert updated_user.password_reset_expires_at is None
        # Verify new password works
        assert AuthService.verify_password(new_password, updated_user.password_hash)


class TestAuthLoginAttempts:
    """Tests for login attempt tracking and account locking"""

    def test_check_and_increment_login_attempts_first_attempt(self, db_session, test_user):
        """Test first login attempt"""
        can_attempt, error_msg = AuthService.check_and_increment_login_attempts(db_session, test_user.email)

        assert can_attempt is True
        assert error_msg is None

        # Verify attempt was incremented
        db_session.refresh(test_user)
        assert test_user.failed_login_attempts == 1

    def test_check_and_increment_login_attempts_multiple(self, db_session, test_user):
        """Test multiple failed login attempts"""
        for i in range(4):
            can_attempt, error_msg = AuthService.check_and_increment_login_attempts(db_session, test_user.email)
            assert can_attempt is True
            assert error_msg is None

        db_session.refresh(test_user)
        assert test_user.failed_login_attempts == 4

    def test_check_and_increment_login_attempts_locks_account(self, db_session, test_user):
        """Test that account gets locked after 5 attempts"""
        # Make 4 attempts
        for i in range(4):
            AuthService.check_and_increment_login_attempts(db_session, test_user.email)

        # 5th attempt should lock the account
        can_attempt, error_msg = AuthService.check_and_increment_login_attempts(db_session, test_user.email)

        assert can_attempt is False
        assert error_msg is not None
        assert "ロック" in error_msg

        db_session.refresh(test_user)
        assert test_user.locked_until is not None
        # Should be locked for about 15 minutes
        expected_unlock = datetime.now(timezone.utc) + timedelta(minutes=15)
        assert abs((test_user.locked_until - expected_unlock).total_seconds()) < 60

    def test_check_and_increment_login_attempts_already_locked(self, db_session, test_user):
        """Test that locked account cannot attempt login"""
        # Lock the account
        test_user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=10)
        test_user.failed_login_attempts = 5
        db_session.commit()

        can_attempt, error_msg = AuthService.check_and_increment_login_attempts(db_session, test_user.email)

        assert can_attempt is False
        assert error_msg is not None
        assert "ロック" in error_msg
        # Should show remaining time
        assert "分後" in error_msg

    def test_check_and_increment_login_attempts_nonexistent_user(self, db_session):
        """Test login attempts for non-existent user"""
        can_attempt, error_msg = AuthService.check_and_increment_login_attempts(
            db_session, "nonexistent@example.com"
        )

        # Should allow attempt (to avoid user enumeration)
        assert can_attempt is True
        assert error_msg is None

    def test_reset_login_attempts(self, db_session, test_user):
        """Test resetting login attempts after successful login"""
        # Set failed attempts
        test_user.failed_login_attempts = 3
        test_user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
        db_session.commit()

        # Reset attempts
        AuthService.reset_login_attempts(test_user, db_session)

        db_session.refresh(test_user)
        assert test_user.failed_login_attempts == 0
        assert test_user.locked_until is None


class TestAuthUserRetrieval:
    """Tests for user retrieval methods"""

    def test_get_user_by_id(self, db_session, test_user):
        """Test getting user by ID"""
        user = AuthService.get_user_by_id(db_session, test_user.id)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    def test_get_user_by_id_not_found(self, db_session):
        """Test getting non-existent user by ID"""
        from uuid import uuid4

        user = AuthService.get_user_by_id(db_session, uuid4())

        assert user is None

    def test_get_user_by_email(self, db_session, test_user):
        """Test getting user by email"""
        user = AuthService.get_user_by_email(db_session, test_user.email)

        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    def test_get_user_by_email_not_found(self, db_session):
        """Test getting non-existent user by email"""
        user = AuthService.get_user_by_email(db_session, "nonexistent@example.com")

        assert user is None


class TestAuthTokenDecoding:
    """Tests for token decoding with various scenarios"""

    def test_decode_access_token_with_custom_expiry(self):
        """Test creating and decoding token with custom expiry"""
        data = {"sub": "user-123", "tenant_id": "tenant-456", "email": "test@example.com"}
        custom_expiry = timedelta(hours=2)
        token = AuthService.create_access_token(data, expires_delta=custom_expiry)

        decoded = AuthService.decode_access_token(token)

        assert decoded.user_id is not None
        assert str(decoded.user_id) == "user-123"
        assert str(decoded.tenant_id) == "tenant-456"
        assert decoded.email == "test@example.com"

    def test_decode_access_token_without_email(self):
        """Test decoding token without email field"""
        data = {"sub": "user-123", "tenant_id": "tenant-456"}
        token = AuthService.create_access_token(data)

        decoded = AuthService.decode_access_token(token)

        assert decoded.user_id is not None
        assert decoded.tenant_id is not None
        assert decoded.email is None
