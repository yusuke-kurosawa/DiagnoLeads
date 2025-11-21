"""Add error logs table

Revision ID: i9j0k1l2m3n4
Revises: h7i8j9k0l1m2
Create Date: 2025-11-19 15:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "i9j0k1l2m3n4"
down_revision: Union[str, None] = "h7i8j9k0l1m2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add error logs table for tracking application errors"""

    # Create error_logs table
    op.create_table(
        "error_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Error classification
        sa.Column("error_type", sa.String(length=100), nullable=False),
        sa.Column("error_code", sa.String(length=20), nullable=True),
        sa.Column("severity", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        # Error details
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("stack_trace", sa.Text(), nullable=True),
        # Request context
        sa.Column("endpoint", sa.String(length=200), nullable=True),
        sa.Column("method", sa.String(length=10), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        # Request/Response data
        sa.Column("request_body", postgresql.JSONB(), nullable=True),
        sa.Column("request_headers", postgresql.JSONB(), nullable=True),
        sa.Column("response_body", postgresql.JSONB(), nullable=True),
        # Performance metrics
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        # Environment & metadata
        sa.Column("environment", sa.String(length=20), nullable=False, server_default="development"),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        # Additional context
        sa.Column("context", postgresql.JSONB(), nullable=True),
        sa.Column("correlation_id", sa.String(length=100), nullable=True),
        # CICD specific
        sa.Column("workflow_name", sa.String(length=200), nullable=True),
        sa.Column("job_name", sa.String(length=200), nullable=True),
        sa.Column("run_id", sa.String(length=100), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        # Foreign keys
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for efficient querying
    op.create_index("idx_error_logs_tenant_id", "error_logs", ["tenant_id"], unique=False)
    op.create_index("idx_error_logs_error_type", "error_logs", ["error_type"], unique=False)
    op.create_index("idx_error_logs_endpoint", "error_logs", ["endpoint"], unique=False)
    op.create_index("idx_error_logs_created_at", "error_logs", ["created_at"], unique=False)
    op.create_index("idx_error_logs_correlation_id", "error_logs", ["correlation_id"], unique=False)
    op.create_index("idx_error_logs_tenant_created", "error_logs", ["tenant_id", "created_at"], unique=False)
    op.create_index("idx_error_logs_type_created", "error_logs", ["error_type", "created_at"], unique=False)


def downgrade() -> None:
    """Remove error logs table"""

    # Drop indexes
    op.drop_index("idx_error_logs_type_created", table_name="error_logs")
    op.drop_index("idx_error_logs_tenant_created", table_name="error_logs")
    op.drop_index("idx_error_logs_correlation_id", table_name="error_logs")
    op.drop_index("idx_error_logs_created_at", table_name="error_logs")
    op.drop_index("idx_error_logs_endpoint", table_name="error_logs")
    op.drop_index("idx_error_logs_error_type", table_name="error_logs")
    op.drop_index("idx_error_logs_tenant_id", table_name="error_logs")

    # Drop table
    op.drop_table("error_logs")
