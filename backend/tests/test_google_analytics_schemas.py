"""
Tests for Google Analytics Schemas

Comprehensive test coverage for Google Analytics integration Pydantic models and validators.
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.google_analytics import (
    GoogleAnalyticsIntegrationBase,
    GoogleAnalyticsIntegrationCreate,
    GoogleAnalyticsIntegrationPublic,
    GoogleAnalyticsIntegrationResponse,
    GoogleAnalyticsIntegrationUpdate,
    GoogleAnalyticsTestResponse,
)


class TestGoogleAnalyticsIntegrationBase:
    """Tests for GoogleAnalyticsIntegrationBase schema"""

    def test_valid_integration_base(self):
        """Test creating valid GA4 integration base"""
        integration = GoogleAnalyticsIntegrationBase(
            measurement_id="G-ABC1234567",
            enabled=True,
            track_frontend=True,
            track_embed_widget=True,
            track_server_events=False,
        )

        assert integration.measurement_id == "G-ABC1234567"
        assert integration.enabled is True
        assert integration.track_frontend is True
        assert integration.track_embed_widget is True
        assert integration.track_server_events is False

    def test_integration_base_default_values(self):
        """Test default values for optional fields"""
        integration = GoogleAnalyticsIntegrationBase(
            measurement_id="G-XYZ9876543",
        )

        assert integration.enabled is True  # default
        assert integration.track_frontend is True  # default
        assert integration.track_embed_widget is True  # default
        assert integration.track_server_events is False  # default
        assert integration.custom_dimensions is None  # default

    def test_integration_base_with_custom_dimensions(self):
        """Test integration with custom dimensions"""
        custom_dims = {
            "dimension1": "tenant_id",
            "dimension2": "assessment_id",
            "metric1": "lead_score",
        }

        integration = GoogleAnalyticsIntegrationBase(
            measurement_id="G-ABC1234567",
            custom_dimensions=custom_dims,
        )

        assert integration.custom_dimensions == custom_dims
        assert integration.custom_dimensions["dimension1"] == "tenant_id"

    def test_measurement_id_valid_formats(self):
        """Test various valid measurement ID formats"""
        valid_ids = [
            "G-ABC1234567",
            "G-XYZ9876543",
            "G-1234567890",
            "G-ABCDEFGHIJ",
            "G-A1B2C3D4E5",
        ]

        for measurement_id in valid_ids:
            integration = GoogleAnalyticsIntegrationBase(
                measurement_id=measurement_id,
            )
            assert integration.measurement_id == measurement_id

    def test_measurement_id_invalid_format_no_prefix(self):
        """Test invalid measurement ID: missing G- prefix"""
        with pytest.raises(ValidationError) as exc_info:
            GoogleAnalyticsIntegrationBase(
                measurement_id="ABC1234567",  # Missing G-
            )

        errors = exc_info.value.errors()
        assert any("measurement_id" in str(error["loc"]) for error in errors)
        assert any("G-XXXXXXXXXX" in str(error["msg"]) for error in errors)

    def test_measurement_id_invalid_format_wrong_length(self):
        """Test invalid measurement ID: wrong length"""
        with pytest.raises(ValidationError) as exc_info:
            GoogleAnalyticsIntegrationBase(
                measurement_id="G-ABC123",  # Too short
            )

        errors = exc_info.value.errors()
        assert any("measurement_id" in str(error["loc"]) for error in errors)

    def test_measurement_id_invalid_format_lowercase(self):
        """Test invalid measurement ID: lowercase letters"""
        with pytest.raises(ValidationError) as exc_info:
            GoogleAnalyticsIntegrationBase(
                measurement_id="G-abc1234567",  # Lowercase not allowed
            )

        errors = exc_info.value.errors()
        assert any("measurement_id" in str(error["loc"]) for error in errors)

    def test_measurement_id_invalid_format_special_chars(self):
        """Test invalid measurement ID: special characters"""
        with pytest.raises(ValidationError) as exc_info:
            GoogleAnalyticsIntegrationBase(
                measurement_id="G-ABC-123456",  # Hyphen in ID part
            )

        errors = exc_info.value.errors()
        assert any("measurement_id" in str(error["loc"]) for error in errors)


class TestGoogleAnalyticsIntegrationCreate:
    """Tests for GoogleAnalyticsIntegrationCreate schema"""

    def test_valid_integration_create(self):
        """Test creating valid GA4 integration creation request"""
        integration = GoogleAnalyticsIntegrationCreate(
            measurement_id="G-ABC1234567",
            enabled=True,
            track_frontend=True,
            track_embed_widget=True,
            track_server_events=True,
            measurement_protocol_api_secret="secret_abc123xyz",
        )

        assert integration.measurement_id == "G-ABC1234567"
        assert integration.measurement_protocol_api_secret == "secret_abc123xyz"
        assert integration.track_server_events is True

    def test_integration_create_without_api_secret(self):
        """Test creating integration without API secret"""
        integration = GoogleAnalyticsIntegrationCreate(
            measurement_id="G-XYZ9876543",
            track_server_events=False,
        )

        assert integration.measurement_id == "G-XYZ9876543"
        assert integration.measurement_protocol_api_secret is None
        assert integration.track_server_events is False

    def test_integration_create_with_custom_dimensions(self):
        """Test creating integration with custom dimensions"""
        integration = GoogleAnalyticsIntegrationCreate(
            measurement_id="G-ABC1234567",
            custom_dimensions={"dimension1": "user_role"},
        )

        assert integration.custom_dimensions["dimension1"] == "user_role"

    def test_integration_create_invalid_measurement_id(self):
        """Test integration creation with invalid measurement ID"""
        with pytest.raises(ValidationError) as exc_info:
            GoogleAnalyticsIntegrationCreate(
                measurement_id="INVALID-ID",
            )

        errors = exc_info.value.errors()
        assert any("measurement_id" in str(error["loc"]) for error in errors)


class TestGoogleAnalyticsIntegrationUpdate:
    """Tests for GoogleAnalyticsIntegrationUpdate schema"""

    def test_valid_integration_update(self):
        """Test creating valid GA4 integration update request"""
        update = GoogleAnalyticsIntegrationUpdate(
            measurement_id="G-NEW1234567",
            enabled=False,
            track_frontend=False,
        )

        assert update.measurement_id == "G-NEW1234567"
        assert update.enabled is False
        assert update.track_frontend is False

    def test_integration_update_partial(self):
        """Test partial update (only some fields)"""
        update = GoogleAnalyticsIntegrationUpdate(
            enabled=True,
        )

        assert update.enabled is True
        assert update.measurement_id is None
        assert update.track_frontend is None
        assert update.track_embed_widget is None

    def test_integration_update_all_none(self):
        """Test update with no fields set"""
        update = GoogleAnalyticsIntegrationUpdate()

        assert update.measurement_id is None
        assert update.enabled is None
        assert update.track_frontend is None
        assert update.track_embed_widget is None
        assert update.track_server_events is None
        assert update.custom_dimensions is None
        assert update.measurement_protocol_api_secret is None

    def test_integration_update_measurement_id_valid(self):
        """Test updating measurement ID with valid format"""
        update = GoogleAnalyticsIntegrationUpdate(
            measurement_id="G-UPD1234567",
        )

        assert update.measurement_id == "G-UPD1234567"

    def test_integration_update_measurement_id_invalid(self):
        """Test updating measurement ID with invalid format"""
        with pytest.raises(ValidationError) as exc_info:
            GoogleAnalyticsIntegrationUpdate(
                measurement_id="G-invalid",  # Too short
            )

        errors = exc_info.value.errors()
        assert any("measurement_id" in str(error["loc"]) for error in errors)

    def test_integration_update_measurement_id_none(self):
        """Test measurement ID can be None in update"""
        update = GoogleAnalyticsIntegrationUpdate(
            measurement_id=None,
            enabled=False,
        )

        assert update.measurement_id is None
        assert update.enabled is False

    def test_integration_update_custom_dimensions(self):
        """Test updating custom dimensions"""
        new_dims = {
            "dimension3": "lead_source",
            "metric2": "engagement_score",
        }

        update = GoogleAnalyticsIntegrationUpdate(
            custom_dimensions=new_dims,
        )

        assert update.custom_dimensions == new_dims

    def test_integration_update_api_secret(self):
        """Test updating API secret"""
        update = GoogleAnalyticsIntegrationUpdate(
            measurement_protocol_api_secret="new_secret_xyz789",
        )

        assert update.measurement_protocol_api_secret == "new_secret_xyz789"


class TestGoogleAnalyticsIntegrationResponse:
    """Tests for GoogleAnalyticsIntegrationResponse schema"""

    def test_valid_integration_response(self):
        """Test creating valid GA4 integration response"""
        integration_id = uuid4()
        tenant_id = uuid4()
        created_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)

        response = GoogleAnalyticsIntegrationResponse(
            id=integration_id,
            tenant_id=tenant_id,
            measurement_id="G-ABC1234567",
            enabled=True,
            track_frontend=True,
            track_embed_widget=True,
            track_server_events=False,
            custom_dimensions={"dimension1": "test"},
            created_at=created_at,
            updated_at=updated_at,
        )

        assert response.id == integration_id
        assert response.tenant_id == tenant_id
        assert response.measurement_id == "G-ABC1234567"
        assert response.created_at == created_at
        assert response.updated_at == updated_at

    def test_integration_response_without_updated_at(self):
        """Test integration response without updated_at"""
        integration_id = uuid4()
        tenant_id = uuid4()

        response = GoogleAnalyticsIntegrationResponse(
            id=integration_id,
            tenant_id=tenant_id,
            measurement_id="G-XYZ9876543",
            enabled=True,
            track_frontend=True,
            track_embed_widget=True,
            track_server_events=False,
            created_at=datetime.now(timezone.utc),
            updated_at=None,
        )

        assert response.updated_at is None

    def test_integration_response_with_all_tracking_enabled(self):
        """Test integration response with all tracking features enabled"""
        integration_id = uuid4()
        tenant_id = uuid4()

        response = GoogleAnalyticsIntegrationResponse(
            id=integration_id,
            tenant_id=tenant_id,
            measurement_id="G-ALL1234567",
            enabled=True,
            track_frontend=True,
            track_embed_widget=True,
            track_server_events=True,
            created_at=datetime.now(timezone.utc),
        )

        assert response.enabled is True
        assert response.track_frontend is True
        assert response.track_embed_widget is True
        assert response.track_server_events is True


class TestGoogleAnalyticsIntegrationPublic:
    """Tests for GoogleAnalyticsIntegrationPublic schema"""

    def test_valid_integration_public(self):
        """Test creating valid public GA4 integration"""
        public = GoogleAnalyticsIntegrationPublic(
            measurement_id="G-PUB1234567",
            enabled=True,
            track_embed_widget=True,
        )

        assert public.measurement_id == "G-PUB1234567"
        assert public.enabled is True
        assert public.track_embed_widget is True

    def test_integration_public_disabled(self):
        """Test public integration with tracking disabled"""
        public = GoogleAnalyticsIntegrationPublic(
            measurement_id="G-DIS1234567",
            enabled=False,
            track_embed_widget=False,
        )

        assert public.enabled is False
        assert public.track_embed_widget is False

    def test_integration_public_no_sensitive_fields(self):
        """Test public schema does not expose sensitive fields"""
        public = GoogleAnalyticsIntegrationPublic(
            measurement_id="G-SEC1234567",
            enabled=True,
            track_embed_widget=True,
        )

        # Verify no API secret field exists
        assert not hasattr(public, "measurement_protocol_api_secret")
        # Verify no internal tracking settings
        assert not hasattr(public, "track_frontend")
        assert not hasattr(public, "track_server_events")


class TestGoogleAnalyticsTestResponse:
    """Tests for GoogleAnalyticsTestResponse schema"""

    def test_valid_test_response_success(self):
        """Test creating valid successful test response"""
        timestamp = datetime.now(timezone.utc)

        response = GoogleAnalyticsTestResponse(
            status="success",
            message="GA4 connection test successful",
            event_name="test_event",
            timestamp=timestamp,
        )

        assert response.status == "success"
        assert response.message == "GA4 connection test successful"
        assert response.event_name == "test_event"
        assert response.timestamp == timestamp
        assert response.error_details is None

    def test_valid_test_response_failed(self):
        """Test creating valid failed test response"""
        response = GoogleAnalyticsTestResponse(
            status="failed",
            message="GA4 connection test failed",
            error_details="Invalid API secret",
        )

        assert response.status == "failed"
        assert response.message == "GA4 connection test failed"
        assert response.error_details == "Invalid API secret"
        assert response.event_name is None
        assert response.timestamp is None

    def test_test_response_minimal(self):
        """Test test response with minimal required fields"""
        response = GoogleAnalyticsTestResponse(
            status="success",
            message="Test passed",
        )

        assert response.status == "success"
        assert response.message == "Test passed"
        assert response.event_name is None
        assert response.timestamp is None
        assert response.error_details is None

    def test_test_response_with_all_fields(self):
        """Test test response with all fields populated"""
        timestamp = datetime.now(timezone.utc)

        response = GoogleAnalyticsTestResponse(
            status="failed",
            message="Connection timeout",
            event_name="diagnostic_test",
            timestamp=timestamp,
            error_details="Network timeout after 30 seconds",
        )

        assert response.status == "failed"
        assert response.message == "Connection timeout"
        assert response.event_name == "diagnostic_test"
        assert response.timestamp == timestamp
        assert response.error_details == "Network timeout after 30 seconds"

    def test_test_response_missing_required_fields(self):
        """Test test response missing required fields"""
        with pytest.raises(ValidationError) as exc_info:
            GoogleAnalyticsTestResponse(
                status="success",
                # Missing message field
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("message",) for error in errors)
