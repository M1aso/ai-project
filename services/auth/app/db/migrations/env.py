import sys
from pathlib import Path

# Add the appropriate path to Python path for imports
# Handle both container deployment and local testing
current_file = Path(__file__).resolve()
if "services" in str(current_file):
    # Running in local development or CI from project root
    sys.path.append(str(current_file.parents[5]))
    from services.auth.app.db import models  # noqa: F401
else:
    # Running in container deployment
    sys.path.append(str(current_file.parents[3]))
    from app.db import models  # noqa: F401

from logging.config import fileConfig
import os

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config

if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name)
    except KeyError:
        pass

if not config.get_main_option("sqlalchemy.url"):
    config.set_main_option(
        "sqlalchemy.url", os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/aiproject")
    )

target_metadata = models.Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
