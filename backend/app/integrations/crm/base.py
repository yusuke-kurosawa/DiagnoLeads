"""
CRM Integration Base Class

Abstract base class for CRM integrations (Salesforce, HubSpot).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from uuid import UUID


class CRMClient(ABC):
    """Base class for CRM integrations."""

    def __init__(self, integration_id: UUID, config: Dict[str, Any]):
        """
        Initialize CRM client.

        Args:
            integration_id: CRM integration ID
            config: Configuration including access_token, instance_url, etc.
        """
        self.integration_id = integration_id
        self.config = config

    @abstractmethod
    async def authenticate(self, code: str, redirect_uri: str) -> Dict[str, str]:
        """
        Exchange OAuth authorization code for tokens.

        Args:
            code: OAuth authorization code
            redirect_uri: Redirect URI used in authorization request

        Returns:
            Dictionary with access_token, refresh_token, expires_at, and optionally instance_url

        Raises:
            HTTPException: If authentication fails
        """
        pass

    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            Dictionary with new access_token and expires_in

        Raises:
            HTTPException: If token refresh fails
        """
        pass

    @abstractmethod
    async def create_lead(self, lead_data: Dict[str, Any]) -> str:
        """
        Create a lead in the CRM.

        Args:
            lead_data: Lead information (name, email, company, etc.)

        Returns:
            CRM record ID (e.g., Salesforce Lead ID)

        Raises:
            HTTPException: If lead creation fails
        """
        pass

    @abstractmethod
    async def update_lead(self, crm_id: str, lead_data: Dict[str, Any]) -> bool:
        """
        Update a lead in the CRM.

        Args:
            crm_id: CRM record ID
            lead_data: Updated lead information

        Returns:
            True if update succeeded

        Raises:
            HTTPException: If lead update fails
        """
        pass

    @abstractmethod
    async def get_lead(self, crm_id: str) -> Dict[str, Any]:
        """
        Retrieve a lead from the CRM.

        Args:
            crm_id: CRM record ID

        Returns:
            Lead data from CRM

        Raises:
            HTTPException: If lead retrieval fails
        """
        pass

    @abstractmethod
    async def delete_lead(self, crm_id: str) -> bool:
        """
        Delete a lead from the CRM.

        Args:
            crm_id: CRM record ID

        Returns:
            True if deletion succeeded

        Raises:
            HTTPException: If lead deletion fails
        """
        pass

    def _apply_field_mapping(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply field mappings from DiagnoLeads to CRM fields.

        This is a common utility method that can be overridden by subclasses.

        Args:
            data: DiagnoLeads lead data

        Returns:
            Mapped data for CRM
        """
        # Default implementation - should be overridden
        return data
