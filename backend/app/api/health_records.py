from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from app.database import get_session
from app.schemas.health_record import (
    HealthRecordCreate,
    HealthRecordUpdate,
    HealthRecordResponse,
    HealthRecordListResponse,
)
from app.services import health_record_service as svc

router = APIRouter(prefix="/api/health-records", tags=["Health Records"])


@router.post("", response_model=HealthRecordResponse, status_code=201)
def create_health_record(
    data: HealthRecordCreate,
    session: Session = Depends(get_session),
):
    record = svc.create_record(session, data)
    return record


@router.get("", response_model=HealthRecordListResponse)
def list_health_records(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    session: Session = Depends(get_session),
):
    records, total = svc.get_records(session, skip, limit, start_date, end_date)
    return HealthRecordListResponse(total=total, records=records)


@router.get("/{record_id}", response_model=HealthRecordResponse)
def get_health_record(
    record_id: int,
    session: Session = Depends(get_session),
):
    record = svc.get_record(session, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.put("/{record_id}", response_model=HealthRecordResponse)
def update_health_record(
    record_id: int,
    data: HealthRecordUpdate,
    session: Session = Depends(get_session),
):
    record = svc.update_record(session, record_id, data)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.delete("/{record_id}", status_code=204)
def delete_health_record(
    record_id: int,
    session: Session = Depends(get_session),
):
    success = svc.delete_record(session, record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Record not found")
    from fastapi.responses import Response
    return Response(status_code=204)
