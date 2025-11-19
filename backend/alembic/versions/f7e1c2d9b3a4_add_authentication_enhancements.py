"""Add authentication enhancements (password reset and login rate limiting)

Revision ID: f7e1c2d9b3a4
Revises: f5a2c3d8e9b1
Create Date: 2025-11-12 14:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f7e1c2d9b3a4"
down_revision: Union[str, None] = "f5a2c3d8e9b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add authentication enhancement columns to users table"""

    # Add password reset fields
    op.add_column(
        "users", sa.Column("password_reset_token", sa.String(255), nullable=True)
    )
    op.add_column(
        "users",
        sa.Column(
            "password_reset_expires_at", sa.DateTime(timezone=True), nullable=True
        ),
    )

    # Add login attempt tracking fields
    op.add_column(
        "users",
        sa.Column(
            "failed_login_attempts", sa.Integer(), nullable=False, server_default="0"
        ),
    )
    op.add_column(
        "users", sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True)
    )

    # Create index for password reset token lookup
    op.create_index("idx_users_password_reset_token", "users", ["password_reset_token"])


def downgrade() -> None:
    """Remove authentication enhancement columns from users table"""

    # Drop index
    op.drop_index("idx_users_password_reset_token", table_name="users")

    # Remove columns
    op.drop_column("users", "locked_until")
    op.drop_column("users", "failed_login_attempts")
    op.drop_column("users", "password_reset_expires_at")
    op.drop_column("users", "password_reset_token")
