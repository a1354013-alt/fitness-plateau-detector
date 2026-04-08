"""app.rules.plateau_detector

Plateau detection is evaluated over a 7-day calendar window.

Rule A (trend change):
- Compare average weight of the last 7-day window vs the previous 7-day window.
- Plateau condition: abs(avg_change) < 0.2 kg.

Rule B (fluctuation band):
- Within the last 7-day window, weight stays within ±0.3 kg.
- Plateau condition: (max - min) <= 0.6 kg.

Minimum data requirement:
- At least 5 recorded days within the last 7-day window.

Notes:
- The caller may optionally provide an explicit anchor_date (e.g. "today") to
  make the time window user-meaningful. If omitted, the latest record date is
  used as the anchor.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Literal

from app.models.health_record import HealthRecord
from app.rules.constants import WINDOW_DAYS, MIN_RECENT_DAYS
from app.schemas.analytics import PlateauResponse


PlateauStatus = Literal["losing", "plateau", "gaining", "insufficient_data"]

AVG_CHANGE_PLATEAU_THRESHOLD_KG = 0.2
FLUCTUATION_PLATEAU_BAND_KG = 0.3  # ±0.3 kg


def detect_plateau(records: list[HealthRecord], *, anchor_date: date | None = None) -> PlateauResponse:
    """Return plateau status + diagnostic metrics.

    - records must be sorted by record_date ascending.
    - anchor_date defaults to the latest record_date.
    """

    if not records:
        return PlateauResponse(
            status="insufficient_data",
            message="No data available for plateau detection.",
            rule_a=None,
            rule_b=None,
            last7_avg=None,
            prev7_avg=None,
            avg_change=None,
            last7_fluctuation=None,
            last7_min=None,
            last7_max=None,
            data_completeness=0.0,
        )

    anchor = anchor_date or records[-1].record_date

    last_start = anchor - timedelta(days=WINDOW_DAYS - 1)
    prev_start = anchor - timedelta(days=(WINDOW_DAYS * 2) - 1)
    prev_end = anchor - timedelta(days=WINDOW_DAYS)

    last7 = [r for r in records if last_start <= r.record_date <= anchor]
    prev7 = [r for r in records if prev_start <= r.record_date <= prev_end]

    data_completeness = len(last7) / float(WINDOW_DAYS)
    if len(last7) < MIN_RECENT_DAYS:
        return PlateauResponse(
            status="insufficient_data",
            message=(
                f"Need at least {MIN_RECENT_DAYS} days of records in the last {WINDOW_DAYS} days "
                "for plateau detection."
            ),
            rule_a=None,
            rule_b=None,
            last7_avg=None,
            prev7_avg=None,
            avg_change=None,
            last7_fluctuation=None,
            last7_min=None,
            last7_max=None,
            data_completeness=data_completeness,
        )

    last_weights = [r.weight for r in last7]
    last_avg = sum(last_weights) / len(last_weights)
    last_min = min(last_weights)
    last_max = max(last_weights)
    last_fluctuation = last_max - last_min

    rule_b = last_fluctuation <= (FLUCTUATION_PLATEAU_BAND_KG * 2)

    # Rule A: compare to previous 7-day window when enough history exists.
    rule_a = None
    prev_avg = None
    avg_change = None
    if len(prev7) >= MIN_RECENT_DAYS:
        prev_weights = [r.weight for r in prev7]
        prev_avg = sum(prev_weights) / len(prev_weights)
        avg_change = last_avg - prev_avg
        rule_a = abs(avg_change) < AVG_CHANGE_PLATEAU_THRESHOLD_KG

    # Status decision
    status: PlateauStatus
    if rule_a is not None and avg_change is not None:
        if rule_a and rule_b:
            status = "plateau"
        elif avg_change <= -AVG_CHANGE_PLATEAU_THRESHOLD_KG:
            status = "losing"
        elif avg_change >= AVG_CHANGE_PLATEAU_THRESHOLD_KG:
            status = "gaining"
        else:
            # Borderline trend change: prefer fluctuation rule as the tie-breaker.
            if rule_b:
                status = "plateau"
            else:
                status = "losing" if avg_change < 0 else "gaining"
    else:
        # Not enough history for Rule A: rely on Rule B + direction within the window.
        if rule_b:
            status = "plateau"
        else:
            direction = last_weights[-1] - last_weights[0]
            status = "losing" if direction < 0 else "gaining"

    message = None
    if data_completeness < 1.0 and status != "insufficient_data":
        message = (
            f"Analysis based on {len(last7)}/{WINDOW_DAYS} days of data. "
            "Confidence reduced due to missing days."
        )

    return PlateauResponse(
        status=status,
        rule_a=rule_a,
        rule_b=rule_b,
        last7_avg=round(last_avg, 2),
        prev7_avg=round(prev_avg, 2) if prev_avg is not None else None,
        avg_change=round(avg_change, 2) if avg_change is not None else None,
        last7_fluctuation=round(last_fluctuation, 2),
        last7_min=round(last_min, 2),
        last7_max=round(last_max, 2),
        data_completeness=data_completeness,
        message=message,
    )
