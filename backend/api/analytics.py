"""HR Analytics & Helpdesk Resolution Trends Router."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database.connection import get_db
from database.crud import get_analytics_summary
from services.department_analytics_service import (
    AnalyticsAccessError,
    get_department_health_analytics,
    resolve_analytics_department,
)
from services.jwt_verifier import verify_azure_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/trends")
def get_analytics_trends(current_user: dict = Depends(verify_azure_user)):
    return get_analytics_summary()


@router.get("/department-health")
def get_department_health(
    department: Optional[str] = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_azure_user),
):
    """Calculated department analytics scoped by the verified JWT identity."""
    try:
        requested_department = resolve_analytics_department(current_user, department)
    except AnalyticsAccessError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(error)
        ) from error
    return get_department_health_analytics(db, requested_department)
