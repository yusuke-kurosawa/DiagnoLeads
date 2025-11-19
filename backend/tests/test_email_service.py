"""
Tests for Email Service

Comprehensive test coverage for email_service.py
Target: 100% coverage
"""

from unittest.mock import MagicMock, patch

from app.services.email_service import EmailService


class TestEmailServiceInit:
    """Tests for EmailService initialization"""

    def test_initialization(self):
        """Test service initialization with settings"""
        service = EmailService()

        # Service should have SMTP configuration from settings
        assert hasattr(service, "smtp_host")
        assert hasattr(service, "smtp_port")
        assert hasattr(service, "smtp_user")
        assert hasattr(service, "smtp_password")
        assert hasattr(service, "from_email")
        assert hasattr(service, "from_name")


class TestEmailServiceSendEmail:
    """Tests for send_email method"""

    @patch("app.services.email_service.smtplib.SMTP")
    @patch("app.services.email_service.settings")
    def test_send_email_success(self, mock_settings, mock_smtp):
        """Test successful email sending"""
        # Configure mock settings
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USER = "user@example.com"
        mock_settings.SMTP_PASSWORD = "password"
        mock_settings.FROM_EMAIL = "noreply@example.com"
        mock_settings.FROM_NAME = "DiagnoLeads"

        # Configure mock SMTP
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        service = EmailService()
        result = service.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            html_content="<p>Test HTML</p>",
            text_content="Test Text",
        )

        assert result is True
        mock_smtp.assert_called_once_with("smtp.example.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user@example.com", "password")
        mock_server.send_message.assert_called_once()

    @patch("app.services.email_service.smtplib.SMTP")
    @patch("app.services.email_service.settings")
    def test_send_email_without_text_content(self, mock_settings, mock_smtp):
        """Test sending email without text content"""
        # Configure mock settings
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USER = "user@example.com"
        mock_settings.SMTP_PASSWORD = "password"
        mock_settings.FROM_EMAIL = "noreply@example.com"
        mock_settings.FROM_NAME = "DiagnoLeads"

        # Configure mock SMTP
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        service = EmailService()
        result = service.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            html_content="<p>Test HTML</p>",
        )

        assert result is True
        mock_server.send_message.assert_called_once()

    @patch("app.services.email_service.settings")
    def test_send_email_no_smtp_config(self, mock_settings):
        """Test email sending when SMTP is not configured"""
        # Configure mock settings with no SMTP
        mock_settings.SMTP_HOST = None
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USER = None
        mock_settings.SMTP_PASSWORD = "password"
        mock_settings.FROM_EMAIL = "noreply@example.com"
        mock_settings.FROM_NAME = "DiagnoLeads"

        service = EmailService()
        result = service.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            html_content="<p>Test HTML</p>",
            text_content="Test Text",
        )

        # Should return False when SMTP is not configured
        assert result is False

    @patch("app.services.email_service.smtplib.SMTP")
    @patch("app.services.email_service.settings")
    def test_send_email_smtp_exception(self, mock_settings, mock_smtp):
        """Test email sending with SMTP exception"""
        # Configure mock settings
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USER = "user@example.com"
        mock_settings.SMTP_PASSWORD = "password"
        mock_settings.FROM_EMAIL = "noreply@example.com"
        mock_settings.FROM_NAME = "DiagnoLeads"

        # Configure mock SMTP to raise exception
        mock_smtp.side_effect = Exception("SMTP connection failed")

        service = EmailService()
        result = service.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            html_content="<p>Test HTML</p>",
        )

        assert result is False

    @patch("app.services.email_service.smtplib.SMTP")
    @patch("app.services.email_service.settings")
    def test_send_email_port_465(self, mock_settings, mock_smtp):
        """Test email sending with port 465 (no STARTTLS)"""
        # Configure mock settings with port 465
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 465
        mock_settings.SMTP_USER = "user@example.com"
        mock_settings.SMTP_PASSWORD = "password"
        mock_settings.FROM_EMAIL = "noreply@example.com"
        mock_settings.FROM_NAME = "DiagnoLeads"

        # Configure mock SMTP
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        service = EmailService()
        result = service.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            html_content="<p>Test HTML</p>",
        )

        assert result is True
        # STARTTLS should not be called for port 465
        mock_server.starttls.assert_not_called()


class TestEmailServicePasswordReset:
    """Tests for send_password_reset_email method"""

    @patch.object(EmailService, "send_email")
    @patch("app.services.email_service.settings")
    def test_send_password_reset_email_with_name(self, mock_settings, mock_send_email):
        """Test sending password reset email with user name"""
        mock_settings.FRONTEND_URL = "https://example.com"
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USER = "user@example.com"
        mock_settings.SMTP_PASSWORD = "password"
        mock_settings.FROM_EMAIL = "noreply@example.com"
        mock_settings.FROM_NAME = "DiagnoLeads"
        mock_send_email.return_value = True

        service = EmailService()
        result = service.send_password_reset_email(
            to_email="user@example.com",
            reset_token="test-token-123",
            user_name="Test User",
        )

        assert result is True
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        assert call_args[1]["to_email"] == "user@example.com"
        assert "パスワードリセット" in call_args[1]["subject"]
        assert "test-token-123" in call_args[1]["html_content"]
        assert "Test User" in call_args[1]["html_content"]

    @patch.object(EmailService, "send_email")
    @patch("app.services.email_service.settings")
    def test_send_password_reset_email_without_name(self, mock_settings, mock_send_email):
        """Test sending password reset email without user name"""
        mock_settings.FRONTEND_URL = "https://example.com"
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USER = "user@example.com"
        mock_settings.SMTP_PASSWORD = "password"
        mock_settings.FROM_EMAIL = "noreply@example.com"
        mock_settings.FROM_NAME = "DiagnoLeads"
        mock_send_email.return_value = True

        service = EmailService()
        result = service.send_password_reset_email(
            to_email="user@example.com",
            reset_token="test-token-456",
        )

        assert result is True
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        assert "test-token-456" in call_args[1]["html_content"]


class TestEmailServiceWelcome:
    """Tests for send_welcome_email method"""

    @patch.object(EmailService, "send_email")
    @patch("app.services.email_service.settings")
    def test_send_welcome_email(self, mock_settings, mock_send_email):
        """Test sending welcome email"""
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USER = "user@example.com"
        mock_settings.SMTP_PASSWORD = "password"
        mock_settings.FROM_EMAIL = "noreply@example.com"
        mock_settings.FROM_NAME = "DiagnoLeads"
        mock_send_email.return_value = True

        service = EmailService()
        result = service.send_welcome_email(
            to_email="newuser@example.com",
            user_name="New User",
        )

        assert result is True
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        assert call_args[1]["to_email"] == "newuser@example.com"
        assert "ようこそ" in call_args[1]["subject"]
        assert "New User" in call_args[1]["html_content"]


class TestEmailServiceLeadNotification:
    """Tests for send_lead_notification_email method"""

    @patch.object(EmailService, "send_email")
    @patch("app.services.email_service.settings")
    def test_send_lead_notification_email(self, mock_settings, mock_send_email):
        """Test sending lead notification email"""
        mock_settings.SMTP_HOST = "smtp.example.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USER = "user@example.com"
        mock_settings.SMTP_PASSWORD = "password"
        mock_settings.FROM_EMAIL = "noreply@example.com"
        mock_settings.FROM_NAME = "DiagnoLeads"
        mock_send_email.return_value = True

        service = EmailService()
        result = service.send_lead_notification_email(
            to_email="admin@example.com",
            lead_name="John Doe",
            lead_email="john@example.com",
            assessment_title="Marketing Assessment",
            score=85,
        )

        assert result is True
        mock_send_email.assert_called_once()
        call_args = mock_send_email.call_args
        assert call_args[1]["to_email"] == "admin@example.com"
        assert "John Doe" in call_args[1]["subject"]
        assert "john@example.com" in call_args[1]["html_content"]
        assert "Marketing Assessment" in call_args[1]["html_content"]
        assert "85" in call_args[1]["html_content"]


class TestEmailServiceSingleton:
    """Tests for singleton instance"""

    def test_singleton_instance_exists(self):
        """Test that singleton instance is created"""
        from app.services.email_service import email_service

        assert email_service is not None
        assert isinstance(email_service, EmailService)
