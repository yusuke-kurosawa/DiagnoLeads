"""Google Analytics Integration Service

Business logic for managing GA4 integrations.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID
import uuid
import logging
from typing import Optional

from app.models.google_analytics_integration import GoogleAnalyticsIntegration
from app.schemas.google_analytics import (
    GoogleAnalyticsIntegrationCreate,
    GoogleAnalyticsTestResponse
)
from app.integrations.google_analytics import GA4MeasurementProtocol

logger = logging.getLogger(__name__)


class GoogleAnalyticsService:
    """Service for managing Google Analytics 4 integrations"""

    def __init__(self, db: Session):
        self.db = db

    async def create_or_update(
        self,
        tenant_id: UUID,
        data: GoogleAnalyticsIntegrationCreate
    ) -> GoogleAnalyticsIntegration:
        """Create or update GA4 integration for a tenant

        Args:
            tenant_id: Tenant UUID
            data: GA4 integration configuration

        Returns:
            GoogleAnalyticsIntegration instance

        Raises:
            ValueError: If measurement_id format is invalid
        """
        # Validate measurement_id format
        if not GoogleAnalyticsIntegration.validate_measurement_id(data.measurement_id):
            raise ValueError(
                "Invalid Measurement ID format. Expected format: G-XXXXXXXXXX"
            )

        # Check if integration already exists
        existing = self.get_by_tenant(tenant_id)

        if existing:
            # Update existing integration
            existing.measurement_id = data.measurement_id
            existing.enabled = data.enabled
            existing.track_frontend = data.track_frontend
            existing.track_embed_widget = data.track_embed_widget
            existing.track_server_events = data.track_server_events
            existing.custom_dimensions = data.custom_dimensions

            # Update API secret if provided
            if data.measurement_protocol_api_secret:
                # TODO: Encrypt API secret before storing
                existing.measurement_protocol_api_secret = data.measurement_protocol_api_secret

            self.db.commit()
            self.db.refresh(existing)

            logger.info(f"Updated GA4 integration for tenant {tenant_id}")
            return existing

        else:
            # Create new integration
            integration = GoogleAnalyticsIntegration(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                measurement_id=data.measurement_id,
                measurement_protocol_api_secret=data.measurement_protocol_api_secret,  # TODO: Encrypt
                enabled=data.enabled,
                track_frontend=data.track_frontend,
                track_embed_widget=data.track_embed_widget,
                track_server_events=data.track_server_events,
                custom_dimensions=data.custom_dimensions
            )

            try:
                self.db.add(integration)
                self.db.commit()
                self.db.refresh(integration)

                logger.info(f"Created GA4 integration for tenant {tenant_id}")
                return integration

            except IntegrityError as e:
                self.db.rollback()
                logger.error(f"Failed to create GA4 integration: {str(e)}")
                raise ValueError("Failed to create GA4 integration. Tenant already has an integration.")

    def get_by_tenant(self, tenant_id: UUID) -> Optional[GoogleAnalyticsIntegration]:
        """Get GA4 integration by tenant ID

        Args:
            tenant_id: Tenant UUID

        Returns:
            GoogleAnalyticsIntegration or None if not found
        """
        return self.db.query(GoogleAnalyticsIntegration).filter(
            GoogleAnalyticsIntegration.tenant_id == tenant_id
        ).first()

    def get_by_id(self, integration_id: UUID) -> Optional[GoogleAnalyticsIntegration]:
        """Get GA4 integration by ID

        Args:
            integration_id: Integration UUID

        Returns:
            GoogleAnalyticsIntegration or None if not found
        """
        return self.db.query(GoogleAnalyticsIntegration).filter(
            GoogleAnalyticsIntegration.id == integration_id
        ).first()

    async def delete(self, tenant_id: UUID) -> bool:
        """Delete GA4 integration for a tenant

        Args:
            tenant_id: Tenant UUID

        Returns:
            True if deleted, False if not found
        """
        integration = self.get_by_tenant(tenant_id)
        if not integration:
            return False

        self.db.delete(integration)
        self.db.commit()

        logger.info(f"Deleted GA4 integration for tenant {tenant_id}")
        return True

    async def test_connection(self, tenant_id: UUID) -> GoogleAnalyticsTestResponse:
        """Test GA4 connection by sending a test event

        Args:
            tenant_id: Tenant UUID

        Returns:
            GoogleAnalyticsTestResponse with test result
        """
        integration = self.get_by_tenant(tenant_id)

        if not integration:
            return GoogleAnalyticsTestResponse(
                status="failed",
                message="Google Analytics integration not found for this tenant",
                error_details="Please configure GA4 integration first"
            )

        if not integration.enabled:
            return GoogleAnalyticsTestResponse(
                status="failed",
                message="Google Analytics integration is disabled",
                error_details="Enable GA4 integration in settings"
            )

        # Check if API secret is configured for server-side tracking
        if not integration.measurement_protocol_api_secret:
            return GoogleAnalyticsTestResponse(
                status="failed",
                message="Measurement Protocol API Secret not configured",
                error_details="Server-side tracking requires API Secret. Configure in settings."
            )

        # Create GA4 client
        client = GA4MeasurementProtocol(
            measurement_id=integration.measurement_id,
            api_secret=integration.measurement_protocol_api_secret,  # TODO: Decrypt
            debug=False
        )

        # Send test event
        test_client_id = f"test-{uuid.uuid4()}"
        result = await client.send_connection_test_event(test_client_id)

        return GoogleAnalyticsTestResponse(**result)

    def get_public_config(self, assessment_id: UUID) -> Optional[dict]:
        """Get public GA4 configuration for embed widget

        Args:
            assessment_id: Assessment UUID

        Returns:
            Public GA4 configuration (measurement_id, enabled, track_embed_widget)
            or None if not found
        """
        # TODO: Implement assessment -> tenant lookup
        # For now, this is a placeholder
        # In production, fetch tenant_id from assessment table, then get GA4 config

        # Example implementation:
        # assessment = self.db.query(Assessment).filter(Assessment.id == assessment_id).first()
        # if not assessment:
        #     return None
        #
        # integration = self.get_by_tenant(assessment.tenant_id)
        # if not integration or not integration.enabled:
        #     return None
        #
        # return {
        #     "measurement_id": integration.measurement_id,
        #     "enabled": integration.enabled,
        #     "track_embed_widget": integration.track_embed_widget
        # }

        logger.warning("get_public_config not fully implemented - requires Assessment model")
        return None
