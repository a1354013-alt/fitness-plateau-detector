from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from app.database import get_session
from app.services import health_record_service as svc
from app.rules import detect_plateau, analyze_reasons, generate_summary
from app.schemas.analytics import (
    DashboardResponse,
    TrendsResponse,
    PlateauResponse,
    ReasonsResponse,
    SummaryResponse,
)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(session: Session = Depends(get_session)):
    """Return KPI metrics for the dashboard."""
    all_records = svc.get_all_records_ordered(session)
    anchor = date.today()
    last7 = svc.get_records_by_days(session, 7, anchor_date=anchor)

    current_weight = None
    if all_records:
        current_weight = all_records[-1].weight

    avg_weight_7d = None
    avg_sleep_7d = None
    avg_calories_7d = None

    if len(last7) >= 5:
        avg_weight_7d = round(sum(r.weight for r in last7) / len(last7), 2)
        avg_sleep_7d = round(sum(r.sleep_hours for r in last7) / len(last7), 2)
        avg_calories_7d = round(sum(r.calories for r in last7) / len(last7), 1)

    # Weight change vs 7 days ago (same calendar date). If the exact date is missing, return None.
    # This is only computed when there is an exact record on the anchor date.
    weight_change_7d = None
    if all_records and current_weight is not None:
        weight_by_date = {r.record_date: r.weight for r in all_records}
        target_date = anchor - timedelta(days=7)
        if anchor in weight_by_date and target_date in weight_by_date:
            weight_change_7d = round(weight_by_date[anchor] - weight_by_date[target_date], 2)

    return DashboardResponse.model_validate({
        "current_weight": current_weight,
        "avg_weight_7d": avg_weight_7d,
        "avg_sleep_7d": avg_sleep_7d,
        "avg_calories_7d": avg_calories_7d,
        "weight_change_7d": weight_change_7d,
        "total_records": len(all_records),
        "last_record_date": all_records[-1].record_date.isoformat() if all_records else None,
    })


@router.get("/trends", response_model=TrendsResponse)
def get_trends(
    days: int = Query(default=30, ge=7, le=365),
    session: Session = Depends(get_session),
):
    """Return time-series data for trend charts."""
    records = svc.get_records_by_days(session, days, anchor_date=date.today())

    trend_data = [
        {
            "date": r.record_date.isoformat(),
            "weight": r.weight,
            "sleep_hours": r.sleep_hours,
            "calories": r.calories,
            "exercise_minutes": r.exercise_minutes,
            "steps": r.steps,
        }
        for r in records
    ]

    return TrendsResponse.model_validate({
        "days": days,
        "data_points": len(trend_data),
        "trends": trend_data,
    })


@router.get("/plateau", response_model=PlateauResponse)
def get_plateau(session: Session = Depends(get_session)):
    """Detect current plateau status."""
    all_records = svc.get_all_records_ordered(session)
    result = detect_plateau(all_records, anchor_date=date.today())
    return PlateauResponse.model_validate(result)


@router.get("/reasons", response_model=ReasonsResponse)
def get_reasons(
    calorie_target: int = Query(default=2000, ge=1000, le=5000),
    session: Session = Depends(get_session),
):
    """Analyse reasons for weight plateau."""
    all_records = svc.get_all_records_ordered(session)
    result = analyze_reasons(all_records, calorie_target, anchor_date=date.today())
    return ReasonsResponse.model_validate(result)


@router.get("/summary", response_model=SummaryResponse)
def get_summary(
    calorie_target: int = Query(default=2000, ge=1000, le=5000),
    session: Session = Depends(get_session),
):
    """Generate human-readable summary combining plateau status and reasons."""
    all_records = svc.get_all_records_ordered(session)
    plateau_result = detect_plateau(all_records, anchor_date=date.today())
    reason_result = analyze_reasons(all_records, calorie_target, anchor_date=date.today())
    summary = generate_summary(plateau_result, reason_result)

    return SummaryResponse.model_validate(
        {"plateau": plateau_result, "reasons": reason_result, "summary": summary}
    )
