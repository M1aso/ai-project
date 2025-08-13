from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "experience_levels",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("label", sa.String(length=50), nullable=False),
        sa.Column("sequence", sa.Integer, nullable=False),
    )
    op.create_table(
        "profiles",
        sa.Column("user_id", sa.String(length=36), primary_key=True),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("nickname", sa.String(length=50)),
        sa.Column("birth_date", sa.Date()),
        sa.Column("gender", sa.String(length=10)),
        sa.Column("country", sa.String(length=100)),
        sa.Column("city", sa.String(length=100)),
        sa.Column("company", sa.String(length=150)),
        sa.Column("position", sa.String(length=150)),
        sa.Column("experience_id", sa.Integer, sa.ForeignKey("experience_levels.id")),
        sa.Column("avatar_url", sa.String(length=255)),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "gender IN ('male','female','other')", name="ck_profiles_gender"
        ),
    )
    op.create_table(
        "social_bindings",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("profiles.user_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("provider", sa.String(length=20), nullable=False),
        sa.Column("provider_id", sa.String(length=255)),
        sa.Column(
            "linked_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "provider IN ('telegram','vkontakte','whatsapp')",
            name="ck_social_bindings_provider",
        ),
    )
    op.create_table(
        "profile_history",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.String(length=36),
            sa.ForeignKey("profiles.user_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("field", sa.String(length=50), nullable=False),
        sa.Column("old_value", sa.Text()),
        sa.Column("new_value", sa.Text()),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("changed_by", sa.String(length=36)),
    )


def downgrade() -> None:
    op.drop_table("profile_history")
    op.drop_table("social_bindings")
    op.drop_table("profiles")
    op.drop_table("experience_levels")
