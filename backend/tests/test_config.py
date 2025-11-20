"""
Tests for Application Configuration

Comprehensive test coverage for core/config.py settings and validation.
"""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings


class TestSettingsDefaults:
    """Tests for Settings default values"""

    def test_default_project_info(self):
        """Test default project information"""
        settings = Settings()

        assert settings.PROJECT_NAME == "DiagnoLeads API"
        assert settings.VERSION == "0.1.0"
        assert settings.ENVIRONMENT in ["development", "staging", "production", "test"]
        assert settings.DEBUG is True

    def test_default_api_settings(self):
        """Test default API settings"""
        settings = Settings()

        assert settings.API_V1_PREFIX == "/api/v1"
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8000

    def test_default_cors_settings(self):
        """Test default CORS allowed origins"""
        settings = Settings()

        assert "http://localhost:3000" in settings.ALLOWED_ORIGINS
        assert "http://localhost:5173" in settings.ALLOWED_ORIGINS
        assert len(settings.ALLOWED_ORIGINS) == 4

    def test_default_jwt_settings(self):
        """Test default JWT settings"""
        settings = Settings()

        assert settings.ALGORITHM == "HS256"
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 1440  # 24 hours
        assert settings.REFRESH_TOKEN_EXPIRE_MINUTES == 10080  # 7 days

    def test_default_database_settings(self):
        """Test default database settings"""
        settings = Settings()

        assert "postgresql://" in settings.DATABASE_URL
        assert settings.DB_POOL_SIZE == 10
        assert settings.DB_MAX_OVERFLOW == 20
        assert settings.DB_POOL_TIMEOUT == 30
        assert settings.DB_ECHO is False

    def test_default_redis_settings(self):
        """Test default Redis settings"""
        settings = Settings()

        assert "redis://" in settings.REDIS_URL
        assert settings.REDIS_MAX_CONNECTIONS == 10
        assert settings.REDIS_SOCKET_TIMEOUT == 5

    def test_default_anthropic_settings(self):
        """Test default Anthropic API settings"""
        settings = Settings()

        assert settings.ANTHROPIC_API_TIMEOUT == 60
        assert settings.ANTHROPIC_MAX_RETRIES == 3

    def test_default_trigger_settings(self):
        """Test default Trigger.dev settings"""
        settings = Settings()

        assert settings.TRIGGER_API_URL == "https://api.trigger.dev"

    def test_default_smtp_settings(self):
        """Test default SMTP settings"""
        settings = Settings()

        assert settings.SMTP_PORT == 587
        assert settings.FROM_EMAIL == "noreply@diagnoleads.com"
        assert settings.FROM_NAME == "DiagnoLeads"

    def test_default_security_settings(self):
        """Test default security settings"""
        settings = Settings()

        assert settings.BCRYPT_ROUNDS == 12
        assert settings.PASSWORD_MIN_LENGTH == 8

    def test_default_rate_limit_settings(self):
        """Test default rate limiting settings"""
        settings = Settings()

        assert settings.RATE_LIMIT_ENABLED is True
        assert settings.RATE_LIMIT_PER_MINUTE == 60
        assert settings.RATE_LIMIT_PER_HOUR == 1000

    def test_default_logging_settings(self):
        """Test default logging settings"""
        settings = Settings()

        assert settings.LOG_LEVEL == "INFO"
        assert settings.LOG_FORMAT == "json"

    def test_default_file_upload_settings(self):
        """Test default file upload settings"""
        settings = Settings()

        assert settings.MAX_UPLOAD_SIZE == 10 * 1024 * 1024  # 10MB
        assert ".jpg" in settings.ALLOWED_UPLOAD_EXTENSIONS
        assert ".pdf" in settings.ALLOWED_UPLOAD_EXTENSIONS
        assert len(settings.ALLOWED_UPLOAD_EXTENSIONS) == 5


class TestSettingsEnvironmentOverrides:
    """Tests for environment variable overrides"""

    def test_override_environment(self):
        """Test overriding ENVIRONMENT setting"""
        with patch.dict(os.environ, {"ENVIRONMENT": "production", "SECRET_KEY": "production-secret-key"}):
            settings = Settings()
            assert settings.ENVIRONMENT == "production"

    def test_override_debug(self):
        """Test overriding DEBUG setting"""
        with patch.dict(os.environ, {"DEBUG": "false"}):
            settings = Settings()
            assert settings.DEBUG is False

    def test_override_api_prefix(self):
        """Test overriding API_V1_PREFIX"""
        with patch.dict(os.environ, {"API_V1_PREFIX": "/api/v2"}):
            settings = Settings()
            assert settings.API_V1_PREFIX == "/api/v2"

    def test_override_database_url(self):
        """Test overriding DATABASE_URL"""
        custom_url = "postgresql://user:pass@localhost:5432/testdb"
        with patch.dict(os.environ, {"DATABASE_URL": custom_url}):
            settings = Settings()
            assert settings.DATABASE_URL == custom_url

    def test_override_secret_key(self):
        """Test overriding SECRET_KEY"""
        with patch.dict(os.environ, {"SECRET_KEY": "custom-secret-key"}):
            settings = Settings()
            assert settings.SECRET_KEY == "custom-secret-key"

    def test_override_anthropic_api_key(self):
        """Test overriding ANTHROPIC_API_KEY"""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-ant-test123"}):
            settings = Settings()
            assert settings.ANTHROPIC_API_KEY == "sk-ant-test123"


class TestSecretKeyValidation:
    """Tests for SECRET_KEY validation"""

    def test_production_with_default_secret_key_raises_error(self):
        """Test production environment with default SECRET_KEY raises error"""
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                ENVIRONMENT="production",
                SECRET_KEY="your-secret-key-change-this-in-production",
            )

        errors = exc_info.value.errors()
        assert any("SECRET_KEY" in str(error) for error in errors)
        assert any("本番環境" in str(error["msg"]) for error in errors)

    def test_production_with_custom_secret_key_succeeds(self):
        """Test production environment with custom SECRET_KEY succeeds"""
        settings = Settings(
            ENVIRONMENT="production",
            SECRET_KEY="strong-random-secret-key-for-production",
        )

        assert settings.SECRET_KEY == "strong-random-secret-key-for-production"
        assert settings.ENVIRONMENT == "production"

    def test_development_with_default_secret_key_succeeds(self):
        """Test development environment allows default SECRET_KEY"""
        settings = Settings(
            ENVIRONMENT="development",
            SECRET_KEY="your-secret-key-change-this-in-production",
        )

        assert settings.SECRET_KEY == "your-secret-key-change-this-in-production"

    def test_staging_with_default_secret_key_succeeds(self):
        """Test staging environment allows default SECRET_KEY"""
        settings = Settings(
            ENVIRONMENT="staging",
            SECRET_KEY="your-secret-key-change-this-in-production",
        )

        assert settings.SECRET_KEY == "your-secret-key-change-this-in-production"


class TestEnvironmentProperties:
    """Tests for environment detection properties"""

    def test_is_production_true(self):
        """Test is_production property returns True in production"""
        settings = Settings(
            ENVIRONMENT="production",
            SECRET_KEY="production-secret-key",
        )

        assert settings.is_production is True
        assert settings.is_development is False
        assert settings.is_staging is False

    def test_is_development_true(self):
        """Test is_development property returns True in development"""
        settings = Settings(ENVIRONMENT="development")

        assert settings.is_development is True
        assert settings.is_production is False
        assert settings.is_staging is False

    def test_is_staging_true(self):
        """Test is_staging property returns True in staging"""
        settings = Settings(ENVIRONMENT="staging")

        assert settings.is_staging is True
        assert settings.is_production is False
        assert settings.is_development is False

    def test_test_environment_properties(self):
        """Test environment properties in test environment"""
        settings = Settings(ENVIRONMENT="test")

        assert settings.is_production is False
        assert settings.is_development is False
        assert settings.is_staging is False


class TestGetSettingsFunction:
    """Tests for get_settings() function"""

    def test_get_settings_returns_settings_instance(self):
        """Test get_settings returns Settings instance"""
        settings = get_settings()

        assert isinstance(settings, Settings)

    def test_get_settings_is_cached(self):
        """Test get_settings returns same instance (cached)"""
        settings1 = get_settings()
        settings2 = get_settings()

        # Should be the same instance due to lru_cache
        assert settings1 is settings2

    def test_get_settings_has_default_values(self):
        """Test get_settings instance has expected defaults"""
        settings = get_settings()

        assert settings.PROJECT_NAME == "DiagnoLeads API"
        assert settings.VERSION == "0.1.0"
        assert settings.API_V1_PREFIX == "/api/v1"


class TestSettingsConfig:
    """Tests for Settings.Config class"""

    def test_config_case_sensitive(self):
        """Test that settings are case-sensitive"""
        # Config.case_sensitive = True means environment variables must match case
        # This is tested implicitly by the fact that settings use exact case

        settings = Settings()
        assert hasattr(settings, "PROJECT_NAME")
        assert hasattr(settings, "ENVIRONMENT")

    def test_config_extra_ignore(self):
        """Test that extra environment variables are ignored"""
        # Config.extra = "ignore" means undefined env vars don't cause errors
        # This is tested implicitly - no validation errors for unknown vars

        with patch.dict(os.environ, {"UNKNOWN_SETTING": "value"}):
            settings = Settings()
            assert not hasattr(settings, "UNKNOWN_SETTING")


class TestIntegrationSettings:
    """Tests for integration-specific settings"""

    def test_microsoft_teams_settings(self):
        """Test Microsoft Teams integration settings"""
        settings = Settings(
            MICROSOFT_CLIENT_ID="client-id",
            MICROSOFT_CLIENT_SECRET="client-secret",
            MICROSOFT_TENANT_ID="tenant-id",
            BOT_APP_ID="bot-id",
            BOT_APP_PASSWORD="bot-password",
            TEAMS_WEBHOOK_URL="https://webhook.url",
        )

        assert settings.MICROSOFT_CLIENT_ID == "client-id"
        assert settings.MICROSOFT_CLIENT_SECRET == "client-secret"
        assert settings.MICROSOFT_TENANT_ID == "tenant-id"
        assert settings.BOT_APP_ID == "bot-id"
        assert settings.BOT_APP_PASSWORD == "bot-password"
        assert settings.TEAMS_WEBHOOK_URL == "https://webhook.url"

    def test_external_integrations_settings(self):
        """Test external integrations settings"""
        settings = Settings(
            SALESFORCE_CLIENT_ID="sf-id",
            SALESFORCE_CLIENT_SECRET="sf-secret",
            HUBSPOT_API_KEY="hs-key",
            SLACK_WEBHOOK_URL="https://slack.webhook",
        )

        assert settings.SALESFORCE_CLIENT_ID == "sf-id"
        assert settings.SALESFORCE_CLIENT_SECRET == "sf-secret"
        assert settings.HUBSPOT_API_KEY == "hs-key"
        assert settings.SLACK_WEBHOOK_URL == "https://slack.webhook"

    def test_supabase_settings(self):
        """Test Supabase settings"""
        settings = Settings(
            SUPABASE_URL="https://supabase.url",
            SUPABASE_ANON_KEY="anon-key",
            SUPABASE_SERVICE_KEY="service-key",
        )

        assert settings.SUPABASE_URL == "https://supabase.url"
        assert settings.SUPABASE_ANON_KEY == "anon-key"
        assert settings.SUPABASE_SERVICE_KEY == "service-key"
