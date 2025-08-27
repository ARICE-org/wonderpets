from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import pkgutil
import importlib

# Import DB Base + URL
from app.db import Base, DATABASE_URL

# Import models package (so we can dynamically load submodules)
import app.models

# --- Alembic config ---
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set DB URL dynamically
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Now Alembic will detect all tables registered on Base.metadata
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
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
