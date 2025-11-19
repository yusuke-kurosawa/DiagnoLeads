"""Google Analytics 4 Measurement Protocol Client

Sends events to GA4 using the Measurement Protocol API for server-side tracking.

Reference: https://developers.google.com/analytics/devguides/collection/protocol/ga4
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class GA4MeasurementProtocol:
    """Google Analytics 4 Measurement Protocol API Client

    Sends events to GA4 from the server-side for:
    - Important business events (lead generation, conversions)
    - Backup tracking when client-side is blocked
    - More accurate conversion measurement
    """

    ENDPOINT = "https://www.google-analytics.com/mp/collect"
    DEBUG_ENDPOINT = "https://www.google-analytics.com/debug/mp/collect"
    VALIDATION_ENDPOINT = "https://www.google-analytics.com/mp/collect/validate"

    def __init__(
        self,
        measurement_id: str,
        api_secret: str,
        debug: bool = False,
        timeout: float = 10.0,
    ):
        """Initialize GA4 Measurement Protocol client

        Args:
            measurement_id: GA4 Measurement ID (G-XXXXXXXXXX)
            api_secret: Measurement Protocol API Secret
            debug: Use debug endpoint for testing (default: False)
            timeout: Request timeout in seconds (default: 10.0)
        """
        self.measurement_id = measurement_id
        self.api_secret = api_secret
        self.timeout = timeout

        # Use debug endpoint if debug mode is enabled
        if debug:
            self.endpoint = self.DEBUG_ENDPOINT
        else:
            self.endpoint = self.ENDPOINT

    async def send_event(
        self,
        client_id: str,
        event_name: str,
        event_params: Optional[Dict] = None,
        user_properties: Optional[Dict] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        """Send a single event to GA4

        Args:
            client_id: Unique client identifier (UUID recommended)
            event_name: Event name (e.g., 'lead_generated')
            event_params: Event parameters (e.g., {'lead_score': 85})
            user_properties: User properties (e.g., {'tenant_id': 'uuid'})
            user_id: Optional user ID for cross-device tracking

        Returns:
            True if successful, False otherwise
        """
        if event_params is None:
            event_params = {}

        url = f"{self.endpoint}?measurement_id={self.measurement_id}&api_secret={self.api_secret}"

        payload = {
            "client_id": client_id,
            "events": [{"name": event_name, "params": event_params}],
        }

        # Add user_id if provided
        if user_id:
            payload["user_id"] = user_id

        # Add user_properties if provided
        if user_properties:
            payload["user_properties"] = user_properties

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()

                logger.info(f"GA4 event sent successfully: {event_name}, client_id: {client_id[:8]}..., params: {event_params}")
                return True

        except httpx.HTTPStatusError as e:
            logger.error(f"GA4 HTTP error sending event '{event_name}': status={e.response.status_code}, response={e.response.text}")
            return False

        except httpx.RequestError as e:
            logger.error(f"GA4 request error sending event '{event_name}': {str(e)}")
            return False

        except Exception as e:
            logger.error(f"GA4 unexpected error sending event '{event_name}': {str(e)}")
            return False

    async def send_batch_events(
        self,
        client_id: str,
        events: List[Dict],
        user_properties: Optional[Dict] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        """Send multiple events in a single request (batch)

        Args:
            client_id: Unique client identifier
            events: List of events, each with 'name' and 'params' keys
            user_properties: User properties shared across all events
            user_id: Optional user ID

        Returns:
            True if successful, False otherwise

        Example:
            events = [
                {"name": "assessment_started", "params": {"assessment_id": "uuid"}},
                {"name": "question_answered", "params": {"question_number": 1}}
            ]
        """
        if not events:
            logger.warning("GA4 batch send called with empty events list")
            return False

        url = f"{self.endpoint}?measurement_id={self.measurement_id}&api_secret={self.api_secret}"

        payload = {"client_id": client_id, "events": events}

        if user_id:
            payload["user_id"] = user_id

        if user_properties:
            payload["user_properties"] = user_properties

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()

                event_names = [e.get("name", "unknown") for e in events]
                logger.info(f"GA4 batch events sent successfully: {len(events)} events ({', '.join(event_names)}), client_id: {client_id[:8]}...")
                return True

        except httpx.HTTPStatusError as e:
            logger.error(f"GA4 HTTP error sending batch events: status={e.response.status_code}, response={e.response.text}")
            return False

        except httpx.RequestError as e:
            logger.error(f"GA4 request error sending batch events: {str(e)}")
            return False

        except Exception as e:
            logger.error(f"GA4 unexpected error sending batch events: {str(e)}")
            return False

    async def validate_event(self, client_id: str, event_name: str, event_params: Optional[Dict] = None) -> Dict:
        """Validate an event using the Measurement Protocol validation endpoint

        Args:
            client_id: Unique client identifier
            event_name: Event name to validate
            event_params: Event parameters

        Returns:
            Validation response from GA4 API
        """
        if event_params is None:
            event_params = {}

        url = f"https://www.google-analytics.com/debug/mp/collect?measurement_id={self.measurement_id}&api_secret={self.api_secret}"

        payload = {
            "client_id": client_id,
            "events": [{"name": event_name, "params": event_params}],
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"GA4 validation error: {str(e)}")
            return {"error": str(e)}

    async def send_connection_test_event(self, client_id: str) -> Dict:
        """Send a test event to verify GA4 connection

        Args:
            client_id: Test client identifier

        Returns:
            Dict with status and message
        """
        event_name = "connection_test"
        event_params = {
            "test": "DiagnoLeads GA4 Integration",
            "timestamp": datetime.utcnow().isoformat(),
        }

        success = await self.send_event(client_id=client_id, event_name=event_name, event_params=event_params)

        if success:
            return {
                "status": "success",
                "message": "Test event sent successfully to GA4. Check GA4 Realtime Report.",
                "event_name": event_name,
                "timestamp": datetime.utcnow(),
            }
        else:
            return {
                "status": "failed",
                "message": "Failed to send test event to GA4. Check credentials and network.",
                "error_details": "See server logs for details",
            }


# Convenience functions for common events


async def send_lead_generated_event(
    client: GA4MeasurementProtocol,
    client_id: str,
    assessment_id: str,
    lead_score: int,
    lead_tier: str,
    tenant_id: str,
) -> bool:
    """Send lead_generated event to GA4

    Args:
        client: GA4MeasurementProtocol instance
        client_id: Client identifier
        assessment_id: Assessment UUID
        lead_score: Lead score (0-100)
        lead_tier: Lead tier ('hot', 'warm', 'cold')
        tenant_id: Tenant UUID

    Returns:
        True if successful
    """
    return await client.send_event(
        client_id=client_id,
        event_name="lead_generated",
        event_params={
            "assessment_id": assessment_id,
            "lead_score": lead_score,
            "lead_tier": lead_tier,
            "tenant_id": tenant_id,
        },
    )


async def send_hot_lead_generated_event(
    client: GA4MeasurementProtocol,
    client_id: str,
    assessment_id: str,
    lead_score: int,
    estimated_value: int = 1000,
    tenant_id: str = "",
) -> bool:
    """Send hot_lead_generated conversion event to GA4

    Args:
        client: GA4MeasurementProtocol instance
        client_id: Client identifier
        assessment_id: Assessment UUID
        lead_score: Lead score (typically 80+)
        estimated_value: Estimated lead value in JPY (default: 1000)
        tenant_id: Tenant UUID

    Returns:
        True if successful
    """
    return await client.send_event(
        client_id=client_id,
        event_name="hot_lead_generated",
        event_params={
            "assessment_id": assessment_id,
            "lead_score": lead_score,
            "value": estimated_value,
            "currency": "JPY",
            "tenant_id": tenant_id,
        },
    )


async def send_assessment_completed_event(
    client: GA4MeasurementProtocol,
    client_id: str,
    assessment_id: str,
    total_time_seconds: int,
    questions_answered: int,
    tenant_id: str,
) -> bool:
    """Send assessment_completed event to GA4

    Args:
        client: GA4MeasurementProtocol instance
        client_id: Client identifier
        assessment_id: Assessment UUID
        total_time_seconds: Total time to complete assessment
        questions_answered: Number of questions answered
        tenant_id: Tenant UUID

    Returns:
        True if successful
    """
    return await client.send_event(
        client_id=client_id,
        event_name="assessment_completed",
        event_params={
            "assessment_id": assessment_id,
            "total_time_seconds": total_time_seconds,
            "questions_answered": questions_answered,
            "tenant_id": tenant_id,
        },
    )
