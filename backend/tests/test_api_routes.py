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


def seed_last_days(client: TestClient, *, days: int = 8) -> None:
    today = date.today()
    start = today - timedelta(days=days - 1)

    for i in range(days):
        d = start + timedelta(days=i)
        client.post(
            "/api/health-records",
            json={
                "record_date": d.isoformat(),
                "weight": 75.0 + (i * 0.1),
                "sleep_hours": 7.0,
                "calories": 2000,
                "protein": 120,
                "exercise_minutes": 30,
                "exercise_type": "Walking",
                "steps": 8000,
                "note": None,
            },
        )


def test_dashboard_endpoint_shape_and_weight_change_7d():
    client = make_client()
    seed_last_days(client, days=8)  # includes today and today-7

    res = client.get("/api/analytics/dashboard")
    assert res.status_code == 200
    data = res.json()

    assert set(
        [
            "current_weight",
            "avg_weight_7d",
            "avg_sleep_7d",
            "avg_calories_7d",
            "weight_change_7d",
            "total_records",
            "last_record_date",
        ]
    ).issubset(data.keys())

    assert data["total_records"] >= 8
    assert data["weight_change_7d"] is not None


def test_summary_endpoint_shape():
    client = make_client()
    seed_last_days(client, days=8)

    res = client.get("/api/analytics/summary", params={"calorie_target": 2000})
    assert res.status_code == 200
    data = res.json()

    assert set(["plateau", "reasons", "summary"]).issubset(data.keys())
    assert set(["text", "insight", "status", "top_reasons"]).issubset(data["summary"].keys())


def test_query_param_validation():
    client = make_client()

    res = client.get("/api/analytics/trends", params={"days": 6})
    assert res.status_code == 422

    res = client.get("/api/analytics/reasons", params={"calorie_target": 999})
    assert res.status_code == 422
