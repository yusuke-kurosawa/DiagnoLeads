"""
CRM Integration Models

Database models for CRM integrations (Salesforce, HubSpot).
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, Text, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base


class CRMIntegration(Base):
    """
    CRM Integration configuration for a tenant.

    Each tenant can have one CRM integration (Salesforce or HubSpot).
    Stores OAuth tokens (encrypted) and sync configuration.
    """

    __tablename__ = "crm_integrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    # CRM Type
    crm_type = Column(String(50), nullable=False)  # 'salesforce', 'hubspot'
    enabled = Column(Boolean, default=True, nullable=False)

    # OAuth Credentials (Encrypted)
    access_token_encrypted = Column(Text, nullable=True)
    refresh_token_encrypted = Column(Text, nullable=True)
    instance_url = Column(String(255), nullable=True)  # Salesforce instance URL
    expires_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Configuration
    field_mappings = Column(JSON, nullable=True, default=dict)  # Custom field mappings
    sync_config = Column(JSON, nullable=True, default=dict)  # Sync direction, frequency, etc.

    # Sync Status
    last_sync_at = Column(TIMESTAMP(timezone=True), nullable=True)
    total_synced = Column(String(50), default="0")  # Total records synced
    failed_syncs = Column(String(50), default="0")  # Failed sync count

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    tenant = relationship("Tenant", back_populates="crm_integration")
    sync_logs = relationship("CRMSyncLog", back_populates="integration", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        UniqueConstraint('tenant_id', name='uq_crm_integration_tenant'),
    )

    def encrypt_access_token(self, token: str):
        """
        Encrypt and store access token.

        TODO: Implement encryption in Phase 2
        For now, this is a placeholder.
        """
        # Placeholder - will implement with cryptography.fernet
        self.access_token_encrypted = token

    def decrypt_access_token(self) -> str:
        """
        Decrypt and return access token.

        TODO: Implement decryption in Phase 2
        For now, this is a placeholder.
        """
        # Placeholder - will implement with cryptography.fernet
        return self.access_token_encrypted or ""

    def encrypt_refresh_token(self, token: str):
        """
        Encrypt and store refresh token.

        TODO: Implement encryption in Phase 2
        """
        # Placeholder
        self.refresh_token_encrypted = token

    def decrypt_refresh_token(self) -> str:
        """
        Decrypt and return refresh token.

        TODO: Implement decryption in Phase 2
        """
        # Placeholder
        return self.refresh_token_encrypted or ""


class CRMSyncLog(Base):
    """
    Log of CRM synchronization operations.

    Tracks each sync attempt (success or failure) for auditing and retry logic.
    """

    __tablename__ = "crm_sync_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id = Column(UUID(as_uuid=True), ForeignKey("crm_integrations.id", ondelete="CASCADE"), nullable=False)
    lead_id = Column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True)

    # Sync Details
    sync_type = Column(String(20), nullable=False)  # 'create', 'update', 'delete'
    direction = Column(String(20), nullable=False)  # 'to_crm', 'from_crm'
    status = Column(String(20), nullable=False, default='pending')  # 'success', 'failed', 'pending'

    # CRM Record Info
    crm_record_id = Column(String(255), nullable=True)  # Salesforce/HubSpot record ID
    fields_synced = Column(JSON, nullable=True)  # List of fields synced

    # Error Handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(String(50), default="0")

    # Timestamps
    synced_at = Column(TIMESTAMP(timezone=True), nullable=True)  # When sync completed
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    integration = relationship("CRMIntegration", back_populates="sync_logs")
    lead = relationship("Lead")
