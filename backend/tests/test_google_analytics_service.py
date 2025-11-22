"""
Tests for Google Analytics Service

Test coverage for GoogleAnalyticsService including:
- Integration creation and updates
- Connection testing
- CRUD operations
- Error handling
"""

from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.models.google_analytics_integration import GoogleAnalyticsIntegration
from app.schemas.google_analytics import GoogleAnalyticsIntegrationCreate
from app.services.google_analytics_service import GoogleAnalyticsService


class TestCreateOrUpdate:
    """Tests for create_or_update method"""

    @pytest.mark.asyncio
    async def test_create_new_integration(self, db_session: Session, test_tenant):
        """Test creating a new GA4 integration"""
        service = GoogleAnalyticsService(db_session)

        data = GoogleAnalyticsIntegrationCreate(
            measurement_id="G-ABC123DEF4",
            measurement_protocol_api_secret="secret123",
            enabled=True,
            track_frontend=True,
            track_embed_widget=True,
            track_server_events=False,
            custom_dimensions={"dimension1": "value1"},
        )

        result = await service.create_or_update(test_tenant.id, data)

        assert result.tenant_id == test_tenant.id
        assert result.measurement_id == "G-ABC123DEF4"
        assert result.enabled is True
        assert result.track_frontend is True

    @pytest.mark.asyncio
    async def test_update_existing_integration(self, db_session: Session, test_tenant):
        """Test updating an existing GA4 integration"""
        # Create initial integration (must match pattern G-[A-Z0-9]{10})
        existing = GoogleAnalyticsIntegration(
            id=uuid4(),
            tenant_id=test_tenant.id,
            measurement_id="G-OLDTEST123",
            enabled=False,
            track_frontend=False,
            track_embed_widget=False,
            track_server_events=False,
        )
        db_session.add(existing)
        db_session.commit()

        # Update with new data
        service = GoogleAnalyticsService(db_session)
        data = GoogleAnalyticsIntegrationCreate(
            measurement_id="G-NEWTEST456",
            measurement_protocol_api_secret="newsecret",
            enabled=True,
            track_frontend=True,
            track_embed_widget=True,
            track_server_events=True,
            custom_dimensions={"dim": "val"},
        )

        result = await service.create_or_update(test_tenant.id, data)

        # Verify update
        assert result.id == existing.id
        assert result.measurement_id == "G-NEWTEST456"
        assert result.enabled is True
        assert result.track_server_events is True

    @pytest.mark.asyncio
    async def test_create_with_invalid_measurement_id(self, db_session: Session, test_tenant):
        """Test creation fails with invalid measurement ID"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            GoogleAnalyticsIntegrationCreate(
                measurement_id="INVALID-ID",
                enabled=True,
                track_frontend=True,
                track_embed_widget=True,
                track_server_events=False,
            )

        assert "Invalid Measurement ID format" in str(exc_info.value)


class TestGetMethods:
    """Tests for get_by_tenant and get_by_id methods"""

    def test_get_by_tenant_found(self, db_session: Session, test_tenant):
        """Test getting integration by tenant ID"""
        integration = GoogleAnalyticsIntegration(
            id=uuid4(),
            tenant_id=test_tenant.id,
            measurement_id="G-TEST123",
            enabled=True,
            track_frontend=True,
            track_embed_widget=True,
            track_server_events=False,
        )
        db_session.add(integration)
        db_session.commit()

        service = GoogleAnalyticsService(db_session)
        result = service.get_by_tenant(test_tenant.id)

        assert result is not None
        assert result.tenant_id == test_tenant.id
        assert result.measurement_id == "G-TEST123"

    def test_get_by_id_found(self, db_session: Session, test_tenant):
        """Test getting integration by ID"""
        integration_id = uuid4()
        integration = GoogleAnalyticsIntegration(
            id=integration_id,
            tenant_id=test_tenant.id,
            measurement_id="G-TEST456",
            enabled=True,
            track_frontend=True,
            track_embed_widget=True,
            track_server_events=False,
        )
        db_session.add(integration)
        db_session.commit()

        service = GoogleAnalyticsService(db_session)
        result = service.get_by_id(integration_id)

        assert result is not None
        assert result.id == integration_id


class TestDelete:
    """Tests for delete method"""

    @pytest.mark.asyncio
    async def test_delete_existing_integration(self, db_session: Session, test_tenant):
        """Test deleting an existing integration"""
        integration = GoogleAnalyticsIntegration(
            id=uuid4(),
            tenant_id=test_tenant.id,
            measurement_id="G-DELETE123",
            enabled=True,
            track_frontend=True,
            track_embed_widget=True,
            track_server_events=False,
        )
        db_session.add(integration)
        db_session.commit()

        service = GoogleAnalyticsService(db_session)
        result = await service.delete(test_tenant.id)

        assert result is True

        # Verify deletion
        deleted = service.get_by_tenant(test_tenant.id)
        assert deleted is None


class TestConnectionTest:
    """Tests for test_connection method"""

    @pytest.mark.asyncio
    async def test_connection_integration_not_found(self, db_session: Session, test_tenant):
        """Test connection test when integration not found"""
        service = GoogleAnalyticsService(db_session)
        result = await service.test_connection(test_tenant.id)

        assert result.status == "failed"
        assert "not found" in result.message

    @pytest.mark.asyncio
    async def test_connection_integration_disabled(self, db_session: Session, test_tenant):
        """Test connection test when integration is disabled"""
        integration = GoogleAnalyticsIntegration(
            id=uuid4(),
            tenant_id=test_tenant.id,
            measurement_id="G-TEST123",
            enabled=False,
            track_frontend=True,
            track_embed_widget=True,
            track_server_events=False,
        )
        db_session.add(integration)
        db_session.commit()

        service = GoogleAnalyticsService(db_session)
        result = await service.test_connection(test_tenant.id)

        assert result.status == "failed"
        assert "disabled" in result.message

    @pytest.mark.asyncio
    async def test_connection_no_api_secret(self, db_session: Session, test_tenant):
        """Test connection test when API secret is not configured"""
        integration = GoogleAnalyticsIntegration(
            id=uuid4(),
            tenant_id=test_tenant.id,
            measurement_id="G-TEST123",
            enabled=True,
            measurement_protocol_api_secret=None,
            track_frontend=True,
            track_embed_widget=True,
            track_server_events=False,
        )
        db_session.add(integration)
        db_session.commit()

        service = GoogleAnalyticsService(db_session)
        result = await service.test_connection(test_tenant.id)

        assert result.status == "failed"
        assert "API Secret not configured" in result.message

    @pytest.mark.asyncio
    @patch("app.services.google_analytics_service.GA4MeasurementProtocol")
    async def test_connection_success(self, mock_ga4_class, db_session: Session, test_tenant):
        """Test successful connection test"""
        integration = GoogleAnalyticsIntegration(
            id=uuid4(),
            tenant_id=test_tenant.id,
            measurement_id="G-TEST123",
            measurement_protocol_api_secret="secret123",
            enabled=True,
            track_frontend=True,
            track_embed_widget=True,
            track_server_events=True,
        )
        db_session.add(integration)
        db_session.commit()

        # Mock GA4 client
        mock_client = Mock()
        mock_client.send_connection_test_event = AsyncMock(
            return_value={
                "status": "success",
                "message": "Connection test successful",
                "validation_messages": [],
            }
        )
        mock_ga4_class.return_value = mock_client

        service = GoogleAnalyticsService(db_session)
        result = await service.test_connection(test_tenant.id)

        assert result.status == "success"
        assert "successful" in result.message
