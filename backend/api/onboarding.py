"""Onboarding & Visas API Router for TicketGenie."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database.crud import (
    create_onboarding_record,
    get_onboarding_records,
    update_onboarding_status,
)
from services.jwt_verifier import verify_azure_user

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
def list_onboarding_records(current_user: dict = Depends(verify_azure_user)):
    return get_onboarding_records()


@router.post("", status_code=201)
def handle_create_onboarding(
    req: OnboardingCreateRequest,
    current_user: dict = Depends(verify_azure_user),
):
    return create_onboarding_record(
        employee_name=req.employee_name,
        role=req.role,
        department=req.department,
        visa_status=req.visa_status or "H1-B / OPT",
        start_date=req.start_date or "2026-09-01",
        status=req.status or "In Progress",
    )


@router.put("/{record_id}")
def handle_update_onboarding(
    record_id: str,
    req: OnboardingUpdateRequest,
    current_user: dict = Depends(verify_azure_user),
):
    success = update_onboarding_status(record_id, req.status)
    if not success:
        raise HTTPException(status_code=404, detail="Onboarding record not found")
    return {
        "message": f"Updated onboarding record {record_id} status to {req.status}",
        "status": req.status,
    }
