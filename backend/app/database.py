from __future__ import annotations

import os
from pathlib import Path
from typing import Generator

from sqlmodel import SQLModel, Session, create_engine


def _resolve_db_url() -> str:
    """
    Stable SQLite path resolution (independent of process working directory).

    Env override:
    - PLATEAUBREAKER_DB_PATH: absolute path, or path relative to backend root

    Default:
    - backend/data/plateaubreaker.sqlite3
    """

    backend_dir = Path(__file__).resolve().parents[1]
    configured = os.getenv("PLATEAUBREAKER_DB_PATH")

    if configured and configured.strip():
        db_path = Path(configured.strip())
        if not db_path.is_absolute():
            db_path = backend_dir / db_path
    else:
        db_path = backend_dir / "data" / "plateaubreaker.sqlite3"

    db_path = db_path.resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    return f"sqlite:///{db_path.as_posix()}"


DATABASE_URL = _resolve_db_url()

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
