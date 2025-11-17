"""
Tests for SMS service (Twilio integration)
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from backend.app.services.sms_service import SMSService


class TestSMSService:
    """Test SMS service functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        with patch("backend.app.services.sms_service.Client"):
            self.sms_service = SMSService()

    def test_validate_phone_number_valid_japan(self):
        """Test phone number validation for Japanese numbers"""
        valid, formatted = self.sms_service.validate_phone_number("+819012345678")
        assert valid is True
        assert formatted == "+819012345678"

    def test_validate_phone_number_valid_us(self):
        """Test phone number validation for US numbers"""
        valid, formatted = self.sms_service.validate_phone_number("+12025551234")
        assert valid is True
        assert formatted == "+12025551234"

    def test_validate_phone_number_invalid_format(self):
        """Test phone number validation with invalid format"""
        valid, formatted = self.sms_service.validate_phone_number("090-1234-5678")
        assert valid is False
        assert "E.164" in formatted  # Error message should mention E.164

    def test_validate_phone_number_missing_plus(self):
        """Test phone number validation missing + prefix"""
        valid, formatted = self.sms_service.validate_phone_number("819012345678")
        assert valid is False

    def test_validate_phone_number_too_short(self):
        """Test phone number validation with too short number"""
        valid, formatted = self.sms_service.validate_phone_number("+8190")
        assert valid is False

    def test_estimate_cost_japan(self):
        """Test cost estimation for Japan"""
        estimate = self.sms_service.estimate_cost(num_messages=100, region="JP")

        assert estimate["num_messages"] == 100
        assert estimate["region"] == "JP"
        assert estimate["cost_per_message"] == 0.073
        assert estimate["total_cost"] == 7.30
        assert estimate["currency"] == "USD"

    def test_estimate_cost_us(self):
        """Test cost estimation for US"""
        estimate = self.sms_service.estimate_cost(num_messages=1000, region="US")

        assert estimate["num_messages"] == 1000
        assert estimate["region"] == "US"
        assert estimate["cost_per_message"] == 0.0079
        assert estimate["total_cost"] == 7.90
        assert estimate["currency"] == "USD"

    def test_estimate_cost_default_region(self):
        """Test cost estimation with default region"""
        estimate = self.sms_service.estimate_cost(num_messages=50, region="OTHER")

        # Should use default cost
        assert estimate["cost_per_message"] == 0.05
        assert estimate["total_cost"] == 2.50

    @patch("backend.app.services.sms_service.Client")
    def test_send_sms_success(self, mock_client_class):
        """Test successful SMS sending"""
        # Mock Twilio client
        mock_message = Mock()
        mock_message.sid = "SM123456789"
        mock_message.status = "sent"

        mock_client = Mock()
        mock_client.messages.create.return_value = mock_message
        mock_client_class.return_value = mock_client

        # Recreate service with mocked client
        sms_service = SMSService()

        result = sms_service.send_sms(
            to="+819012345678",
            message="Test message",
            short_url="https://short.url/abc123"
        )

        # Verify result
        assert result["success"] is True
        assert result["sid"] == "SM123456789"
        assert result["status"] == "sent"
        assert result["error"] is None

        # Verify Twilio API was called correctly
        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args
        assert call_args.kwargs["to"] == "+819012345678"
        assert "Test message" in call_args.kwargs["body"]

    @patch("backend.app.services.sms_service.Client")
    def test_send_sms_with_url_placeholder(self, mock_client_class):
        """Test SMS sending with URL placeholder replacement"""
        mock_message = Mock()
        mock_message.sid = "SM123456789"
        mock_message.status = "sent"

        mock_client = Mock()
        mock_client.messages.create.return_value = mock_message
        mock_client_class.return_value = mock_client

        sms_service = SMSService()

        result = sms_service.send_sms(
            to="+819012345678",
            message="診断はこちら: {url}",
            short_url="https://short.url/abc123"
        )

        # URL should be inserted
        call_args = mock_client.messages.create.call_args
        assert "https://short.url/abc123" in call_args.kwargs["body"]
        assert "{url}" not in call_args.kwargs["body"]

    @patch("backend.app.services.sms_service.Client")
    def test_send_sms_failure(self, mock_client_class):
        """Test SMS sending failure"""
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("Twilio API error")
        mock_client_class.return_value = mock_client

        sms_service = SMSService()

        result = sms_service.send_sms(
            to="+819012345678",
            message="Test message",
            short_url=None
        )

        # Verify failure result
        assert result["success"] is False
        assert result["sid"] is None
        assert result["status"] == "failed"
        assert "Twilio API error" in result["error"]

    @pytest.mark.asyncio
    @patch("backend.app.services.sms_service.Client")
    async def test_send_campaign_success(self, mock_client_class):
        """Test bulk SMS campaign sending"""
        # Mock Twilio responses
        mock_messages = [
            Mock(sid=f"SM{i}", status="sent") for i in range(3)
        ]

        mock_client = Mock()
        mock_client.messages.create.side_effect = mock_messages
        mock_client_class.return_value = mock_client

        # Mock campaign and database
        mock_campaign = Mock()
        mock_campaign.id = "campaign_123"
        mock_campaign.message_template = "診断: {url}"

        mock_db = AsyncMock()

        sms_service = SMSService()

        recipients = [
            "+819012345671",
            "+819012345672",
            "+819012345673",
        ]

        result = await sms_service.send_campaign(
            campaign=mock_campaign,
            recipients=recipients,
            short_url="https://short.url/abc",
            db=mock_db
        )

        # Verify results
        assert result["total"] == 3
        assert result["sent"] == 3
        assert result["failed"] == 0

    @pytest.mark.asyncio
    @patch("backend.app.services.sms_service.Client")
    async def test_send_campaign_partial_failure(self, mock_client_class):
        """Test bulk SMS campaign with partial failures"""
        # Mock Twilio responses with some failures
        mock_client = Mock()
        mock_client.messages.create.side_effect = [
            Mock(sid="SM1", status="sent"),
            Exception("Invalid phone number"),
            Mock(sid="SM3", status="sent"),
        ]
        mock_client_class.return_value = mock_client

        mock_campaign = Mock()
        mock_campaign.id = "campaign_123"
        mock_campaign.message_template = "Test: {url}"

        mock_db = AsyncMock()

        sms_service = SMSService()

        recipients = [
            "+819012345671",
            "+819012345672",  # This will fail
            "+819012345673",
        ]

        result = await sms_service.send_campaign(
            campaign=mock_campaign,
            recipients=recipients,
            short_url="https://short.url/abc",
            db=mock_db
        )

        # Verify mixed results
        assert result["total"] == 3
        assert result["sent"] == 2
        assert result["failed"] == 1
