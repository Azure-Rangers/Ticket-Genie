"""HR Analytics & Helpdesk Resolution Trends Router."""

from __future__ import annotations

from fastapi import APIRouter
from database.crud import get_analytics_summary

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/trends")
def get_analytics_trends():
    return get_analytics_summary()
