from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


PlateauStatus = Literal["losing", "plateau", "gaining", "insufficient_data"]
ReasonsStatus = Literal["ok", "insufficient_data"]


class DashboardResponse(BaseModel):
    current_weight: Optional[float] = None
    avg_weight_7d: Optional[float] = None
    avg_sleep_7d: Optional[float] = None
    avg_calories_7d: Optional[float] = None
    weight_change_7d: Optional[float] = None
    total_records: int = 0
    last_record_date: Optional[str] = None


class TrendPoint(BaseModel):
    date: str
    weight: float
    sleep_hours: float
    calories: int
    exercise_minutes: int
    steps: Optional[int] = None


class TrendsResponse(BaseModel):
    days: int = Field(..., ge=7, le=365)
    data_points: int = Field(..., ge=0)
    trends: list[TrendPoint]


class PlateauResponse(BaseModel):
    status: PlateauStatus
    rule_a: Optional[bool] = None
    rule_b: Optional[bool] = None
    last7_avg: Optional[float] = None
    prev7_avg: Optional[float] = None
    avg_change: Optional[float] = None
    last7_fluctuation: Optional[float] = None
    last7_min: Optional[float] = None
    last7_max: Optional[float] = None
    data_completeness: Optional[float] = Field(default=None, ge=0, le=1)
    message: Optional[str] = None


class ReasonItem(BaseModel):
    code: str
    label: str
    description: str
    severity: float = Field(..., ge=0)
    value: float
    threshold: float
    details: Optional[dict[str, Any]] = None


class ReasonsResponse(BaseModel):
    status: ReasonsStatus = "ok"
    message: Optional[str] = None
    reasons: list[ReasonItem]
    all_reasons: list[ReasonItem]
    data_points: int = Field(..., ge=0)
    missing_days: int = Field(..., ge=0, le=7)


class SummaryPayload(BaseModel):
    text: str
    insight: str
    status: PlateauStatus
    top_reasons: list[str]


class SummaryResponse(BaseModel):
    plateau: PlateauResponse
    reasons: ReasonsResponse
    summary: SummaryPayload
