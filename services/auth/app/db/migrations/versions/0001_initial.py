from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("login_type", sa.String(length=10), nullable=False),
        sa.Column("phone", sa.String(length=15), unique=True),
        sa.Column("email", sa.String(length=255), unique=True),
        sa.Column("password_hash", sa.String(length=255)),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column("blocked_until", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    op.create_table(
        "email_verifications",
        sa.Column("token", sa.String(length=64), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_email_verifications_token", "email_verifications", ["token"], unique=True
    )

    op.create_table(
        "password_resets",
        sa.Column("token", sa.String(length=64), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_password_resets_token", "password_resets", ["token"], unique=True
    )

    op.create_table(
        "refresh_tokens",
        sa.Column("token", sa.String(length=64), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("family", sa.String(length=36), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_refresh_tokens_user_id_family", "refresh_tokens", ["user_id", "family"]
    )


def downgrade() -> None:
    op.drop_index("ix_refresh_tokens_user_id_family", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
    op.drop_index("ix_password_resets_token", table_name="password_resets")
    op.drop_table("password_resets")
    op.drop_index("ix_email_verifications_token", table_name="email_verifications")
    op.drop_table("email_verifications")
    op.drop_table("users")
