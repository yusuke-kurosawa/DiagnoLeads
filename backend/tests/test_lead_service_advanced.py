"""
Advanced Tests for Lead Service

Test coverage for GA4 events, Teams notifications, and edge cases
Target: 100% coverage for lead_service.py
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.models.google_analytics_integration import GoogleAnalyticsIntegration
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadStatusUpdate
from app.services.lead_service import LeadService


class TestLeadServiceGA4Integration:
    """Tests for GA4 event tracking"""

    @pytest.mark.asyncio
    async def test_send_ga4_event_success(self, db_session, test_tenant, test_user):
        """Test successful GA4 event sending"""
        service = LeadService(db_session)

        # Create GA4 integration
        ga_integration = GoogleAnalyticsIntegration(
            tenant_id=test_tenant.id,
            measurement_id="G-TEST123456",
            measurement_protocol_api_secret="test-secret",
            enabled=True,
            track_server_events=True,
        )
        db_session.add(ga_integration)
        db_session.commit()

        with patch("app.services.lead_service.GA4MeasurementProtocol") as mock_ga4:
            mock_client = MagicMock()
            mock_client.send_event = AsyncMock(return_value=True)
            mock_ga4.return_value = mock_client

            await service._send_ga4_event(
                tenant_id=test_tenant.id, event_name="lead_created", event_params={"score": 80}
            )

            mock_client.send_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_ga4_event_no_integration(self, db_session, test_tenant):
        """Test GA4 event when no integration exists"""
        service = LeadService(db_session)

        # Should not raise error, just return
        await service._send_ga4_event(tenant_id=test_tenant.id, event_name="test_event", event_params={})

    @pytest.mark.asyncio
    async def test_send_ga4_event_disabled(self, db_session, test_tenant):
        """Test GA4 event when integration is disabled"""
        service = LeadService(db_session)

        # Create disabled GA4 integration
        ga_integration = GoogleAnalyticsIntegration(
            tenant_id=test_tenant.id,
            measurement_id="G-TEST123456",
            measurement_protocol_api_secret="test-secret",
            enabled=False,  # Disabled
            track_server_events=True,
        )
        db_session.add(ga_integration)
        db_session.commit()

        with patch("app.services.lead_service.GA4MeasurementProtocol") as mock_ga4:
            await service._send_ga4_event(tenant_id=test_tenant.id, event_name="test_event", event_params={})

            # Should not create client
            mock_ga4.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_ga4_event_server_tracking_disabled(self, db_session, test_tenant):
        """Test GA4 event when server-side tracking is disabled"""
        service = LeadService(db_session)

        # Create GA4 integration without server tracking
        ga_integration = GoogleAnalyticsIntegration(
            tenant_id=test_tenant.id,
            measurement_id="G-TEST123456",
            measurement_protocol_api_secret="test-secret",
            enabled=True,
            track_server_events=False,  # Server events disabled
        )
        db_session.add(ga_integration)
        db_session.commit()

        with patch("app.services.lead_service.GA4MeasurementProtocol") as mock_ga4:
            await service._send_ga4_event(tenant_id=test_tenant.id, event_name="test_event", event_params={})

            mock_ga4.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_ga4_event_no_api_secret(self, db_session, test_tenant):
        """Test GA4 event when API secret is not configured"""
        service = LeadService(db_session)

        # Create GA4 integration without API secret
        ga_integration = GoogleAnalyticsIntegration(
            tenant_id=test_tenant.id,
            measurement_id="G-TEST123456",
            measurement_protocol_api_secret=None,  # No API secret
            enabled=True,
            track_server_events=True,
        )
        db_session.add(ga_integration)
        db_session.commit()

        with patch("app.services.lead_service.GA4MeasurementProtocol") as mock_ga4:
            await service._send_ga4_event(tenant_id=test_tenant.id, event_name="test_event", event_params={})

            mock_ga4.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_ga4_event_exception_handling(self, db_session, test_tenant):
        """Test GA4 event handles exceptions gracefully"""
        service = LeadService(db_session)

        # Create GA4 integration
        ga_integration = GoogleAnalyticsIntegration(
            tenant_id=test_tenant.id,
            measurement_id="G-TEST123456",
            measurement_protocol_api_secret="test-secret",
            enabled=True,
            track_server_events=True,
        )
        db_session.add(ga_integration)
        db_session.commit()

        with patch("app.services.lead_service.GA4MeasurementProtocol") as mock_ga4:
            mock_ga4.side_effect = Exception("Connection error")

            # Should not raise, just log error
            await service._send_ga4_event(tenant_id=test_tenant.id, event_name="test_event", event_params={})

    @pytest.mark.asyncio
    async def test_send_ga4_event_with_custom_client_id(self, db_session, test_tenant):
        """Test GA4 event with custom client ID"""
        service = LeadService(db_session)

        # Create GA4 integration
        ga_integration = GoogleAnalyticsIntegration(
            tenant_id=test_tenant.id,
            measurement_id="G-TEST123456",
            measurement_protocol_api_secret="test-secret",
            enabled=True,
            track_server_events=True,
        )
        db_session.add(ga_integration)
        db_session.commit()

        with patch("app.services.lead_service.GA4MeasurementProtocol") as mock_ga4:
            mock_client = MagicMock()
            mock_client.send_event = AsyncMock(return_value=True)
            mock_ga4.return_value = mock_client

            custom_client_id = "custom-client-123"
            await service._send_ga4_event(
                tenant_id=test_tenant.id, event_name="test_event", event_params={}, client_id=custom_client_id
            )

            # Verify client_id was passed
            call_args = mock_client.send_event.call_args
            assert call_args[1]["client_id"] == custom_client_id


class TestLeadServiceTeamsIntegration:
    """Tests for Teams notification"""

    @pytest.mark.asyncio
    async def test_send_teams_notification_not_available(self, db_session, test_tenant, test_user):
        """Test Teams notification when integration not available"""
        service = LeadService(db_session)
        service._teams_notification_enabled = False

        lead = Lead(
            tenant_id=test_tenant.id,
            name="Test Lead",
            email="test@example.com",
            score=80,
            status="new",
            created_by=test_user.id,
        )

        # Should not raise error when disabled
        await service._send_teams_notification(lead, test_tenant)


class TestLeadServiceCreateWithIntegrations:
    """Tests for create method with integrations"""

    def test_create_lead_with_duplicate_email_error_message(self, db_session, test_tenant, test_user):
        """Test create lead with duplicate email shows proper error"""
        service = LeadService(db_session)

        # Create first lead
        data1 = LeadCreate(name="Lead 1", email="duplicate@example.com", status="new")
        service.create(data1, test_tenant.id, test_user.id)

        # Try to create duplicate
        data2 = LeadCreate(name="Lead 2", email="duplicate@example.com", status="new")

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            service.create(data2, test_tenant.id, test_user.id)

        assert "already exists" in str(exc_info.value.detail)
        assert exc_info.value.status_code == 400


class TestLeadServiceUpdateStatus:
    """Tests for update_status method edge cases"""

    def test_update_status_from_converted_prevention(self, db_session, test_tenant, test_user):
        """Test that converted status cannot be changed"""
        service = LeadService(db_session)

        # Create converted lead
        lead = Lead(
            tenant_id=test_tenant.id,
            name="Converted Lead",
            email="converted@example.com",
            score=90,
            status="converted",
            created_by=test_user.id,
        )
        db_session.add(lead)
        db_session.commit()

        # Try to change status
        status_update = LeadStatusUpdate(status="qualified")

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            service.update_status(lead.id, status_update, test_tenant.id, test_user.id)

        assert "converted" in str(exc_info.value.detail).lower()

    def test_update_status_updates_last_contacted(self, db_session, test_tenant, test_user):
        """Test that updating to contacted sets last_contacted_at"""
        service = LeadService(db_session)

        lead = Lead(
            tenant_id=test_tenant.id,
            name="Test Lead",
            email="test@example.com",
            score=70,
            status="new",
            created_by=test_user.id,
        )
        db_session.add(lead)
        db_session.commit()

        status_update = LeadStatusUpdate(status="contacted")
        updated = service.update_status(lead.id, status_update, test_tenant.id, test_user.id)

        assert updated.status == "contacted"
        assert updated.last_contacted_at is not None

    def test_update_status_not_found(self, db_session, test_tenant, test_user):
        """Test updating status of non-existent lead"""
        service = LeadService(db_session)

        status_update = LeadStatusUpdate(status="qualified")
        updated = service.update_status(uuid4(), status_update, test_tenant.id, test_user.id)

        assert updated is None


class TestLeadServiceUpdateScore:
    """Tests for update_score method edge cases"""

    def test_update_score_not_found(self, db_session, test_tenant):
        """Test updating score of non-existent lead"""
        service = LeadService(db_session)

        from app.schemas.lead import LeadScoreUpdate

        score_update = LeadScoreUpdate(score=85)
        updated = service.update_score(uuid4(), score_update, test_tenant.id)

        assert updated is None
