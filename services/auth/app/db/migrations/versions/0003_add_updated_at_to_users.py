"""Add updated_at field to users table

Revision ID: 0003
Revises: 0002_increase_refresh_token_length
Create Date: 2025-08-25 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone

# revision identifiers, used by Alembic.
revision = '0003'
down_revision = '0002_increase_refresh_token_length'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add updated_at column to users table
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    
    # Set initial value for existing records
    op.execute("UPDATE users SET updated_at = created_at WHERE updated_at IS NULL")
    
    # Make the column not nullable after setting values
    op.alter_column('users', 'updated_at', nullable=False)


def downgrade() -> None:
    # Remove updated_at column
    op.drop_column('users', 'updated_at')
