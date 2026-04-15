from __future__ import annotations

from datetime import date

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

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
    app.dependency_overrides[get_session] = override_get_session
    return TestClient(app)


def seed(client: TestClient, d: date, *, weight: float) -> None:
    res = client.post(
        "/api/health-records",
        json={
            "record_date": d.isoformat(),
            "weight": weight,
            "sleep_hours": 7.0,
            "calories": 2000,
            "exercise_minutes": 0,
        },
    )
    assert res.status_code == 201


def test_list_filters_are_inclusive_and_sorted_desc():
    client = make_client()
    d1 = date(2026, 4, 1)
    d2 = date(2026, 4, 2)
    d3 = date(2026, 4, 3)

    seed(client, d1, weight=75.0)
    seed(client, d2, weight=74.8)
    seed(client, d3, weight=74.6)

    res = client.get(
        "/api/health-records",
        params={"start_date": d2.isoformat(), "end_date": d2.isoformat(), "skip": 0, "limit": 100},
    )
    assert res.status_code == 200
    payload = res.json()
    assert payload["total"] == 1
    assert payload["records"][0]["record_date"] == d2.isoformat()

    res = client.get("/api/health-records", params={"start_date": d2.isoformat(), "skip": 0, "limit": 100})
    assert res.status_code == 200
    payload = res.json()
    # Should include d2 and d3, ordered desc.
    assert payload["total"] == 2
    assert [r["record_date"] for r in payload["records"]] == [d3.isoformat(), d2.isoformat()]


def test_list_rejects_start_date_after_end_date():
    client = make_client()
    d1 = date(2026, 4, 1)
    d2 = date(2026, 4, 2)

    seed(client, d1, weight=75.0)
    seed(client, d2, weight=74.8)

    res = client.get(
        "/api/health-records",
        params={"start_date": d2.isoformat(), "end_date": d1.isoformat(), "skip": 0, "limit": 100},
    )
    assert res.status_code == 422


def test_list_accepts_valid_date_range():
    client = make_client()
    d1 = date(2026, 4, 1)
    d2 = date(2026, 4, 2)
    d3 = date(2026, 4, 3)

    seed(client, d1, weight=75.0)
    seed(client, d2, weight=74.8)
    seed(client, d3, weight=74.6)

    res = client.get(
        "/api/health-records",
        params={"start_date": d1.isoformat(), "end_date": d3.isoformat(), "skip": 0, "limit": 100},
    )
    assert res.status_code == 200
    payload = res.json()
    assert payload["total"] == 3
    assert [r["record_date"] for r in payload["records"]] == [d3.isoformat(), d2.isoformat(), d1.isoformat()]
