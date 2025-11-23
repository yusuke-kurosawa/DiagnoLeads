"""
Salesforce CRM Integration Client

Implements Salesforce REST API integration for lead synchronization.
"""

import httpx
from typing import Dict, Any
from datetime import datetime, timezone, timedelta
from app.integrations.crm.base import CRMClient
from app.integrations.microsoft.retry_policy import with_retry
from app.core.config import settings


class SalesforceClient(CRMClient):
    """Salesforce integration client."""

    API_VERSION = "v57.0"

    async def authenticate(self, code: str, redirect_uri: str) -> Dict[str, str]:
        """
        Exchange OAuth authorization code for access token.

        Salesforce OAuth 2.0 token endpoint:
        POST https://login.salesforce.com/services/oauth2/token

        Args:
            code: Authorization code from OAuth callback
            redirect_uri: Redirect URI used in authorization request

        Returns:
            Dictionary containing:
            - access_token: OAuth access token
            - refresh_token: OAuth refresh token
            - instance_url: Salesforce instance URL
            - expires_at: Token expiration datetime (ISO format)

        Raises:
            httpx.HTTPStatusError: If token exchange fails
        """
        token_url = "https://login.salesforce.com/services/oauth2/token"

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": settings.SALESFORCE_CLIENT_ID,
            "client_secret": settings.SALESFORCE_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()

            result = response.json()

            # Salesforce tokens typically expire in 2 hours
            expires_at = datetime.now(timezone.utc) + timedelta(hours=2)

            return {
                "access_token": result["access_token"],
                "refresh_token": result.get("refresh_token", ""),
                "instance_url": result["instance_url"],
                "expires_at": expires_at.isoformat(),
            }

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Refresh Salesforce access token using refresh token.

        Salesforce refresh token endpoint:
        POST https://login.salesforce.com/services/oauth2/token

        Args:
            refresh_token: Refresh token from initial OAuth flow

        Returns:
            Dictionary containing:
            - access_token: New OAuth access token
            - instance_url: Salesforce instance URL
            - expires_at: Token expiration datetime (ISO format)

        Raises:
            httpx.HTTPStatusError: If token refresh fails
        """
        token_url = "https://login.salesforce.com/services/oauth2/token"

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": settings.SALESFORCE_CLIENT_ID,
            "client_secret": settings.SALESFORCE_CLIENT_SECRET,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()

            result = response.json()

            # Salesforce tokens typically expire in 2 hours
            expires_at = datetime.now(timezone.utc) + timedelta(hours=2)

            return {
                "access_token": result["access_token"],
                "instance_url": result.get("instance_url", self.config.get("instance_url", "")),
                "expires_at": expires_at.isoformat(),
            }

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
