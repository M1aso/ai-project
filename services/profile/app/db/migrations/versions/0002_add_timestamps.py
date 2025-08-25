from alembic import op
import sqlalchemy as sa

revision = "0002_add_timestamps"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add created_at to profiles
    op.add_column("profiles", sa.Column(
        "created_at", sa.DateTime(timezone=True), 
        server_default=sa.func.now(), nullable=False
    ))
    
    # Add created_at and updated_at to experience_levels
    op.add_column("experience_levels", sa.Column(
        "created_at", sa.DateTime(timezone=True), 
        server_default=sa.func.now(), nullable=False
    ))
    op.add_column("experience_levels", sa.Column(
        "updated_at", sa.DateTime(timezone=True), 
        server_default=sa.func.now(), nullable=False
    ))
    
    # Add updated_at to social_bindings (rename linked_at to created_at)
    op.add_column("social_bindings", sa.Column(
        "updated_at", sa.DateTime(timezone=True), 
        server_default=sa.func.now(), nullable=False
    ))
    
    # Add created_at and updated_at to profile_history
    op.add_column("profile_history", sa.Column(
        "updated_at", sa.DateTime(timezone=True), 
        server_default=sa.func.now(), nullable=False
    ))


def downgrade() -> None:
    op.drop_column("profile_history", "updated_at")
    op.drop_column("social_bindings", "updated_at")
    op.drop_column("experience_levels", "updated_at")
    op.drop_column("experience_levels", "created_at")
    op.drop_column("profiles", "created_at")
