from __future__ import annotations

from datetime import date, timedelta

from app.models.health_record import HealthRecord
from app.rules.reason_analyzer import analyze_reasons


def test_reason_analyzer_flags_sleep_and_calories():
    start = date(2026, 3, 1)
    records: list[HealthRecord] = []

    # 7 recent days: low sleep + high calories should trigger SleepIssue + CalorieIssue
    for i in range(7):
        d = start + timedelta(days=i)
        records.append(
            HealthRecord(
                record_date=d,
                weight=75.0,
                sleep_hours=5.0,
                calories=2600,
                protein=120,
                exercise_minutes=30,
                exercise_type="Walking",
                steps=8000,
                note=None,
            )
        )

    result = analyze_reasons(records, calorie_target=2000)
    assert result["status"] in ("ok", "insufficient_data")

    codes = {r["code"] for r in result.get("all_reasons", [])}
    assert "SleepIssue" in codes
    assert "CalorieIssue" in codes

