"""Add timestamps to auth tables

Revision ID: 0002_add_timestamps
Revises: 0001_initial
Create Date: 2025-08-26 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_add_timestamps'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add updated_at column to users table and other timestamp improvements."""
    # Add updated_at to users table if it doesn't exist
    try:
        op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), 
                                        server_default=sa.func.now(), nullable=False))
    except Exception:
        # Column might already exist in some environments
        pass


def downgrade() -> None:
    """Remove updated_at column from users table."""
    try:
        op.drop_column('users', 'updated_at')
    except Exception:
        # Column might not exist in some environments
        pass