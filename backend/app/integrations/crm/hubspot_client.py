"""
HubSpot CRM Integration Client

Implements HubSpot v3 API integration for contact synchronization.
"""

import httpx
from typing import Dict, Any
from app.integrations.crm.base import CRMClient
from app.integrations.microsoft.retry_policy import with_retry


class HubSpotClient(CRMClient):
    """HubSpot integration client."""

    BASE_URL = "https://api.hubapi.com"

    async def authenticate(self, code: str) -> Dict[str, str]:
        """
        Exchange OAuth code for access token.

        TODO: Implement full OAuth flow in Phase 2
        """
        # Placeholder for Phase 2 implementation
        raise NotImplementedError("HubSpot OAuth not yet implemented")

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Refresh HubSpot access token.

        TODO: Implement token refresh in Phase 2
        """
        # Placeholder for Phase 2 implementation
        raise NotImplementedError("Token refresh not yet implemented")

    @with_retry(max_retries=3)
    async def create_lead(self, lead_data: Dict[str, Any]) -> str:
        """
        Create a contact in HubSpot.

        Note: HubSpot uses "Contact" instead of "Lead".

        Args:
            lead_data: Lead information with DiagnoLeads field names

        Returns:
            HubSpot Contact ID

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        url = f"{self.BASE_URL}/crm/v3/objects/contacts"

        # Apply field mapping
        properties = self._apply_field_mapping(lead_data)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                json={"properties": properties},
                headers={
                    "Authorization": f"Bearer {self.config['access_token']}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()

            result = response.json()
            return result["id"]  # HubSpot Contact ID

    @with_retry(max_retries=3)
    async def update_lead(self, crm_id: str, lead_data: Dict[str, Any]) -> bool:
        """
        Update a contact in HubSpot.

        Args:
            crm_id: HubSpot Contact ID
            lead_data: Updated lead information

        Returns:
            True if update succeeded

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        url = f"{self.BASE_URL}/crm/v3/objects/contacts/{crm_id}"

        # Apply field mapping
        properties = self._apply_field_mapping(lead_data)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.patch(
                url,
                json={"properties": properties},
                headers={
                    "Authorization": f"Bearer {self.config['access_token']}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()

            return response.status_code == 200

    @with_retry(max_retries=3)
    async def get_lead(self, crm_id: str) -> Dict[str, Any]:
        """
        Retrieve a contact from HubSpot.

        Args:
            crm_id: HubSpot Contact ID

        Returns:
            Contact data from HubSpot

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        url = f"{self.BASE_URL}/crm/v3/objects/contacts/{crm_id}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                headers={
                    "Authorization": f"Bearer {self.config['access_token']}",
                },
            )
            response.raise_for_status()

            return response.json()

    @with_retry(max_retries=3)
    async def delete_lead(self, crm_id: str) -> bool:
        """
        Delete a contact from HubSpot.

        Args:
            crm_id: HubSpot Contact ID

        Returns:
            True if deletion succeeded

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        url = f"{self.BASE_URL}/crm/v3/objects/contacts/{crm_id}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                url,
                headers={
                    "Authorization": f"Bearer {self.config['access_token']}",
                },
            )
            response.raise_for_status()

            return response.status_code == 204

    def _apply_field_mapping(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map DiagnoLeads fields to HubSpot Contact properties.

        Default mapping:
        - name → firstname + lastname (split by space)
        - email → email
        - company → company
        - phone → phone
        - score → hs_lead_score
        - priority_level → lead_priority (custom property)

        Custom mappings can be configured in self.config["field_mappings"].

        Args:
            data: DiagnoLeads lead data

        Returns:
            HubSpot-formatted contact properties
        """
        # Get custom mappings if configured
        custom_mappings = self.config.get("field_mappings", {})

        # Default field mapping
        default_mapping = {
            "email": "email",
            "company": "company",
            "phone": "phone",
            "score": "hs_lead_score",
            "priority_level": "lead_priority",
        }

        properties = {}

        # Handle name splitting (firstname + lastname)
        if "name" in data and data["name"]:
            parts = data["name"].strip().split(" ", 1)
            properties["firstname"] = parts[0]
            properties["lastname"] = parts[1] if len(parts) > 1 else ""

        # Map other fields
        for diagno_field, hubspot_prop in default_mapping.items():
            if diagno_field in data and data[diagno_field] is not None:
                # Apply custom mapping if exists
                target_prop = custom_mappings.get(diagno_field, hubspot_prop)
                # HubSpot properties must be strings
                properties[target_prop] = str(data[diagno_field])

        # Add detected challenges as JSON string (custom property)
        if "detected_challenges" in data and data["detected_challenges"]:
            import json

            properties["detected_challenges"] = json.dumps(data["detected_challenges"])

        return properties
