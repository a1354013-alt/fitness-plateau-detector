from __future__ import annotations

from datetime import date, timedelta

from app.models.health_record import HealthRecord
from app.rules.plateau_detector import detect_plateau


def _make_records(start: date, days: int, *, weight: float) -> list[HealthRecord]:
    records: list[HealthRecord] = []
    for i in range(days):
        d = start + timedelta(days=i)
        records.append(
            HealthRecord(
                record_date=d,
                weight=weight,
                sleep_hours=7.0,
                calories=2000,
                protein=120,
                exercise_minutes=30,
                exercise_type="Walking",
                steps=8000,
                note=None,
            )
        )
    return records


def test_plateau_detects_plateau_with_stable_weight():
    start = date(2026, 3, 1)
    records = _make_records(start, 14, weight=75.0)
    result = detect_plateau(records)

    assert result.status == "plateau"
    assert result.rule_b is True
    assert result.rule_a is True


def test_plateau_insufficient_with_too_few_recent_days():
    start = date(2026, 3, 1)
    records = _make_records(start, 4, weight=75.0)
    result = detect_plateau(records)

    assert result.status == "insufficient_data"
    assert result.rule_a is None
    assert result.rule_b is None
