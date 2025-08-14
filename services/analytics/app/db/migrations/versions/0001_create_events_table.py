from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("src", sa.String(100)),
        sa.Column("payload", sa.JSON, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("events")
