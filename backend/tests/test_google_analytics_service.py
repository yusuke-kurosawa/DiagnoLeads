"""
Tests for Google Analytics Service

Comprehensive test coverage for google_analytics_service.py
Target: 100% coverage
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas.google_analytics import GoogleAnalyticsIntegrationCreate
from app.services.google_analytics_service import GoogleAnalyticsService


class TestGoogleAnalyticsServiceCreate:
    """Tests for create_or_update method"""

    @pytest.mark.asyncio
    async def test_create_new_integration(self, db_session, test_tenant):
        """Test creating a new GA4 integration"""
        service = GoogleAnalyticsService(db_session)

        data = GoogleAnalyticsIntegrationCreate(
            measurement_id="G-ABC1234567",
            enabled=True,
            track_frontend=True,
            track_embed_widget=True,
            track_server_events=False,
            measurement_protocol_api_secret="test-secret-123",
        )

        integration = await service.create_or_update(test_tenant.id, data)

        assert integration.id is not None
        assert integration.tenant_id == test_tenant.id
        assert integration.measurement_id == "G-ABC1234567"
        assert integration.enabled is True
        assert integration.track_frontend is True
        assert integration.measurement_protocol_api_secret == "test-secret-123"

    @pytest.mark.asyncio
    async def test_update_existing_integration(self, db_session, test_tenant):
        """Test updating an existing GA4 integration"""
        service = GoogleAnalyticsService(db_session)

        # Create initial integration
        initial_data = GoogleAnalyticsIntegrationCreate(
            measurement_id="G-ABC1234567",
            enabled=True,
            track_frontend=True,
        )
        await service.create_or_update(test_tenant.id, initial_data)

        # Update integration
        update_data = GoogleAnalyticsIntegrationCreate(
            measurement_id="G-XYZ9876543",
            enabled=False,
            track_frontend=False,
            measurement_protocol_api_secret="new-secret",
        )
        updated = await service.create_or_update(test_tenant.id, update_data)

        assert updated.measurement_id == "G-XYZ9876543"
        assert updated.enabled is False
        assert updated.track_frontend is False
        assert updated.measurement_protocol_api_secret == "new-secret"

    @pytest.mark.asyncio
    async def test_create_invalid_measurement_id(self, db_session, test_tenant):
        """Test creating integration with invalid measurement ID"""
        # Pydantic validates before service method is called
        with pytest.raises(ValidationError):
            GoogleAnalyticsIntegrationCreate(
                measurement_id="INVALID-ID",
                enabled=True,
            )

    @pytest.mark.asyncio
    async def test_update_without_api_secret(self, db_session, test_tenant):
        """Test updating integration without changing API secret"""
        service = GoogleAnalyticsService(db_session)

        # Create with secret
        initial_data = GoogleAnalyticsIntegrationCreate(
            measurement_id="G-ABC1234567",
            enabled=True,
            measurement_protocol_api_secret="original-secret",
        )
        await service.create_or_update(test_tenant.id, initial_data)

        # Update without secret
        update_data = GoogleAnalyticsIntegrationCreate(
            measurement_id="G-XYZ9876543",
            enabled=True,
            measurement_protocol_api_secret=None,
        )
        updated = await service.create_or_update(test_tenant.id, update_data)

        # Secret should remain unchanged
        assert updated.measurement_protocol_api_secret == "original-secret"


class TestGoogleAnalyticsServiceGet:
    """Tests for get methods"""

    @pytest.mark.asyncio
    async def test_get_by_tenant(self, db_session, test_tenant):
        """Test getting integration by tenant ID"""
        service = GoogleAnalyticsService(db_session)

        # Create integration
        data = GoogleAnalyticsIntegrationCreate(
            measurement_id="G-ABC1234567",
            enabled=True,
        )
        created = await service.create_or_update(test_tenant.id, data)

        # Get by tenant
        integration = service.get_by_tenant(test_tenant.id)

        assert integration is not None
        assert integration.id == created.id
        assert integration.tenant_id == test_tenant.id

    def test_get_by_tenant_not_found(self, db_session):
        """Test getting non-existent integration"""
        service = GoogleAnalyticsService(db_session)

        integration = service.get_by_tenant(uuid4())

        assert integration is None

    @pytest.mark.asyncio
    async def test_get_by_id(self, db_session, test_tenant):
        """Test getting integration by ID"""
        service = GoogleAnalyticsService(db_session)

        # Create integration
        data = GoogleAnalyticsIntegrationCreate(
            measurement_id="G-ABC1234567",
            enabled=True,
        )
        created = await service.create_or_update(test_tenant.id, data)

        # Get by ID
        integration = service.get_by_id(created.id)

        assert integration is not None
        assert integration.id == created.id

    def test_get_by_id_not_found(self, db_session):
        """Test getting integration by non-existent ID"""
        service = GoogleAnalyticsService(db_session)

        integration = service.get_by_id(uuid4())

        assert integration is None


class TestGoogleAnalyticsServiceDelete:
    """Tests for delete method"""

    @pytest.mark.asyncio
    async def test_delete_existing_integration(self, db_session, test_tenant):
        """Test deleting an existing integration"""
        service = GoogleAnalyticsService(db_session)

        # Create integration
        data = GoogleAnalyticsIntegrationCreate(
            measurement_id="G-ABC1234567",
            enabled=True,
        )
        await service.create_or_update(test_tenant.id, data)

        # Delete
        result = await service.delete(test_tenant.id)

        assert result is True

        # Verify deletion
        integration = service.get_by_tenant(test_tenant.id)
        assert integration is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_integration(self, db_session):
        """Test deleting non-existent integration"""
        service = GoogleAnalyticsService(db_session)

        result = await service.delete(uuid4())

        assert result is False


class TestGoogleAnalyticsServiceTestConnection:
    """Tests for test_connection method"""

    @pytest.mark.asyncio
    async def test_connection_integration_not_found(self, db_session):
        """Test connection when integration doesn't exist"""
        service = GoogleAnalyticsService(db_session)

        response = await service.test_connection(uuid4())

        assert response.status == "failed"
        assert "not found" in response.message

    @pytest.mark.asyncio
    async def test_connection_integration_disabled(self, db_session, test_tenant):
        """Test connection when integration is disabled"""
        service = GoogleAnalyticsService(db_session)

        # Create disabled integration
        data = GoogleAnalyticsIntegrationCreate(
            measurement_id="G-ABC1234567",
            enabled=False,
        )
        await service.create_or_update(test_tenant.id, data)

        response = await service.test_connection(test_tenant.id)

        assert response.status == "failed"
        assert "disabled" in response.message

    @pytest.mark.asyncio
    async def test_connection_no_api_secret(self, db_session, test_tenant):
        """Test connection without API secret"""
        service = GoogleAnalyticsService(db_session)

        # Create integration without API secret
        data = GoogleAnalyticsIntegrationCreate(
            measurement_id="G-ABC1234567",
            enabled=True,
            measurement_protocol_api_secret=None,
        )
        await service.create_or_update(test_tenant.id, data)

        response = await service.test_connection(test_tenant.id)

        assert response.status == "failed"
        assert "API Secret" in response.message

    @pytest.mark.asyncio
    @patch("app.services.google_analytics_service.GA4MeasurementProtocol")
    async def test_connection_success(self, mock_ga4_class, db_session, test_tenant):
        """Test successful connection"""
        service = GoogleAnalyticsService(db_session)

        # Create integration with API secret
        data = GoogleAnalyticsIntegrationCreate(
            measurement_id="G-ABC1234567",
            enabled=True,
            measurement_protocol_api_secret="test-secret",
        )
        await service.create_or_update(test_tenant.id, data)

        # Mock GA4 client
        mock_client = MagicMock()
        mock_client.send_connection_test_event = AsyncMock(return_value={"status": "success", "message": "Connection successful"})
        mock_ga4_class.return_value = mock_client

        response = await service.test_connection(test_tenant.id)

        assert response.status == "success"
        assert mock_client.send_connection_test_event.called


class TestGoogleAnalyticsServiceGetPublicConfig:
    """Tests for get_public_config method"""

    def test_get_public_config_not_implemented(self, db_session):
        """Test that get_public_config returns None (not fully implemented)"""
        service = GoogleAnalyticsService(db_session)

        config = service.get_public_config(uuid4())

        assert config is None
