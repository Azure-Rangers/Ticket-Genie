"""User Profiles API Router for TicketGenie."""

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

from database.crud import get_user_profile, update_user_profile

router = APIRouter(prefix="/users", tags=["users"])


class UserProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None


@router.get("/profile")
def handle_get_profile(user_id: Optional[str] = "usr-1"):
    return get_user_profile(user_id=user_id or "usr-1")


@router.put("/profile")
def handle_update_profile(req: UserProfileUpdateRequest, user_id: Optional[str] = "usr-1"):
    return update_user_profile(
        user_id=user_id or "usr-1",
        name=req.name,
        email=req.email,
        phone=req.phone,
        department=req.department,
    )
