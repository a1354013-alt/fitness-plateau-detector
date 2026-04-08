from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator


class HealthRecordCreate(BaseModel):
    record_date: date
    weight: float = Field(..., gt=0, lt=500, description="Weight in kg")
    sleep_hours: float = Field(..., ge=0, le=24, description="Sleep hours")
    calories: int = Field(..., ge=0, description="Daily calories intake")
    protein: Optional[int] = Field(default=None, ge=0)
    exercise_minutes: int = Field(default=0, ge=0)
    exercise_type: Optional[str] = Field(default=None, max_length=100)
    steps: Optional[int] = Field(default=None, ge=0)
    note: Optional[str] = None

    @field_validator("weight")
    @classmethod
    def weight_must_be_reasonable(cls, v):
        if v <= 0 or v > 500:
            raise ValueError("Weight must be between 0 and 500 kg")
        return round(v, 2)


class HealthRecordUpdate(BaseModel):
    record_date: Optional[date] = None
    weight: Optional[float] = Field(default=None, gt=0, lt=500, description="Weight in kg")
    sleep_hours: Optional[float] = Field(default=None, ge=0, le=24, description="Sleep hours")
    calories: Optional[int] = Field(default=None, ge=0, description="Daily calories intake")
    protein: Optional[int] = Field(default=None, ge=0)
    exercise_minutes: Optional[int] = Field(default=None, ge=0)
    exercise_type: Optional[str] = Field(default=None, max_length=100)
    steps: Optional[int] = Field(default=None, ge=0)
    note: Optional[str] = None

    @field_validator("weight")
    @classmethod
    def weight_must_be_reasonable(cls, v):
        if v is not None and (v <= 0 or v > 500):
            raise ValueError("Weight must be between 0 and 500 kg")
        return round(v, 2) if v is not None else v


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


class HealthRecordListResponse(BaseModel):
    total: int
    records: list[HealthRecordResponse]
