"""
Tests for Core Exceptions Module

Comprehensive test coverage for custom exception classes and error handling.
"""

from fastapi import HTTPException, status

from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
    DiagnoLeadsException,
    ErrorCode,
    ExternalServiceError,
    ResourceNotFoundError,
    TenantAccessDeniedError,
    TenantError,
    ValidationError,
    handle_exception,
)


class TestErrorCode:
    """Tests for ErrorCode enum"""

    def test_auth_error_codes(self):
        """Test authentication error codes"""
        assert ErrorCode.AUTH_INVALID_CREDENTIALS == "AUTH_001"
        assert ErrorCode.AUTH_TOKEN_EXPIRED == "AUTH_002"
        assert ErrorCode.AUTH_TOKEN_INVALID == "AUTH_003"
        assert ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS == "AUTH_004"
        assert ErrorCode.AUTH_USER_NOT_FOUND == "AUTH_005"
        assert ErrorCode.AUTH_USER_ALREADY_EXISTS == "AUTH_006"
        assert ErrorCode.AUTH_EMAIL_NOT_VERIFIED == "AUTH_007"

    def test_tenant_error_codes(self):
        """Test tenant error codes"""
        assert ErrorCode.TENANT_NOT_FOUND == "TENANT_001"
        assert ErrorCode.TENANT_INVALID == "TENANT_002"
        assert ErrorCode.TENANT_LIMIT_EXCEEDED == "TENANT_003"
        assert ErrorCode.TENANT_SUBSCRIPTION_INACTIVE == "TENANT_004"
        assert ErrorCode.TENANT_ACCESS_DENIED == "TENANT_005"

    def test_assessment_error_codes(self):
        """Test assessment error codes"""
        assert ErrorCode.ASSESSMENT_NOT_FOUND == "ASSESS_001"
        assert ErrorCode.ASSESSMENT_INVALID_STATUS == "ASSESS_002"
        assert ErrorCode.ASSESSMENT_VALIDATION_FAILED == "ASSESS_003"
        assert ErrorCode.ASSESSMENT_PUBLISH_FAILED == "ASSESS_004"
        assert ErrorCode.ASSESSMENT_QUESTION_LIMIT == "ASSESS_005"
        assert ErrorCode.ASSESSMENT_AI_GENERATION_FAILED == "ASSESS_006"

    def test_lead_error_codes(self):
        """Test lead error codes"""
        assert ErrorCode.LEAD_NOT_FOUND == "LEAD_001"
        assert ErrorCode.LEAD_INVALID_STATUS == "LEAD_002"
        assert ErrorCode.LEAD_DUPLICATE_EMAIL == "LEAD_003"
        assert ErrorCode.LEAD_SCORING_FAILED == "LEAD_004"
        assert ErrorCode.LEAD_EXPORT_FAILED == "LEAD_005"

    def test_validation_error_codes(self):
        """Test validation error codes"""
        assert ErrorCode.VALIDATION_ERROR == "VALID_001"
        assert ErrorCode.VALIDATION_REQUIRED_FIELD == "VALID_002"
        assert ErrorCode.VALIDATION_INVALID_FORMAT == "VALID_003"
        assert ErrorCode.VALIDATION_OUT_OF_RANGE == "VALID_004"

    def test_database_error_codes(self):
        """Test database error codes"""
        assert ErrorCode.DB_QUERY_FAILED == "DB_001"
        assert ErrorCode.DB_INTEGRITY_ERROR == "DB_002"
        assert ErrorCode.DB_TRANSACTION_FAILED == "DB_003"
        assert ErrorCode.DB_CONNECTION_FAILED == "DB_004"

    def test_system_error_codes(self):
        """Test system error codes"""
        assert ErrorCode.SYSTEM_ERROR == "SYS_001"
        assert ErrorCode.SYSTEM_CONFIGURATION_ERROR == "SYS_002"
        assert ErrorCode.SYSTEM_RESOURCE_EXHAUSTED == "SYS_003"


class TestDiagnoLeadsException:
    """Tests for base DiagnoLeadsException"""

    def test_exception_initialization(self):
        """Test basic exception creation"""
        exc = DiagnoLeadsException(
            code=ErrorCode.SYSTEM_ERROR,
            message="Test error",
            details={"key": "value"},
            http_status=500,
        )

        assert exc.code == ErrorCode.SYSTEM_ERROR
        assert exc.message == "Test error"
        assert exc.details == {"key": "value"}
        assert exc.http_status == 500

    def test_exception_default_details(self):
        """Test exception with default empty details"""
        exc = DiagnoLeadsException(code=ErrorCode.SYSTEM_ERROR, message="Test error")

        assert exc.details == {}

    def test_to_dict(self):
        """Test converting exception to dictionary"""
        exc = DiagnoLeadsException(
            code=ErrorCode.LEAD_NOT_FOUND,
            message="Lead not found",
            details={"lead_id": "123"},
        )

        result = exc.to_dict()

        assert result["error"]["code"] == "LEAD_001"
        assert result["error"]["message"] == "Lead not found"
        assert result["error"]["details"]["lead_id"] == "123"

    def test_to_http_exception(self):
        """Test converting to FastAPI HTTPException"""
        exc = DiagnoLeadsException(
            code=ErrorCode.AUTH_INVALID_CREDENTIALS,
            message="Invalid credentials",
            http_status=status.HTTP_401_UNAUTHORIZED,
        )

        http_exc = exc.to_http_exception()

        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == 401
        assert http_exc.detail["code"] == "AUTH_001"
        assert http_exc.detail["message"] == "Invalid credentials"


class TestAuthenticationError:
    """Tests for AuthenticationError"""

    def test_default_authentication_error(self):
        """Test authentication error with defaults"""
        exc = AuthenticationError()

        assert exc.code == ErrorCode.AUTH_INVALID_CREDENTIALS
        assert exc.message == "認証に失敗しました"
        assert exc.http_status == status.HTTP_401_UNAUTHORIZED

    def test_custom_authentication_error(self):
        """Test authentication error with custom values"""
        exc = AuthenticationError(
            code=ErrorCode.AUTH_TOKEN_EXPIRED,
            message="Token expired",
            details={"token_id": "abc123"},
        )

        assert exc.code == ErrorCode.AUTH_TOKEN_EXPIRED
        assert exc.message == "Token expired"
        assert exc.details["token_id"] == "abc123"


class TestAuthorizationError:
    """Tests for AuthorizationError"""

    def test_default_authorization_error(self):
        """Test authorization error with defaults"""
        exc = AuthorizationError()

        assert exc.code == ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS
        assert exc.message == "この操作を実行する権限がありません"
        assert exc.http_status == status.HTTP_403_FORBIDDEN

    def test_custom_authorization_error(self):
        """Test authorization error with custom values"""
        exc = AuthorizationError(
            message="Access denied to resource",
            details={"resource": "admin_panel"},
        )

        assert exc.http_status == 403


class TestTenantError:
    """Tests for TenantError"""

    def test_default_tenant_error(self):
        """Test tenant error with defaults"""
        exc = TenantError()

        assert exc.code == ErrorCode.TENANT_NOT_FOUND
        assert exc.message == "テナントが見つかりません"
        assert exc.http_status == status.HTTP_404_NOT_FOUND

    def test_custom_tenant_error(self):
        """Test tenant error with custom values"""
        exc = TenantError(
            code=ErrorCode.TENANT_LIMIT_EXCEEDED,
            message="Tenant limit exceeded",
            details={"current": 100, "max": 50},
        )

        assert exc.code == ErrorCode.TENANT_LIMIT_EXCEEDED
        assert exc.details["current"] == 100


class TestTenantAccessDeniedError:
    """Tests for TenantAccessDeniedError"""

    def test_default_tenant_access_denied(self):
        """Test tenant access denied with defaults"""
        exc = TenantAccessDeniedError()

        assert exc.code == ErrorCode.TENANT_ACCESS_DENIED
        assert exc.message == "他のテナントのリソースにアクセスできません"
        assert exc.http_status == status.HTTP_403_FORBIDDEN

    def test_custom_tenant_access_denied(self):
        """Test tenant access denied with custom message"""
        exc = TenantAccessDeniedError(
            message="Cannot access tenant B resources",
            details={"attempted_tenant": "tenant-b", "user_tenant": "tenant-a"},
        )

        assert exc.message == "Cannot access tenant B resources"
        assert exc.details["attempted_tenant"] == "tenant-b"


class TestResourceNotFoundError:
    """Tests for ResourceNotFoundError"""

    def test_resource_not_found_error(self):
        """Test resource not found error"""
        exc = ResourceNotFoundError(
            code=ErrorCode.LEAD_NOT_FOUND,
            resource_type="Lead",
            resource_id="lead-123",
        )

        assert exc.code == ErrorCode.LEAD_NOT_FOUND
        assert "Lead (ID: lead-123) が見つかりません" in exc.message
        assert exc.details["resource_type"] == "Lead"
        assert exc.details["resource_id"] == "lead-123"
        assert exc.http_status == status.HTTP_404_NOT_FOUND

    def test_resource_not_found_with_custom_details(self):
        """Test resource not found with additional details"""
        exc = ResourceNotFoundError(
            code=ErrorCode.ASSESSMENT_NOT_FOUND,
            resource_type="Assessment",
            resource_id=456,
            details={"tenant_id": "tenant-abc", "requested_by": "user-xyz"},
        )

        assert exc.details["tenant_id"] == "tenant-abc"
        assert exc.details["requested_by"] == "user-xyz"


class TestValidationError:
    """Tests for ValidationError"""

    def test_default_validation_error(self):
        """Test validation error with defaults"""
        exc = ValidationError()

        assert exc.code == ErrorCode.VALIDATION_ERROR
        assert exc.message == "入力データが無効です"
        assert exc.http_status == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_custom_validation_error(self):
        """Test validation error with custom values"""
        exc = ValidationError(
            code=ErrorCode.VALIDATION_REQUIRED_FIELD,
            message="Email is required",
            details={"field": "email", "constraint": "required"},
        )

        assert exc.code == ErrorCode.VALIDATION_REQUIRED_FIELD
        assert exc.details["field"] == "email"


class TestExternalServiceError:
    """Tests for ExternalServiceError"""

    def test_external_service_error(self):
        """Test external service error"""
        exc = ExternalServiceError(
            code=ErrorCode.INTEGRATION_GA4_FAILED,
            service_name="Google Analytics 4",
            message="API request failed",
        )

        assert exc.code == ErrorCode.INTEGRATION_GA4_FAILED
        assert "Google Analytics 4: API request failed" in exc.message
        assert exc.details["service"] == "Google Analytics 4"
        assert exc.http_status == status.HTTP_503_SERVICE_UNAVAILABLE

    def test_external_service_error_with_details(self):
        """Test external service error with additional details"""
        exc = ExternalServiceError(
            code=ErrorCode.INTEGRATION_TEAMS_FAILED,
            service_name="Microsoft Teams",
            message="Webhook timeout",
            details={"service": "Microsoft Teams", "webhook_url": "https://example.com/webhook", "timeout": 30},
        )

        assert exc.details["service"] == "Microsoft Teams"
        assert exc.details["webhook_url"] == "https://example.com/webhook"
        assert exc.details["timeout"] == 30


class TestDatabaseError:
    """Tests for DatabaseError"""

    def test_default_database_error(self):
        """Test database error with defaults"""
        exc = DatabaseError()

        assert exc.code == ErrorCode.DB_QUERY_FAILED
        assert exc.message == "データベース操作に失敗しました"
        assert exc.http_status == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_custom_database_error(self):
        """Test database error with custom values"""
        exc = DatabaseError(
            code=ErrorCode.DB_INTEGRITY_ERROR,
            message="Foreign key constraint violation",
            details={"table": "leads", "constraint": "fk_tenant_id"},
        )

        assert exc.code == ErrorCode.DB_INTEGRITY_ERROR
        assert exc.details["table"] == "leads"


class TestHandleException:
    """Tests for handle_exception helper function"""

    def test_handle_diagnoleads_exception(self):
        """Test handling DiagnoLeads custom exception"""
        original_exc = AuthenticationError(
            code=ErrorCode.AUTH_TOKEN_EXPIRED,
            message="Token has expired",
        )

        http_exc = handle_exception(original_exc)

        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == 401
        assert http_exc.detail["code"] == "AUTH_002"

    def test_handle_generic_exception(self):
        """Test handling generic Python exception"""
        original_exc = ValueError("Something went wrong")

        http_exc = handle_exception(original_exc)

        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == 500
        assert http_exc.detail["code"] == "SYS_001"
        assert http_exc.detail["message"] == "システムエラーが発生しました"
        assert http_exc.detail["details"]["error"] == "Something went wrong"

    def test_handle_standard_exception(self):
        """Test handling standard exception"""
        original_exc = RuntimeError("Unexpected error")

        http_exc = handle_exception(original_exc)

        assert http_exc.status_code == 500
        assert "Unexpected error" in http_exc.detail["details"]["error"]
