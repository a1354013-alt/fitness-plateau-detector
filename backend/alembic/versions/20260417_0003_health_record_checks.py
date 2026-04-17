"""Add DB-level CHECK constraints for health_records core fields.

Revision ID: 20260417_0003
Revises: 20260415_0002
Create Date: 2026-04-17
"""

from __future__ import annotations

from alembic import op

revision = "20260417_0003"
down_revision = "20260415_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # NOTE: SQLite cannot add/drop constraints in-place; batch mode recreates the table safely.
    with op.batch_alter_table("health_records", recreate="always") as batch:
        batch.create_check_constraint(
            "ck_health_records_weight_range",
            "weight > 0 AND weight <= 500",
        )
        batch.create_check_constraint(
            "ck_health_records_sleep_hours_range",
            "sleep_hours >= 0 AND sleep_hours <= 24",
        )
        batch.create_check_constraint(
            "ck_health_records_calories_range",
            "calories >= 0 AND calories <= 20000",
        )
        batch.create_check_constraint(
            "ck_health_records_protein_range",
            "(protein IS NULL) OR (protein >= 0 AND protein <= 500)",
        )
        batch.create_check_constraint(
            "ck_health_records_exercise_minutes_range",
            "exercise_minutes >= 0 AND exercise_minutes <= 1440",
        )
        batch.create_check_constraint(
            "ck_health_records_steps_range",
            "(steps IS NULL) OR (steps >= 0 AND steps <= 200000)",
        )


def downgrade() -> None:
    with op.batch_alter_table("health_records", recreate="always") as batch:
        batch.drop_constraint("ck_health_records_steps_range", type_="check")
        batch.drop_constraint("ck_health_records_exercise_minutes_range", type_="check")
        batch.drop_constraint("ck_health_records_protein_range", type_="check")
        batch.drop_constraint("ck_health_records_calories_range", type_="check")
        batch.drop_constraint("ck_health_records_sleep_hours_range", type_="check")
        batch.drop_constraint("ck_health_records_weight_range", type_="check")

