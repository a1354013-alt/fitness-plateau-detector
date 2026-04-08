from typing import Optional
from datetime import date, datetime, timezone
from sqlmodel import SQLModel, Field


# All timestamps in the database are stored as UTC naive datetime objects.
# They should be treated as UTC and converted to local time only for display purposes.
def _utcnow_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class HealthRecord(SQLModel, table=True):
    __tablename__ = "health_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    record_date: date = Field(index=True, unique=True)
    weight: float
    sleep_hours: float
    calories: int
    protein: Optional[int] = Field(default=None)
    exercise_minutes: int = Field(default=0)
    exercise_type: Optional[str] = Field(default=None, max_length=100)
    steps: Optional[int] = Field(default=None)
    note: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=_utcnow_naive)
    updated_at: datetime = Field(default_factory=_utcnow_naive)
