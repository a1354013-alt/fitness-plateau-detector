from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

from app.migrations import upgrade_to_head


def _sqlite_url(path: Path) -> str:
    return f"sqlite:///{path.as_posix()}"


def test_health_records_db_check_constraints_enforced():
    with TemporaryDirectory(prefix="plateaubreaker_checks_") as tmpdir:
        db_path = Path(tmpdir) / "checks.sqlite3"
        upgrade_to_head(sqlalchemy_url=_sqlite_url(db_path))

        engine = create_engine(_sqlite_url(db_path), future=True)
        try:

            def insert_row(*, record_date: str, **overrides: object) -> None:
                now = datetime.now(timezone.utc)
                base = {
                    "record_date": record_date,
                    "weight": 75.0,
                    "sleep_hours": 7.0,
                    "calories": 2000,
                    "protein": 120,
                    "exercise_minutes": 30,
                    "exercise_type": "Walking",
                    "steps": 8000,
                    "note": "ok",
                    "created_at": now,
                    "updated_at": now,
                }
                base.update(overrides)

                cols = ", ".join(base.keys())
                params = ", ".join(f":{k}" for k in base.keys())
                stmt = text(f"INSERT INTO health_records ({cols}) VALUES ({params})")
                with engine.begin() as conn:
                    conn.execute(stmt, base)

            # Sanity: constraints are present in the DDL
            with engine.connect() as conn:
                ddl = conn.execute(
                    text("SELECT sql FROM sqlite_master WHERE type='table' AND name='health_records'"),
                ).scalar_one()
            assert "ck_health_records_weight_range" in ddl
            assert "ck_health_records_sleep_hours_range" in ddl
            assert "ck_health_records_calories_range" in ddl
            assert "ck_health_records_protein_range" in ddl
            assert "ck_health_records_exercise_minutes_range" in ddl
            assert "ck_health_records_steps_range" in ddl

            # Weight
            with pytest.raises(IntegrityError):
                insert_row(record_date="2026-04-01", weight=0)

            # Sleep hours
            with pytest.raises(IntegrityError):
                insert_row(record_date="2026-04-02", sleep_hours=25)

            # Calories
            with pytest.raises(IntegrityError):
                insert_row(record_date="2026-04-03", calories=20001)

            # Protein (optional)
            insert_row(record_date="2026-04-04", protein=None)
            with pytest.raises(IntegrityError):
                insert_row(record_date="2026-04-05", protein=-1)

            # Exercise minutes
            with pytest.raises(IntegrityError):
                insert_row(record_date="2026-04-06", exercise_minutes=1441)

            # Steps (optional)
            insert_row(record_date="2026-04-07", steps=None)
            with pytest.raises(IntegrityError):
                insert_row(record_date="2026-04-08", steps=200001)
        finally:
            engine.dispose()
