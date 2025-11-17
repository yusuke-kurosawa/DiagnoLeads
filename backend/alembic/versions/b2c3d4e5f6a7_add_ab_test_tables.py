"""Add A/B test tables

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-11-17 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create A/B test and variant tables"""

    # Create A/B test status enum
    ab_test_status_enum = postgresql.ENUM(
        'draft', 'running', 'paused', 'completed', 'archived',
        name='abteststatus',
        create_type=True
    )
    ab_test_status_enum.create(op.get_bind(), checkfirst=True)

    # Create A/B test type enum
    ab_test_type_enum = postgresql.ENUM(
        'question_order', 'cta_text', 'cta_color', 'intro_text', 'custom',
        name='abtesttype',
        create_type=True
    )
    ab_test_type_enum.create(op.get_bind(), checkfirst=True)

    # Create ab_tests table
    op.create_table(
        'ab_tests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('test_type', ab_test_type_enum, nullable=False, server_default='custom'),
        sa.Column('traffic_allocation', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('min_sample_size', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('confidence_threshold', sa.Float(), nullable=False, server_default='0.95'),
        sa.Column('exploration_rate', sa.Float(), nullable=False, server_default='0.1'),
        sa.Column('status', ab_test_status_enum, nullable=False, server_default='draft', index=True),
        sa.Column('total_impressions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_conversions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('overall_conversion_rate', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('winner_variant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes for ab_tests
    op.create_index('idx_ab_tests_tenant_id', 'ab_tests', ['tenant_id'])
    op.create_index('idx_ab_tests_assessment_id', 'ab_tests', ['assessment_id'])
    op.create_index('idx_ab_tests_status', 'ab_tests', ['status'])
    op.create_index('idx_ab_tests_created_at', 'ab_tests', ['created_at'])

    # Create ab_test_variants table
    op.create_table(
        'ab_test_variants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('ab_test_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_control', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('config', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('impressions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('conversions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('conversion_rate', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('alpha', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('beta', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('thompson_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('current_traffic_allocation', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('confidence_interval_lower', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('confidence_interval_upper', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['ab_test_id'], ['ab_tests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )

    # Create indexes for ab_test_variants
    op.create_index('idx_ab_test_variants_ab_test_id', 'ab_test_variants', ['ab_test_id'])
    op.create_index('idx_ab_test_variants_tenant_id', 'ab_test_variants', ['tenant_id'])


def downgrade() -> None:
    """Drop A/B test and variant tables"""

    # Drop indexes
    op.drop_index('idx_ab_test_variants_tenant_id', table_name='ab_test_variants')
    op.drop_index('idx_ab_test_variants_ab_test_id', table_name='ab_test_variants')

    op.drop_index('idx_ab_tests_created_at', table_name='ab_tests')
    op.drop_index('idx_ab_tests_status', table_name='ab_tests')
    op.drop_index('idx_ab_tests_assessment_id', table_name='ab_tests')
    op.drop_index('idx_ab_tests_tenant_id', table_name='ab_tests')

    # Drop tables
    op.drop_table('ab_test_variants')
    op.drop_table('ab_tests')

    # Drop enums
    ab_test_type_enum = postgresql.ENUM(
        'question_order', 'cta_text', 'cta_color', 'intro_text', 'custom',
        name='abtesttype'
    )
    ab_test_type_enum.drop(op.get_bind(), checkfirst=True)

    ab_test_status_enum = postgresql.ENUM(
        'draft', 'running', 'paused', 'completed', 'archived',
        name='abteststatus'
    )
    ab_test_status_enum.drop(op.get_bind(), checkfirst=True)
