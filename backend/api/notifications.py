"""Notifications API Router for TicketGenie."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database.crud import (
    create_notification,
    get_notifications,
    mark_notification_read,
)
from services.jwt_verifier import verify_azure_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationCreateRequest(BaseModel):
    title: str
    message: str
    user_id: Optional[str] = "all"


@router.get("")
def list_notifications(
    user_id: Optional[str] = None,
    current_user: dict = Depends(verify_azure_user),
):
    user_role = (current_user.get("role") or "").lower()
    is_admin = any(
        r in user_role for r in ["admin", "super", "operations"]
    ) or current_user.get("is_dev", False)

    target_user_id = (
        user_id
        if (is_admin and user_id)
        else (current_user.get("oid") or current_user.get("email") or "user")
    )
    return get_notifications(user_id=target_user_id)


@router.post("", status_code=201)
def handle_create_notification(
    req: NotificationCreateRequest,
    current_user: dict = Depends(verify_azure_user),
):
    return create_notification(
        title=req.title,
        message=req.message,
        user_id=req.user_id or "all",
    )


@router.put("/{notif_id}/read")
def handle_mark_notification_read(
    notif_id: str,
    current_user: dict = Depends(verify_azure_user),
):
    success = mark_notification_read(notif_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": f"Marked notification {notif_id} as read"}


@router.get("/outbox")
def list_email_outbox(
    current_user: dict = Depends(verify_azure_user),
):
    """Retrieve sent email outbox audit trail."""
    from services.email_service import get_outbox_log

    return get_outbox_log()

