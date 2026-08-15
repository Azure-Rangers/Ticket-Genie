"""Notifications API Router for TicketGenie."""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database.crud import (
    create_notification,
    get_notifications,
    mark_notification_read,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationCreateRequest(BaseModel):
    title: str
    message: str
    user_id: Optional[str] = "all"


@router.get("")
def list_notifications(user_id: Optional[str] = "user"):
    return get_notifications(user_id=user_id or "user")


@router.post("", status_code=201)
def handle_create_notification(req: NotificationCreateRequest):
    return create_notification(
        title=req.title,
        message=req.message,
        user_id=req.user_id or "all",
    )


@router.put("/{notif_id}/read")
def handle_mark_notification_read(notif_id: str):
    success = mark_notification_read(notif_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": f"Notification {notif_id} marked as read"}
