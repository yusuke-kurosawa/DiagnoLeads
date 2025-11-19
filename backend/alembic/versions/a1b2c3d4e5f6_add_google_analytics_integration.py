"""Add Google Analytics integration table

Revision ID: a1b2c3d4e5f6
Revises: f7e1c2d9b3a4
Create Date: 2025-11-18 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "f7e1c2d9b3a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Google Analytics integration table and configuration"""

    # Create google_analytics_integrations table
    op.create_table(
        "google_analytics_integrations",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("measurement_id", sa.String(length=20), nullable=False),
        sa.Column(
            "measurement_protocol_api_secret", sa.String(length=255), nullable=True
        ),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "track_frontend", sa.Boolean(), nullable=False, server_default="true"
        ),
        sa.Column(
            "track_embed_widget", sa.Boolean(), nullable=False, server_default="true"
        ),
        sa.Column(
            "track_server_events", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("custom_dimensions", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
            onupdate=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", name="uq_ga_integration_tenant"),
    )

    # Create indexes
    op.create_index(
        "ix_ga_integration_tenant_id", "google_analytics_integrations", ["tenant_id"]
    )
    op.create_index(
        "ix_ga_integration_enabled", "google_analytics_integrations", ["enabled"]
    )

    # Enable Row-Level Security (RLS) for multi-tenant isolation
    op.execute("""
        ALTER TABLE google_analytics_integrations ENABLE ROW LEVEL SECURITY;
    """)

    # Create RLS policy for tenant isolation
    op.execute("""
        CREATE POLICY tenant_isolation_policy_ga_integration
        ON google_analytics_integrations
        FOR ALL
        USING (tenant_id::text = current_setting('app.current_tenant_id', true));
    """)


def downgrade() -> None:
    """Remove Google Analytics integration table"""

    # Drop RLS policy
    op.execute("""
        DROP POLICY IF EXISTS tenant_isolation_policy_ga_integration
        ON google_analytics_integrations;
    """)

    # Disable RLS
    op.execute("""
        ALTER TABLE google_analytics_integrations DISABLE ROW LEVEL SECURITY;
    """)

    # Drop indexes
    op.drop_index(
        "ix_ga_integration_enabled", table_name="google_analytics_integrations"
    )
    op.drop_index(
        "ix_ga_integration_tenant_id", table_name="google_analytics_integrations"
    )

    # Drop table
    op.drop_table("google_analytics_integrations")
