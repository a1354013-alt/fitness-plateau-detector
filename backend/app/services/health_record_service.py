from datetime import date, datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import Session, desc, select

from app.models.health_record import HealthRecord
from app.schemas.health_record import HealthRecordCreate, HealthRecordUpdate

# Database timestamps are UTC naive. Treatment must be consistent system-wide.

def create_record(session: Session, data: HealthRecordCreate) -> HealthRecord:
    # Check for existing record on the same date
    existing_record = session.exec(select(HealthRecord).where(HealthRecord.record_date == data.record_date)).first()
    if existing_record:
        raise HTTPException(status_code=409, detail=f"Record for date {data.record_date} already exists. Please update it instead.")

    record = HealthRecord(**data.model_dump())
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def get_record(session: Session, record_id: int) -> Optional[HealthRecord]:
    return session.get(HealthRecord, record_id)


def get_records(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> tuple[list[HealthRecord], int]:
    query = select(HealthRecord)
    if start_date:
        query = query.where(HealthRecord.record_date >= start_date)
    if end_date:
        query = query.where(HealthRecord.record_date <= end_date)
    query = query.order_by(desc(HealthRecord.record_date)).offset(skip).limit(limit)

    records = session.exec(query).all()

    total_query = select(func.count()).select_from(HealthRecord)
    if start_date:
        total_query = total_query.where(HealthRecord.record_date >= start_date)
    if end_date:
        total_query = total_query.where(HealthRecord.record_date <= end_date)
    total = session.exec(total_query).one()
    return list(records), total


def update_record(
    session: Session, record_id: int, data: HealthRecordUpdate
) -> Optional[HealthRecord]:
    record = session.get(HealthRecord, record_id)
    if not record:
        return None

    update_data = data.model_dump(exclude_unset=True)

    # Defense-in-depth: if a non-nullable column is explicitly set to null in the payload,
    # reject it early (422) instead of letting it reach the DB commit.
    non_nullable = ("record_date", "weight", "sleep_hours", "calories", "exercise_minutes")
    for field in non_nullable:
        if field in update_data and update_data[field] is None:
            raise HTTPException(status_code=422, detail=f"{field} cannot be null")

    # Check for date collision if record_date is being updated
    if "record_date" in update_data and update_data["record_date"] != record.record_date:
        existing_record_on_new_date = session.exec(
            select(HealthRecord).where(
                HealthRecord.record_date == update_data["record_date"],
                HealthRecord.id != record_id
            )
        ).first()
        if existing_record_on_new_date:
            raise HTTPException(
                status_code=409,
                detail=f"Record for date {update_data['record_date']} already exists for another record.",
            )

    for key, value in update_data.items():
        setattr(record, key, value)

    record.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def delete_record(session: Session, record_id: int) -> bool:
    record = session.get(HealthRecord, record_id)
    if not record:
        return False
    session.delete(record)
    session.commit()
    return True


def get_records_by_days(session: Session, days: int, *, anchor_date: Optional[date] = None) -> list[HealthRecord]:
    """Return records within the last N calendar days (inclusive), ordered ascending.

    The default anchor_date is today, not the latest record date, so that UI
    semantics like "last 7 days" are based on the user's calendar expectations.
    """

    end_date = anchor_date or date.today()
    start_date = end_date - timedelta(days=days - 1)
    query = select(HealthRecord).where(
        HealthRecord.record_date >= start_date,
        HealthRecord.record_date <= end_date,
    ).order_by(HealthRecord.record_date)
    return list(session.exec(query).all())


def get_all_records_ordered(session: Session) -> list[HealthRecord]:
    query = select(HealthRecord).order_by(HealthRecord.record_date)
    return list(session.exec(query).all())
