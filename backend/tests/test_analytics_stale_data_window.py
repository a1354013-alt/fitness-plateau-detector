from __future__ import annotations

from datetime import date, timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.analytics import router as analytics_router
from app.api.health_records import router as health_records_router
from app.database import get_session
from app.models.health_record import (
    HealthRecord,  # noqa: F401  (ensure SQLModel metadata is populated)
)


def make_client() -> TestClient:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app = FastAPI()
    app.include_router(health_records_router)
    app.include_router(analytics_router)
    app.dependency_overrides[get_session] = override_get_session
    return TestClient(app)


def test_dashboard_averages_null_when_no_recent_records():
    client = make_client()

    old_day = date.today() - timedelta(days=20)
    res = client.post(
        "/api/health-records",
        json={
            "record_date": old_day.isoformat(),
            "weight": 75.0,
            "sleep_hours": 7.0,
            "calories": 2000,
            "exercise_minutes": 0,
        },
    )
    assert res.status_code == 201

    dash = client.get("/api/analytics/dashboard")
    assert dash.status_code == 200
    data = dash.json()

    assert data["total_records"] == 1
    assert data["current_weight"] == 75.0
    assert data["last_record_date"] == old_day.isoformat()

    # Averages are for the last 7 calendar days ending today. With no recent records, they remain null.
    assert data["avg_weight_7d"] is None
    assert data["avg_sleep_7d"] is None
    assert data["avg_calories_7d"] is None
    # 7d change requires records for today and exactly 7 days ago.
    assert data["weight_change_7d"] is None


def test_summary_insufficient_when_no_recent_records():
    client = make_client()

    old_day = date.today() - timedelta(days=20)
    res = client.post(
        "/api/health-records",
        json={
            "record_date": old_day.isoformat(),
            "weight": 75.0,
            "sleep_hours": 7.0,
            "calories": 2000,
            "exercise_minutes": 0,
        },
    )
    assert res.status_code == 201

    res = client.get("/api/analytics/summary", params={"calorie_target": 2000})
    assert res.status_code == 200
    data = res.json()

    assert data["plateau"]["status"] == "insufficient_data"
    assert data["reasons"]["status"] == "insufficient_data"
    assert data["summary"]["status"] == "insufficient_data"
