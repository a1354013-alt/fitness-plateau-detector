from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_serializer, field_validator, model_validator

from app.time import format_datetime_utc_z, get_today

MAX_NOTE_LENGTH = 500
MAX_EXERCISE_TYPE_LENGTH = 50
MAX_CALORIES = 20000
MAX_PROTEIN = 500
MAX_EXERCISE_MINUTES = 1440
MAX_STEPS = 200000


class HealthRecordCreate(BaseModel):
    record_date: date
    weight: float = Field(..., gt=0, le=500, description="Weight in kg")
    sleep_hours: float = Field(..., ge=0, le=24, description="Sleep hours")
    calories: int = Field(..., ge=0, le=MAX_CALORIES, description="Daily calories intake")
    protein: Optional[int] = Field(default=None, ge=0, le=MAX_PROTEIN)
    exercise_minutes: int = Field(default=0, ge=0, le=MAX_EXERCISE_MINUTES)
    exercise_type: Optional[str] = Field(default=None, max_length=MAX_EXERCISE_TYPE_LENGTH)
    steps: Optional[int] = Field(default=None, ge=0, le=MAX_STEPS)
    note: Optional[str] = Field(default=None, max_length=MAX_NOTE_LENGTH)

    @field_validator("record_date")
    @classmethod
    def record_date_must_not_be_in_future(cls, v: date) -> date:
        today = get_today()
        if v > today:
            raise ValueError(f"record_date cannot be in the future (max: {today.isoformat()})")
        return v

    @field_validator("weight")
    @classmethod
    def weight_must_be_reasonable(cls, v):
        if v <= 0 or v > 500:
            raise ValueError("Weight must be between 0 and 500 kg")
        return round(v, 2)

    @field_validator("note")
    @classmethod
    def normalize_note(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        trimmed = v.strip()
        return trimmed or None

    @field_validator("exercise_type")
    @classmethod
    def normalize_exercise_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        trimmed = " ".join(v.strip().split())
        return trimmed or None


class HealthRecordUpdate(BaseModel):
    record_date: Optional[date] = None
    weight: Optional[float] = Field(default=None, gt=0, le=500, description="Weight in kg")
    sleep_hours: Optional[float] = Field(default=None, ge=0, le=24, description="Sleep hours")
    calories: Optional[int] = Field(default=None, ge=0, le=MAX_CALORIES, description="Daily calories intake")
    protein: Optional[int] = Field(default=None, ge=0, le=MAX_PROTEIN)
    exercise_minutes: Optional[int] = Field(default=None, ge=0, le=MAX_EXERCISE_MINUTES)
    exercise_type: Optional[str] = Field(default=None, max_length=MAX_EXERCISE_TYPE_LENGTH)
    steps: Optional[int] = Field(default=None, ge=0, le=MAX_STEPS)
    note: Optional[str] = Field(default=None, max_length=MAX_NOTE_LENGTH)

    @field_validator("record_date")
    @classmethod
    def record_date_must_not_be_in_future(cls, v: Optional[date]) -> Optional[date]:
        if v is None:
            return v
        today = get_today()
        if v > today:
            raise ValueError(f"record_date cannot be in the future (max: {today.isoformat()})")
        return v

    @model_validator(mode="after")
    def disallow_explicit_null_for_required_fields(self):
        """Distinguish 'field not provided' vs 'field provided as null'.

        For non-nullable DB columns, explicit null in an update payload must be rejected
        with a 422, rather than failing at commit time.
        """

        fields_set = getattr(self, "__pydantic_fields_set__", set())
        non_nullable = ("record_date", "weight", "sleep_hours", "calories", "exercise_minutes")
        for field in non_nullable:
            if field in fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self

    @field_validator("weight")
    @classmethod
    def weight_must_be_reasonable(cls, v):
        if v is not None and (v <= 0 or v > 500):
            raise ValueError("Weight must be between 0 and 500 kg")
        return round(v, 2) if v is not None else v

    @field_validator("note")
    @classmethod
    def normalize_note(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        trimmed = v.strip()
        return trimmed or None

    @field_validator("exercise_type")
    @classmethod
    def normalize_exercise_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        trimmed = " ".join(v.strip().split())
        return trimmed or None


class HealthRecordResponse(BaseModel):
    id: int
    record_date: date
    weight: float
    sleep_hours: float
    calories: int
    protein: Optional[int]
    exercise_minutes: int
    exercise_type: Optional[str]
    steps: Optional[int]
    note: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("created_at", "updated_at")
    def serialize_utc_z(self, value: datetime) -> str:
        return format_datetime_utc_z(value)


class HealthRecordListResponse(BaseModel):
    total: int
    records: list[HealthRecordResponse]
