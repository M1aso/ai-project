from alembic import op
import sqlalchemy as sa

revision = "0002_add_timestamps"
down_revision = "0001_create_events_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add created_at and updated_at columns to events table
    op.add_column("events", sa.Column(
        "created_at", sa.DateTime(timezone=True), 
        server_default=sa.func.now(), nullable=False
    ))
    op.add_column("events", sa.Column(
        "updated_at", sa.DateTime(timezone=True), 
        server_default=sa.func.now(), nullable=False
    ))


def downgrade() -> None:
    op.drop_column("events", "updated_at")
    op.drop_column("events", "created_at")
