from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine.url import make_url
from sqlmodel import SQLModel

from alembic import context

# Ensure `app.*` imports work when running Alembic from the backend folder.
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.database import DATABASE_URL, ensure_db_dir_exists  # noqa: E402
from app.models.health_record import HealthRecord  # noqa: F401,E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Keep Alembic and the app on the same connection URL semantics.
configured_url = config.get_main_option("sqlalchemy.url") or ""
# Allow programmatic callers (tests/tools) to override the target DB URL by
# setting it on the Alembic Config before running commands.
if (not configured_url.strip()) or configured_url.strip() == "sqlite:///./data/plateaubreaker.sqlite3":
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    ensure_db_dir_exists()
else:
    # Ensure target SQLite directories exist when running against a custom URL.
    url = make_url(configured_url)
    if url.drivername.startswith("sqlite") and url.database:
        Path(url.database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
