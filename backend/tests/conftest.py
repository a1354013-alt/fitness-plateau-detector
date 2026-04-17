from __future__ import annotations

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator

import pytest
from sqlmodel import Session, SQLModel, create_engine

backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Ensure app-level smoke tests (importing app.main) never write to the repo tree.
_pytest_tmp_db_dir = TemporaryDirectory(prefix="plateaubreaker_pytest_")
os.environ.setdefault(
    "PLATEAUBREAKER_DB_PATH",
    str((Path(_pytest_tmp_db_dir.name) / "plateaubreaker_pytest.sqlite3").resolve()),
)


@pytest.fixture()
def session() -> Generator[Session, None, None]:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s
