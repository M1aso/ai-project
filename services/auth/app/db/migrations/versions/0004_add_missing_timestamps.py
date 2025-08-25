from alembic import op
import sqlalchemy as sa

revision = "0004_add_missing_timestamps"
down_revision = "0003_add_updated_at_to_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add updated_at to tables that don't have it
    op.add_column("email_verifications", sa.Column(
        "updated_at", sa.DateTime(timezone=True), 
        server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
    ))
    op.add_column("password_resets", sa.Column(
        "updated_at", sa.DateTime(timezone=True), 
        server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
    ))
    op.add_column("refresh_tokens", sa.Column(
        "updated_at", sa.DateTime(timezone=True), 
        server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False
    ))


def downgrade() -> None:
    op.drop_column("refresh_tokens", "updated_at")
    op.drop_column("password_resets", "updated_at")
    op.drop_column("email_verifications", "updated_at")
