from alembic import op
import sqlalchemy as sa

revision = "0003_create_metrics_table"
down_revision = "0002_add_timestamps"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "metrics",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("value", sa.String(255), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.String(36)),
        sa.Column("meta", sa.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), 
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), 
                  server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("metrics")
