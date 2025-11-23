"""Add topics and industries tables

Revision ID: j0k1l2m3n4o5
Revises: i9j0k1l2m3n4
Create Date: 2025-11-21 21:06:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "j0k1l2m3n4o5"
down_revision: Union[str, None] = "i9j0k1l2m3n4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add topics and industries tables for assessment categorization"""

    # Create topics table
    op.create_table(
        "topics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("color", sa.String(length=7), nullable=True),
        sa.Column("icon", sa.String(length=50), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="999"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "name", name="uq_topics_tenant_name"),
    )

    # Create industries table
    op.create_table(
        "industries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("color", sa.String(length=7), nullable=True),
        sa.Column("icon", sa.String(length=50), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="999"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "name", name="uq_industries_tenant_name"),
    )

    # Create indexes for efficient querying
    op.create_index("ix_topics_tenant_id", "topics", ["tenant_id"])
    op.create_index("ix_topics_is_active", "topics", ["is_active"])
    op.create_index("ix_industries_tenant_id", "industries", ["tenant_id"])
    op.create_index("ix_industries_is_active", "industries", ["is_active"])


def downgrade() -> None:
    """Remove topics and industries tables"""
    op.drop_index("ix_industries_is_active", table_name="industries")
    op.drop_index("ix_industries_tenant_id", table_name="industries")
    op.drop_index("ix_topics_is_active", table_name="topics")
    op.drop_index("ix_topics_tenant_id", table_name="topics")
    op.drop_table("industries")
    op.drop_table("topics")
