"""fix_profile_history_id_type

Revision ID: 0003_fix_profile_history_id_type
Revises: 0002_add_timestamps
Create Date: 2025-08-26 18:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0003_fix_profile_history_id_type'
down_revision = '0002_add_timestamps'
branch_labels = None
depends_on = None


def upgrade():
    # Change profile_history.id from bigint to integer
    # This requires recreating the table due to PostgreSQL limitations with primary key changes
    op.execute('ALTER TABLE profile_history DROP CONSTRAINT profile_history_pkey CASCADE')
    op.execute('ALTER TABLE profile_history ALTER COLUMN id TYPE INTEGER USING id::integer')
    op.execute('ALTER TABLE profile_history ADD PRIMARY KEY (id)')


def downgrade():
    # Revert back to bigint
    op.execute('ALTER TABLE profile_history DROP CONSTRAINT profile_history_pkey CASCADE')
    op.execute('ALTER TABLE profile_history ALTER COLUMN id TYPE BIGINT USING id::bigint')
    op.execute('ALTER TABLE profile_history ADD PRIMARY KEY (id)')
