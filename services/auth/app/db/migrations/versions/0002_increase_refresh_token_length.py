"""increase refresh token length

Revision ID: 0002_increase_refresh_token_length
Revises: 0001_initial
Create Date: 2025-08-25 09:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002_increase_refresh_token_length'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade():
    """Increase refresh token column length to accommodate JWT tokens."""
    # Increase token column from VARCHAR(64) to VARCHAR(512) to accommodate JWT tokens
    op.alter_column('refresh_tokens', 'token',
                   existing_type=sa.VARCHAR(length=64),
                   type_=sa.VARCHAR(length=512),
                   existing_nullable=False)


def downgrade():
    """Revert refresh token column length back to 64 characters."""
    # Note: This may cause data loss if there are tokens longer than 64 characters
    op.alter_column('refresh_tokens', 'token',
                   existing_type=sa.VARCHAR(length=512),
                   type_=sa.VARCHAR(length=64),
                   existing_nullable=False)
