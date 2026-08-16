"""HR Analytics & Helpdesk Resolution Trends Router."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from database.crud import get_analytics_summary
from services.jwt_verifier import verify_azure_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/trends")
def get_analytics_trends(current_user: dict = Depends(verify_azure_user)):
    return get_analytics_summary()
