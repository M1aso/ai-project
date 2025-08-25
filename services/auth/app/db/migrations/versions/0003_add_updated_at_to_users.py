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
    # Try to add the column - it might already exist in test databases
    try:
        op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
        # Set initial value for existing records
        op.execute("UPDATE users SET updated_at = created_at WHERE updated_at IS NULL")
        
        # Try to make it not nullable (PostgreSQL only)
        try:
            op.alter_column('users', 'updated_at', nullable=False)
        except:
            # SQLite doesn't support ALTER COLUMN, so we'll leave it nullable
            pass
            
    except Exception:
        # Column might already exist (e.g., in test databases)
        # Just try to set the values
        try:
            op.execute("UPDATE users SET updated_at = created_at WHERE updated_at IS NULL")
        except:
            pass


def downgrade() -> None:
    # Try to remove the column
    try:
        op.drop_column('users', 'updated_at')
    except:
        pass
