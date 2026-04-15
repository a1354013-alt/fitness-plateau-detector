from __future__ import annotations

from datetime import date

import pytest
from fastapi import HTTPException

from app.schemas.health_record import HealthRecordCreate, HealthRecordUpdate
from app.services import health_record_service as svc


def test_create_get_update_delete_record(session):
    created = svc.create_record(
        session,
        HealthRecordCreate(
            record_date=date(2026, 4, 1),
            weight=75.2,
            sleep_hours=7.0,
            calories=1900,
            protein=120,
            exercise_minutes=30,
            exercise_type="Running",
            steps=8000,
            note="ok",
        ),
    )

    fetched = svc.get_record(session, created.id)
    assert fetched is not None
    assert fetched.record_date == date(2026, 4, 1)
    assert fetched.weight == pytest.approx(75.2)

    updated = svc.update_record(
        session,
        created.id,
        HealthRecordUpdate(weight=74.9, note="updated"),
    )
    assert updated is not None
    assert updated.weight == pytest.approx(74.9)
    assert updated.note == "updated"

    ok = svc.delete_record(session, created.id)
    assert ok is True
    assert svc.get_record(session, created.id) is None


def test_create_same_date_conflict(session):
    svc.create_record(
        session,
        HealthRecordCreate(
            record_date=date(2026, 4, 1),
            weight=75.0,
            sleep_hours=7.0,
            calories=2000,
            exercise_minutes=0,
        ),
    )

    with pytest.raises(HTTPException) as exc:
        svc.create_record(
            session,
            HealthRecordCreate(
                record_date=date(2026, 4, 1),
                weight=75.1,
                sleep_hours=7.0,
                calories=2000,
                exercise_minutes=0,
            ),
        )

    assert exc.value.status_code == 409

