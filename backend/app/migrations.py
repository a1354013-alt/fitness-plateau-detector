from __future__ import annotations

from pathlib import Path

from alembic.config import Config

from alembic import command


def _backend_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def upgrade_to_head(*, sqlalchemy_url: str) -> None:
    """Apply Alembic migrations to `head` for the given DB URL.

    This is used for bootstrapping brand-new databases so that DB-level
    constraints (e.g. CHECK constraints) are present even when the app is the
    first process to touch the DB file.
    """

    backend_dir = _backend_dir()
    alembic_ini = backend_dir / "alembic.ini"
    if not alembic_ini.exists():
        raise RuntimeError(f"Missing Alembic config: {alembic_ini}")

    config = Config(str(alembic_ini))
    # Ensure script_location resolves correctly even when the app is started
    # from the repo root (e.g. `uvicorn ... --app-dir backend`).
    config.set_main_option("script_location", str((backend_dir / "alembic").resolve()))
    # Ensure we always run migrations against the app-resolved URL semantics.
    config.set_main_option("sqlalchemy.url", sqlalchemy_url)
    command.upgrade(config, "head")
