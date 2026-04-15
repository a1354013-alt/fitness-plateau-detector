"""app.rules.reason_analyzer

Reason analysis is evaluated over the last 7 calendar days.

Minimum data requirement:
- At least 5 recorded days within the last 7-day window.

Reason codes:
- SleepIssue
- CalorieIssue
- WeekendOvereating
- ExerciseDrop
- DataMissing

Notes:
- The caller may provide an explicit anchor_date (e.g. "today"). If omitted,
  the latest record date is used.
"""

from __future__ import annotations

from datetime import date, timedelta

from app.models.health_record import HealthRecord
from app.rules.constants import MIN_RECENT_DAYS, WINDOW_DAYS
from app.schemas.analytics import ReasonItem, ReasonsResponse

# Severity weights for each reason type (normalized to 0-1 scale)
SEVERITY_WEIGHTS: dict[str, float] = {
    "SleepIssue": 1.0,
    "CalorieIssue": 1.0,
    "WeekendOvereating": 0.8,
    "ExerciseDrop": 0.8,
    "DataMissing": 1.2,  # Prioritize missing data: it affects confidence
}

SLEEP_THRESHOLD_HOURS = 6.0
WEEKEND_OVEREATING_RATIO = 1.20
EXERCISE_DROP_RATIO = 0.70
MAX_MISSING_DAYS = 2


def analyze_reasons(
    records: list[HealthRecord],
    calorie_target: int,
    *,
    anchor_date: date | None = None,
) -> ReasonsResponse:
    """Return ranked reasons for plateau.

    - records must be sorted by record_date ascending.
    - anchor_date defaults to the latest record_date.
    """

    if not records:
        return ReasonsResponse(
            status="insufficient_data",
            message="No data available for reason analysis.",
            reasons=[],
            all_reasons=[],
            data_points=0,
            missing_days=WINDOW_DAYS,
        )

    anchor = anchor_date or records[-1].record_date

    last_start = anchor - timedelta(days=WINDOW_DAYS - 1)
    prev_start = anchor - timedelta(days=(WINDOW_DAYS * 2) - 1)
    prev_end = anchor - timedelta(days=WINDOW_DAYS)

    last7 = [r for r in records if last_start <= r.record_date <= anchor]
    prev7 = [r for r in records if prev_start <= r.record_date <= prev_end]

    expected_dates = {last_start + timedelta(days=i) for i in range(WINDOW_DAYS)}
    actual_dates = {r.record_date for r in last7}
    missing_count = len(expected_dates - actual_dates)

    if len(last7) < MIN_RECENT_DAYS:
        return ReasonsResponse(
            status="insufficient_data",
            message=(
                f"Need at least {MIN_RECENT_DAYS} days of records in the last {WINDOW_DAYS} days for reason analysis."
            ),
            reasons=[],
            all_reasons=[],
            data_points=len(last7),
            missing_days=missing_count,
        )

    reasons: list[ReasonItem] = []

    # Rule 1: Sleep Issue
    avg_sleep = sum(r.sleep_hours for r in last7) / len(last7)
    if avg_sleep < SLEEP_THRESHOLD_HOURS:
        reasons.append(
            ReasonItem(
                code="SleepIssue",
                label="Insufficient Sleep",
                description=(
                    f"Average sleep last {WINDOW_DAYS} days: {avg_sleep:.1f}h "
                    f"(threshold: {SLEEP_THRESHOLD_HOURS}h)"
                ),
                severity=round(
                    ((SLEEP_THRESHOLD_HOURS - avg_sleep) / SLEEP_THRESHOLD_HOURS)
                    * SEVERITY_WEIGHTS["SleepIssue"],
                    3,
                ),
                value=float(round(avg_sleep, 2)),
                threshold=float(SLEEP_THRESHOLD_HOURS),
                details={"avg_sleep": round(avg_sleep, 1), "threshold": SLEEP_THRESHOLD_HOURS},
            )
        )

    # Rule 2: Calorie Issue
    avg_calories = sum(r.calories for r in last7) / len(last7)
    if avg_calories > calorie_target:
        excess_ratio = (avg_calories - calorie_target) / float(calorie_target)
        reasons.append(
            ReasonItem(
                code="CalorieIssue",
                label="High Calorie Intake",
                description=(
                    f"Average calories last {WINDOW_DAYS} days: {avg_calories:.0f} kcal "
                    f"(target: {calorie_target} kcal)"
                ),
                severity=round(excess_ratio * SEVERITY_WEIGHTS["CalorieIssue"], 3),
                value=float(round(avg_calories, 1)),
                threshold=float(calorie_target),
                details={
                    "avg_calories": round(avg_calories, 0),
                    "target": calorie_target,
                    "over_target_percent": round(excess_ratio * 100, 0),
                },
            )
        )

    # Rule 3: Weekend Overeating
    weekend_records = [r for r in last7 if r.record_date.weekday() >= 5]
    weekday_records = [r for r in last7 if r.record_date.weekday() < 5]
    if weekend_records and weekday_records:
        weekend_avg = sum(r.calories for r in weekend_records) / len(weekend_records)
        weekday_avg = sum(r.calories for r in weekday_records) / len(weekday_records)
        if weekday_avg > 0 and weekend_avg > weekday_avg * WEEKEND_OVEREATING_RATIO:
            ratio = weekend_avg / weekday_avg
            reasons.append(
                ReasonItem(
                    code="WeekendOvereating",
                    label="Weekend Overeating",
                    description=(
                        f"Weekend avg: {weekend_avg:.0f} kcal, {((ratio - 1) * 100):.0f}% higher "
                        f"than weekday avg: {weekday_avg:.0f} kcal"
                    ),
                    severity=round((ratio - 1.0) * SEVERITY_WEIGHTS["WeekendOvereating"], 3),
                    value=float(round(weekend_avg, 1)),
                    threshold=float(round(weekday_avg * WEEKEND_OVEREATING_RATIO, 1)),
                    details={
                        "weekend_avg": round(weekend_avg, 0),
                        "weekday_avg": round(weekday_avg, 0),
                        "higher_percent": round((ratio - 1) * 100, 0),
                    },
                )
            )

    # Rule 4: Exercise Drop (requires previous window)
    if prev7 and len(prev7) >= MIN_RECENT_DAYS:
        last_exercise = sum(r.exercise_minutes for r in last7) / len(last7)
        prev_exercise = sum(r.exercise_minutes for r in prev7) / len(prev7)
        if prev_exercise > 0 and last_exercise < prev_exercise * EXERCISE_DROP_RATIO:
            drop_ratio = 1.0 - (last_exercise / prev_exercise)
            reasons.append(
                ReasonItem(
                    code="ExerciseDrop",
                    label="Exercise Reduction",
                    description=(
                        f"Recent exercise: {last_exercise:.0f} min/day vs Previous: {prev_exercise:.0f} min/day"
                    ),
                    severity=round(drop_ratio * SEVERITY_WEIGHTS["ExerciseDrop"], 3),
                    value=float(round(last_exercise, 1)),
                    threshold=float(round(prev_exercise * EXERCISE_DROP_RATIO, 1)),
                    details={
                        "last7_exercise": round(last_exercise, 0),
                        "prev7_exercise": round(prev_exercise, 0),
                        "drop_percent": round(drop_ratio * 100, 0),
                    },
                )
            )

    # Rule 5: Data Missing
    if missing_count > MAX_MISSING_DAYS:
        reasons.append(
            ReasonItem(
                code="DataMissing",
                label="Incomplete Data",
                description=f"Missing {missing_count} days of records in the last {WINDOW_DAYS} days",
                severity=round((missing_count / float(WINDOW_DAYS)) * SEVERITY_WEIGHTS["DataMissing"], 3),
                value=float(missing_count),
                threshold=float(MAX_MISSING_DAYS),
                details={"missing_days": missing_count},
            )
        )

    reasons.sort(key=lambda x: x.severity, reverse=True)
    top2 = reasons[:2]

    message = None

    if missing_count > 0:
        message = (
            f"Analysis based on {len(last7)}/{WINDOW_DAYS} days of data. "
            f"Confidence reduced due to {missing_count} missing day(s)."
        )

    return ReasonsResponse(
        status="ok",
        reasons=top2,
        all_reasons=reasons,
        data_points=len(last7),
        missing_days=missing_count,
        message=message,
    )
