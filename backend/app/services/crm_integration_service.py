"""
CRM Integration Service

Manages CRM integrations and lead synchronization.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.crm_integration import CRMIntegration, CRMSyncLog
from app.models.lead import Lead
from app.integrations.crm.salesforce_client import SalesforceClient
from app.integrations.crm.hubspot_client import HubSpotClient


class CRMIntegrationService:
    """Service for managing CRM integrations and synchronization."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_integration(self, tenant_id: UUID) -> Optional[CRMIntegration]:
        """
        Get CRM integration for a tenant.

        Args:
            tenant_id: Tenant UUID

        Returns:
            CRMIntegration if exists, None otherwise
        """
        result = await self.db.execute(
            select(CRMIntegration).where(CRMIntegration.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def create_integration(
        self,
        tenant_id: UUID,
        crm_type: str,
        access_token: str,
        refresh_token: str,
        instance_url: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> CRMIntegration:
        """
        Create a new CRM integration.

        Args:
            tenant_id: Tenant UUID
            crm_type: 'salesforce' or 'hubspot'
            access_token: OAuth access token
            refresh_token: OAuth refresh token
            instance_url: Salesforce instance URL (optional)
            expires_at: Token expiration time (optional)

        Returns:
            Created CRMIntegration
        """
        integration = CRMIntegration(
            tenant_id=tenant_id,
            crm_type=crm_type,
            instance_url=instance_url,
            expires_at=expires_at,
        )

        # Encrypt and store tokens
        integration.encrypt_access_token(access_token)
        integration.encrypt_refresh_token(refresh_token)

        self.db.add(integration)
        await self.db.commit()
        await self.db.refresh(integration)

        return integration

    async def sync_lead_to_crm(
        self,
        lead_id: UUID,
        tenant_id: UUID,
        sync_type: str = "create",
        force: bool = False,
    ) -> CRMSyncLog:
        """
        Synchronize a lead to CRM.

        Args:
            lead_id: Lead UUID
            tenant_id: Tenant UUID
            sync_type: 'create', 'update', or 'delete'
            force: Force sync even if already synced

        Returns:
            CRMSyncLog with sync result

        Raises:
            ValueError: If CRM integration not configured or lead not found
        """
        # Get CRM integration
        integration = await self.get_integration(tenant_id)
        if not integration or not integration.enabled:
            raise ValueError("CRM integration not configured or disabled")

        # Get lead
        result = await self.db.execute(
            select(Lead).where(Lead.id == lead_id)
        )
        lead = result.scalar_one_or_none()
        if not lead:
            raise ValueError(f"Lead {lead_id} not found")

        # Create sync log
        sync_log = CRMSyncLog(
            integration_id=integration.id,
            lead_id=lead_id,
            sync_type=sync_type,
            direction="to_crm",
            status="pending",
        )

        try:
            # Get CRM client
            client = self._get_crm_client(integration)

            # Prepare lead data
            lead_data = self._prepare_lead_data(lead)

            # Sync to CRM
            if sync_type == "create":
                crm_id = await client.create_lead(lead_data)
                sync_log.crm_record_id = crm_id

                # Update lead with CRM ID
                # TODO: Add crm_external_id field to Lead model
                # lead.crm_external_id = crm_id

            elif sync_type == "update":
                # TODO: Get crm_external_id from lead
                crm_id = "placeholder"  # lead.crm_external_id
                await client.update_lead(crm_id, lead_data)
                sync_log.crm_record_id = crm_id

            elif sync_type == "delete":
                # TODO: Get crm_external_id from lead
                crm_id = "placeholder"  # lead.crm_external_id
                await client.delete_lead(crm_id)
                sync_log.crm_record_id = crm_id

            else:
                raise ValueError(f"Invalid sync_type: {sync_type}")

            # Mark as success
            sync_log.status = "success"
            sync_log.synced_at = datetime.now(timezone.utc)
            sync_log.fields_synced = list(lead_data.keys())

            # Update integration stats
            integration.last_sync_at = datetime.now(timezone.utc)
            integration.total_synced = str(int(integration.total_synced) + 1)

        except Exception as e:
            # Mark as failed
            sync_log.status = "failed"
            sync_log.error_message = str(e)
            integration.failed_syncs = str(int(integration.failed_syncs) + 1)

            # TODO: Schedule retry with Trigger.dev
            raise

        finally:
            self.db.add(sync_log)
            await self.db.commit()
            await self.db.refresh(sync_log)

        return sync_log

    def _get_crm_client(self, integration: CRMIntegration):
        """
        Get CRM client based on integration type.

        Args:
            integration: CRMIntegration instance

        Returns:
            SalesforceClient or HubSpotClient

        Raises:
            ValueError: If CRM type is not supported
        """
        config = {
            "access_token": integration.decrypt_access_token(),
            "refresh_token": integration.decrypt_refresh_token(),
            "instance_url": integration.instance_url,
            "field_mappings": integration.field_mappings or {},
        }

        if integration.crm_type == "salesforce":
            return SalesforceClient(integration.id, config)
        elif integration.crm_type == "hubspot":
            return HubSpotClient(integration.id, config)
        else:
            raise ValueError(f"Unsupported CRM type: {integration.crm_type}")

    def _prepare_lead_data(self, lead: Lead) -> Dict[str, Any]:
        """
        Prepare lead data for CRM sync.

        Args:
            lead: Lead instance

        Returns:
            Dictionary of lead data
        """
        return {
            "name": lead.name,
            "email": lead.email,
            "company": lead.company,
            "phone": lead.phone,
            "score": lead.score,
            "priority_level": lead.priority_level,
            # TODO: Add detected_challenges when available
            # "detected_challenges": lead.detected_challenges,
        }

    async def get_sync_logs(
        self,
        tenant_id: UUID,
        limit: int = 100,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> tuple[list[CRMSyncLog], int]:
        """
        Get sync logs for a tenant.

        Args:
            tenant_id: Tenant UUID
            limit: Maximum number of logs to return
            offset: Offset for pagination
            status: Filter by status ('success', 'failed', 'pending')

        Returns:
            Tuple of (logs, total_count)
        """
        # Get integration
        integration = await self.get_integration(tenant_id)
        if not integration:
            return [], 0

        # Build query
        query = select(CRMSyncLog).where(CRMSyncLog.integration_id == integration.id)

        if status:
            query = query.where(CRMSyncLog.status == status)

        # Get total count
        count_query = select(CRMSyncLog).where(CRMSyncLog.integration_id == integration.id)
        if status:
            count_query = count_query.where(CRMSyncLog.status == status)
        count_result = await self.db.execute(count_query)
        total = len(count_result.scalars().all())

        # Get logs
        query = query.order_by(CRMSyncLog.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        logs = result.scalars().all()

        return list(logs), total
