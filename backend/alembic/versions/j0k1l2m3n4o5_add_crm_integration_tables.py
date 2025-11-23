"""Add CRM integration tables

Revision ID: j0k1l2m3n4o5
Revises: i9j0k1l2m3n4
Create Date: 2025-11-23 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "j0k1l2m3n4o5"
down_revision: Union[str, None] = "i9j0k1l2m3n4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add CRM integration tables (Salesforce, HubSpot)"""

    # Create crm_integrations table
    op.create_table(
        "crm_integrations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        # CRM Type
        sa.Column("crm_type", sa.String(length=50), nullable=False),  # 'salesforce', 'hubspot'
        sa.Column("enabled", sa.Boolean(), default=True, nullable=False),
        # OAuth Credentials (Encrypted)
        sa.Column("access_token_encrypted", sa.Text(), nullable=True),
        sa.Column("refresh_token_encrypted", sa.Text(), nullable=True),
        sa.Column("instance_url", sa.String(length=255), nullable=True),  # Salesforce instance URL
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        # Configuration
        sa.Column("field_mappings", postgresql.JSONB(), nullable=True),  # Custom field mappings
        sa.Column("sync_config", postgresql.JSONB(), nullable=True),  # Sync direction, frequency, etc.
        # Sync Status
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_synced", sa.String(length=50), server_default="0", nullable=False),
        sa.Column("failed_syncs", sa.String(length=50), server_default="0", nullable=False),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), onupdate=sa.text("now()"), nullable=False),
        # Foreign keys
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        # Constraints
        sa.UniqueConstraint("tenant_id", name="uq_crm_integration_tenant"),
    )

    # Create indexes for crm_integrations
    op.create_index("idx_crm_integrations_tenant_id", "crm_integrations", ["tenant_id"], unique=False)
    op.create_index("idx_crm_integrations_crm_type", "crm_integrations", ["crm_type"], unique=False)
    op.create_index("idx_crm_integrations_enabled", "crm_integrations", ["enabled"], unique=False)

    # Create crm_sync_logs table
    op.create_table(
        "crm_sync_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("integration_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Sync Details
        sa.Column("sync_type", sa.String(length=20), nullable=False),  # 'create', 'update', 'delete'
        sa.Column("direction", sa.String(length=20), nullable=False),  # 'to_crm', 'from_crm'
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),  # 'success', 'failed', 'pending'
        # CRM Record Info
        sa.Column("crm_record_id", sa.String(length=255), nullable=True),  # Salesforce/HubSpot record ID
        sa.Column("fields_synced", postgresql.JSONB(), nullable=True),  # List of fields synced
        # Error Handling
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.String(length=50), server_default="0", nullable=False),
        # Timestamps
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),  # When sync completed
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        # Foreign keys
        sa.ForeignKeyConstraint(["integration_id"], ["crm_integrations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for crm_sync_logs
    op.create_index("idx_crm_sync_logs_integration_id", "crm_sync_logs", ["integration_id"], unique=False)
    op.create_index("idx_crm_sync_logs_lead_id", "crm_sync_logs", ["lead_id"], unique=False)
    op.create_index("idx_crm_sync_logs_status", "crm_sync_logs", ["status"], unique=False)
    op.create_index("idx_crm_sync_logs_created_at", "crm_sync_logs", ["created_at"], unique=False)
    op.create_index("idx_crm_sync_logs_integration_status", "crm_sync_logs", ["integration_id", "status"], unique=False)


def downgrade() -> None:
    """Remove CRM integration tables"""

    # Drop crm_sync_logs indexes
    op.drop_index("idx_crm_sync_logs_integration_status", table_name="crm_sync_logs")
    op.drop_index("idx_crm_sync_logs_created_at", table_name="crm_sync_logs")
    op.drop_index("idx_crm_sync_logs_status", table_name="crm_sync_logs")
    op.drop_index("idx_crm_sync_logs_lead_id", table_name="crm_sync_logs")
    op.drop_index("idx_crm_sync_logs_integration_id", table_name="crm_sync_logs")

    # Drop crm_sync_logs table
    op.drop_table("crm_sync_logs")

    # Drop crm_integrations indexes
    op.drop_index("idx_crm_integrations_enabled", table_name="crm_integrations")
    op.drop_index("idx_crm_integrations_crm_type", table_name="crm_integrations")
    op.drop_index("idx_crm_integrations_tenant_id", table_name="crm_integrations")

    # Drop crm_integrations table
    op.drop_table("crm_integrations")
