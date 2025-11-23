"""
Salesforce CRM Integration Client

Implements Salesforce REST API integration for lead synchronization.
"""

import httpx
from typing import Dict, Any
from app.integrations.crm.base import CRMClient
from app.integrations.microsoft.retry_policy import with_retry


class SalesforceClient(CRMClient):
    """Salesforce integration client."""

    API_VERSION = "v57.0"

    async def authenticate(self, code: str) -> Dict[str, str]:
        """
        Exchange OAuth code for access token.

        TODO: Implement full OAuth flow in Phase 2
        """
        # Placeholder for Phase 2 implementation
        raise NotImplementedError("Salesforce OAuth not yet implemented")

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Refresh Salesforce access token.

        TODO: Implement token refresh in Phase 2
        """
        # Placeholder for Phase 2 implementation
        raise NotImplementedError("Token refresh not yet implemented")

    @with_retry(max_retries=3)
    async def create_lead(self, lead_data: Dict[str, Any]) -> str:
        """
        Create a lead in Salesforce.

        Args:
            lead_data: Lead information with DiagnoLeads field names

        Returns:
            Salesforce Lead ID (18-character)

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        url = f"{self.config['instance_url']}/services/data/{self.API_VERSION}/sobjects/Lead"

        # Apply field mapping
        mapped_data = self._apply_field_mapping(lead_data)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                json=mapped_data,
                headers={
                    "Authorization": f"Bearer {self.config['access_token']}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()

            result = response.json()
            return result["id"]  # Salesforce Lead ID

    @with_retry(max_retries=3)
    async def update_lead(self, crm_id: str, lead_data: Dict[str, Any]) -> bool:
        """
        Update a lead in Salesforce.

        Args:
            crm_id: Salesforce Lead ID
            lead_data: Updated lead information

        Returns:
            True if update succeeded

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        url = f"{self.config['instance_url']}/services/data/{self.API_VERSION}/sobjects/Lead/{crm_id}"

        # Apply field mapping
        mapped_data = self._apply_field_mapping(lead_data)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.patch(
                url,
                json=mapped_data,
                headers={
                    "Authorization": f"Bearer {self.config['access_token']}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()

            return response.status_code == 204

    @with_retry(max_retries=3)
    async def get_lead(self, crm_id: str) -> Dict[str, Any]:
        """
        Retrieve a lead from Salesforce.

        Args:
            crm_id: Salesforce Lead ID

        Returns:
            Lead data from Salesforce

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        url = f"{self.config['instance_url']}/services/data/{self.API_VERSION}/sobjects/Lead/{crm_id}"

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
        Delete a lead from Salesforce.

        Args:
            crm_id: Salesforce Lead ID

        Returns:
            True if deletion succeeded

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        url = f"{self.config['instance_url']}/services/data/{self.API_VERSION}/sobjects/Lead/{crm_id}"

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
        Map DiagnoLeads fields to Salesforce Lead fields.

        Default mapping:
        - name → FirstName + LastName (split by space)
        - email → Email
        - company → Company
        - phone → Phone
        - score → LeadScore__c (custom field)
        - priority_level → Priority__c (custom field)

        Custom mappings can be configured in self.config["field_mappings"].

        Args:
            data: DiagnoLeads lead data

        Returns:
            Salesforce-formatted lead data
        """
        # Get custom mappings if configured
        custom_mappings = self.config.get("field_mappings", {})

        # Default field mapping
        default_mapping = {
            "email": "Email",
            "company": "Company",
            "phone": "Phone",
            "score": "LeadScore__c",
            "priority_level": "Priority__c",
        }

        mapped = {}

        # Handle name splitting (FirstName + LastName)
        if "name" in data and data["name"]:
            parts = data["name"].strip().split(" ", 1)
            mapped["FirstName"] = parts[0]
            mapped["LastName"] = parts[1] if len(parts) > 1 else parts[0]

        # Map other fields
        for diagno_field, salesforce_field in default_mapping.items():
            if diagno_field in data and data[diagno_field] is not None:
                # Apply custom mapping if exists
                target_field = custom_mappings.get(diagno_field, salesforce_field)
                mapped[target_field] = data[diagno_field]

        # Add detected challenges as JSON string (custom field)
        if "detected_challenges" in data and data["detected_challenges"]:
            import json

            mapped["DetectedChallenges__c"] = json.dumps(data["detected_challenges"])

        return mapped
