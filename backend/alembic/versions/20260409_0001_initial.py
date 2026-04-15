"""Initial schema (health_records).

Revision ID: 20260409_0001
Revises:
Create Date: 2026-04-09
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260409_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "health_records",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("record_date", sa.Date(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("sleep_hours", sa.Float(), nullable=False),
        sa.Column("calories", sa.Integer(), nullable=False),
        sa.Column("protein", sa.Integer(), nullable=True),
        sa.Column("exercise_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("exercise_type", sa.String(length=100), nullable=True),
        sa.Column("steps", sa.Integer(), nullable=True),
        sa.Column("note", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("record_date", name="uq_health_records_record_date"),
    )
    op.create_index("ix_health_records_record_date", "health_records", ["record_date"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_health_records_record_date", table_name="health_records")
    op.drop_table("health_records")

