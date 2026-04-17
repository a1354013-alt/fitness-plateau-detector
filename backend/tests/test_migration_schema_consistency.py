from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import sqlalchemy as sa
from sqlalchemy import create_engine

from app.migrations import upgrade_to_head
from app.models.health_record import HealthRecord


def _sqlite_url(path: Path) -> str:
    return f"sqlite:///{path.as_posix()}"


def test_alembic_upgraded_schema_matches_sqlmodel_contract():
    """Guard against schema drift between Alembic migrations and SQLModel/Pydantic contracts."""

    with TemporaryDirectory(prefix="plateaubreaker_schema_") as tmpdir:
        db_path = Path(tmpdir) / "schema.sqlite3"
        upgrade_to_head(sqlalchemy_url=_sqlite_url(db_path))

        engine = create_engine(_sqlite_url(db_path), future=True)
        try:
            inspector = sa.inspect(engine)

            assert "health_records" in inspector.get_table_names()

            cols = {c["name"]: c for c in inspector.get_columns("health_records")}

            def col(name: str) -> dict:
                assert name in cols, f"Missing column: {name}"
                return cols[name]

            # Types / nullability
            assert isinstance(col("id")["type"], sa.Integer)
            assert col("id")["nullable"] is False

            assert isinstance(col("record_date")["type"], sa.Date)
            assert col("record_date")["nullable"] is False

            assert isinstance(col("weight")["type"], sa.Float)
            assert col("weight")["nullable"] is False

            assert isinstance(col("sleep_hours")["type"], sa.Float)
            assert col("sleep_hours")["nullable"] is False

            assert isinstance(col("calories")["type"], sa.Integer)
            assert col("calories")["nullable"] is False

            assert isinstance(col("protein")["type"], sa.Integer)
            assert col("protein")["nullable"] is True

            assert isinstance(col("exercise_minutes")["type"], sa.Integer)
            assert col("exercise_minutes")["nullable"] is False

            assert isinstance(col("exercise_type")["type"], sa.String)
            assert col("exercise_type")["type"].length == 50
            assert col("exercise_type")["nullable"] is True

            assert isinstance(col("steps")["type"], sa.Integer)
            assert col("steps")["nullable"] is True

            assert isinstance(col("note")["type"], sa.String)
            assert col("note")["type"].length == 500
            assert col("note")["nullable"] is True

            assert isinstance(col("created_at")["type"], sa.DateTime)
            assert col("created_at")["nullable"] is False

            assert isinstance(col("updated_at")["type"], sa.DateTime)
            assert col("updated_at")["nullable"] is False

            # Uniqueness / indexes
            uniques = inspector.get_unique_constraints("health_records")
            unique_cols = {tuple(u["column_names"]) for u in uniques}
            assert ("record_date",) in unique_cols

            indexes = inspector.get_indexes("health_records")
            index_cols = {tuple(i["column_names"]) for i in indexes}
            assert ("record_date",) in index_cols

            # CHECK constraints should exist after migrations (defense-in-depth).
            with engine.connect() as conn:
                ddl = conn.execute(
                    sa.text("SELECT sql FROM sqlite_master WHERE type='table' AND name='health_records'"),
                ).scalar_one()
            for name in (
                "ck_health_records_weight_range",
                "ck_health_records_sleep_hours_range",
                "ck_health_records_calories_range",
                "ck_health_records_protein_range",
                "ck_health_records_exercise_minutes_range",
                "ck_health_records_steps_range",
            ):
                assert name in ddl

            # SQLModel contract: timestamps are declared as timezone-aware (even though SQLite stores as DATETIME).
            assert isinstance(HealthRecord.__table__.c.created_at.type, sa.DateTime)
            assert HealthRecord.__table__.c.created_at.type.timezone is True
            assert isinstance(HealthRecord.__table__.c.updated_at.type, sa.DateTime)
            assert HealthRecord.__table__.c.updated_at.type.timezone is True
        finally:
            engine.dispose()
