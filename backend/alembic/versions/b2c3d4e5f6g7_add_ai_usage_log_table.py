"""Add AI usage log table

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-11-18 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add AI usage log table for tracking API usage and costs"""

    # Create ai_usage_logs table
    op.create_table(
        'ai_usage_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('operation', sa.String(length=100), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('input_tokens', sa.Integer(), nullable=False, default=0),
        sa.Column('output_tokens', sa.Integer(), nullable=False, default=0),
        sa.Column('total_tokens', sa.Integer(), nullable=False, default=0),
        sa.Column('cost_usd', sa.Float(), nullable=True),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('lead_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('success', sa.String(length=20), nullable=False, default='success'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for efficient querying
    op.create_index('idx_ai_usage_logs_tenant_id', 'ai_usage_logs', ['tenant_id'], unique=False)
    op.create_index('idx_ai_usage_logs_operation', 'ai_usage_logs', ['operation'], unique=False)
    op.create_index('idx_ai_usage_logs_created_at', 'ai_usage_logs', ['created_at'], unique=False)
    op.create_index('idx_ai_usage_logs_tenant_created', 'ai_usage_logs', ['tenant_id', 'created_at'], unique=False)


def downgrade() -> None:
    """Remove AI usage log table"""

    # Drop indexes
    op.drop_index('idx_ai_usage_logs_tenant_created', table_name='ai_usage_logs')
    op.drop_index('idx_ai_usage_logs_created_at', table_name='ai_usage_logs')
    op.drop_index('idx_ai_usage_logs_operation', table_name='ai_usage_logs')
    op.drop_index('idx_ai_usage_logs_tenant_id', table_name='ai_usage_logs')

    # Drop table
    op.drop_table('ai_usage_logs')
