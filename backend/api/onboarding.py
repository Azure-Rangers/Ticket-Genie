"""Onboarding & Visas API Router for TicketGenie."""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database.crud import (
    create_onboarding_record,
    get_onboarding_records,
    update_onboarding_status,
)

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


class OnboardingCreateRequest(BaseModel):
    employee_name: str
    role: str
    department: str
    visa_status: Optional[str] = "H1-B / OPT"
    start_date: Optional[str] = "2026-09-01"
    status: Optional[str] = "In Progress"


class OnboardingUpdateRequest(BaseModel):
    status: str


@router.get("")
def list_onboarding_records():
    return get_onboarding_records()


@router.post("", status_code=201)
def handle_create_onboarding(req: OnboardingCreateRequest):
    return create_onboarding_record(
        employee_name=req.employee_name,
        role=req.role,
        department=req.department,
        visa_status=req.visa_status or "H1-B / OPT",
        start_date=req.start_date or "2026-09-01",
        status=req.status or "In Progress",
    )


@router.put("/{rec_id}")
def handle_update_onboarding(rec_id: str, req: OnboardingUpdateRequest):
    updated = update_onboarding_status(rec_id, req.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Onboarding record not found")
    return updated
