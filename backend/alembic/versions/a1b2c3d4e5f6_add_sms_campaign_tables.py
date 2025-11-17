"""Add SMS campaign tables

Revision ID: a1b2c3d4e5f6
Revises: f7e1c2d9b3a4
Create Date: 2025-11-17 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'f7e1c2d9b3a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create SMS campaign and message tables"""

    # Create SMS status enum
    sms_status_enum = postgresql.ENUM(
        'pending', 'sent', 'delivered', 'failed', 'undelivered',
        name='smsstatus',
        create_type=True
    )
    sms_status_enum.create(op.get_bind(), checkfirst=True)

    # Create sms_campaigns table
    op.create_table(
        'sms_campaigns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('qr_code_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('message_template', sa.Text(), nullable=False),
        sa.Column('recipients', postgresql.JSONB(), nullable=False),
        sa.Column('total_recipients', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('sent_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('delivered_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sms_status_enum, nullable=False, server_default='pending', index=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['qr_code_id'], ['qr_codes.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes for sms_campaigns
    op.create_index('idx_sms_campaigns_tenant_id', 'sms_campaigns', ['tenant_id'])
    op.create_index('idx_sms_campaigns_status', 'sms_campaigns', ['status'])
    op.create_index('idx_sms_campaigns_created_at', 'sms_campaigns', ['created_at'])

    # Create sms_messages table
    op.create_table(
        'sms_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('phone_number', sa.String(20), nullable=False),
        sa.Column('message_text', sa.Text(), nullable=False),
        sa.Column('twilio_sid', sa.String(34), nullable=True),
        sa.Column('status', sms_status_enum, nullable=False, server_default='pending', index=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('clicked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('clicked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['campaign_id'], ['sms_campaigns.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    )

    # Create indexes for sms_messages
    op.create_index('idx_sms_messages_campaign_id', 'sms_messages', ['campaign_id'])
    op.create_index('idx_sms_messages_tenant_id', 'sms_messages', ['tenant_id'])
    op.create_index('idx_sms_messages_status', 'sms_messages', ['status'])
    op.create_index('idx_sms_messages_twilio_sid', 'sms_messages', ['twilio_sid'])


def downgrade() -> None:
    """Drop SMS campaign and message tables"""

    # Drop indexes
    op.drop_index('idx_sms_messages_twilio_sid', table_name='sms_messages')
    op.drop_index('idx_sms_messages_status', table_name='sms_messages')
    op.drop_index('idx_sms_messages_tenant_id', table_name='sms_messages')
    op.drop_index('idx_sms_messages_campaign_id', table_name='sms_messages')

    op.drop_index('idx_sms_campaigns_created_at', table_name='sms_campaigns')
    op.drop_index('idx_sms_campaigns_status', table_name='sms_campaigns')
    op.drop_index('idx_sms_campaigns_tenant_id', table_name='sms_campaigns')

    # Drop tables
    op.drop_table('sms_messages')
    op.drop_table('sms_campaigns')

    # Drop enum
    sms_status_enum = postgresql.ENUM(
        'pending', 'sent', 'delivered', 'failed', 'undelivered',
        name='smsstatus'
    )
    sms_status_enum.drop(op.get_bind(), checkfirst=True)
