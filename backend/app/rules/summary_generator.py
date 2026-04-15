"""app.rules.summary_generator

Generates human-readable summary + recommended actions from plateau detection and
reason analysis results.

Returned object shape (consumed by frontend):
- text: string
- insight: string (multi-line)
- status: plateau status string
- top_reasons: list of reason codes
"""

from __future__ import annotations

from app.schemas.analytics import PlateauResponse, ReasonItem, ReasonsResponse, SummaryPayload

STATUS_MESSAGES: dict[str, str] = {
    "plateau": "Your weight appears to be in a plateau based on recent trends.",
    "losing": "You're losing weight — keep up the good work.",
    "gaining": "Your weight is trending upward in recent days.",
    "insufficient_data": "Not enough recent data to analyze your trend yet.",
}


REASON_ACTIONS: dict[str, str] = {
    "SleepIssue": "Aim for 7–8 hours of sleep and keep sleep times consistent.",
    "CalorieIssue": "Reduce average calorie intake toward your target and track high-calorie items.",
    "WeekendOvereating": "Plan weekends: keep calories closer to weekday levels and watch portions.",
    "ExerciseDrop": "Restore activity levels (e.g. 30 minutes/day) to match your previous routine.",
    "DataMissing": "Log daily records consistently to improve analysis confidence.",
}


def _format_reason_line(idx: int, reason: ReasonItem) -> str:
    rank = "Main" if idx == 0 else "Secondary"
    label = reason.label or reason.code or "Unknown"
    details = reason.details or {}

    suffix = ""
    code = reason.code
    if code == "SleepIssue" and details.get("avg_sleep") is not None:
        suffix = f" (avg {details['avg_sleep']:.1f}h)"
    elif code == "CalorieIssue" and details.get("avg_calories") is not None:
        suffix = f" (avg {details['avg_calories']:.0f} kcal)"
    elif code == "WeekendOvereating" and details.get("higher_percent") is not None:
        suffix = f" ({details['higher_percent']:.0f}% higher on weekends)"
    elif code == "ExerciseDrop" and details.get("drop_percent") is not None:
        suffix = f" ({details['drop_percent']:.0f}% drop)"
    elif code == "DataMissing" and details.get("missing_days") is not None:
        suffix = f" ({details['missing_days']} missing days)"

    return f"{rank} factor: {label}{suffix}."


def generate_summary(plateau_result: PlateauResponse, reason_result: ReasonsResponse) -> SummaryPayload:
    status = plateau_result.status or "insufficient_data"
    reasons: list[ReasonItem] = list(reason_result.reasons or [])

    status_sentence = STATUS_MESSAGES.get(status, STATUS_MESSAGES["insufficient_data"])

    parts: list[str] = []

    # Data reliability / insufficient-data messages first
    if reason_result.status == "insufficient_data":
        parts.append(reason_result.message or "Not enough recent data to analyze reasons yet.")
    elif plateau_result.status == "insufficient_data":
        parts.append(plateau_result.message or "Not enough recent data to detect plateau yet.")
    elif any(r.code == "DataMissing" for r in reasons):
        parts.append("Some recent days are missing — results may be less reliable.")

    parts.append(status_sentence)

    # Add top reasons when analysis is reliable
    if status != "insufficient_data" and reason_result.status != "insufficient_data":
        for idx, reason in enumerate(reasons[:2]):
            parts.append(_format_reason_line(idx, reason))

    summary_text = " ".join(parts).strip()

    # Build detailed insight
    action_lines: list[str] = []
    for reason in reasons[:2]:
        code = reason.code
        action = REASON_ACTIONS.get(code)
        if action:
            action_lines.append(f"- {action}")

    if action_lines:
        insight_text = "Recommended actions:\n" + "\n".join(action_lines)
    else:
        if status == "losing":
            insight_text = "Recommended actions:\n- Keep doing what works and stay consistent."
        elif status == "insufficient_data":
            insight_text = "Recommended actions:\n- Log at least 5 days of records within the last 7 days to unlock analysis."
        else:
            insight_text = "Recommended actions:\n- Focus on consistency for the next week and review again."

    return SummaryPayload(
        text=summary_text,
        insight=insight_text,
        status=status,
        top_reasons=[r.code for r in reasons],
    )
