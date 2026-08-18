"""Announcements API Router for TicketGenie."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database.crud import (
    create_announcement,
    delete_announcement,
    get_announcements,
)
from services.jwt_verifier import verify_azure_user

router = APIRouter(prefix="/announcements", tags=["announcements"])


class AnnouncementCreateRequest(BaseModel):
    title: str
    content: str
    category: Optional[str] = "General Alert"
    author: Optional[str] = "Admin Operations"


@router.get("")
def list_announcements(current_user: dict = Depends(verify_azure_user)):
    return get_announcements()


@router.post("", status_code=201)
def handle_create_announcement(
    req: AnnouncementCreateRequest,
    current_user: dict = Depends(verify_azure_user),
):
    return create_announcement(
        title=req.title,
        content=req.content,
        category=req.category or "General Alert",
        author=req.author or current_user.get("name", "Admin Operations"),
    )


@router.delete("/{anc_id}")
def handle_delete_announcement(
    anc_id: str,
    current_user: dict = Depends(verify_azure_user),
):
    removed = delete_announcement(anc_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {"message": f"Deleted announcement {anc_id}"}
