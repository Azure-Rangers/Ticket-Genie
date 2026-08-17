from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.connection import get_db
from database.crud import (
    get_all_tickets,
    get_ticket_by_id,
    update_ticket,
)
from models.ticket import TicketCreate, TicketResponse, TicketUpdate
from services.jwt_verifier import verify_azure_user
from services.ticket_service import process_new_ticket

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", status_code=201, response_model=TicketResponse)
def handle_create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_azure_user),
):
    if not getattr(ticket, "is_anonymous", False):
        user_identity = current_user.get("oid") or current_user.get("email")
        if user_identity:
            ticket.requester_id = user_identity
    return process_new_ticket(ticket, db=db)


@router.get("", response_model=List[TicketResponse])
def list_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    department: Optional[str] = None,
    requester_id: Optional[str] = None,
    admin_view: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_azure_user),
):
    user_role = (current_user.get("role") or "").lower()
    is_super = any(r in user_role for r in ["super", "operations", "upper management", "executive"]) or current_user.get("is_dev", False)
    is_admin = is_super or ("admin" in user_role)

    if admin_view:
        if not is_admin:
            raise HTTPException(status_code=403, detail="Admin privileges required for admin_view access.")
        effective_requester = requester_id
        if is_super:
            effective_department = department
        else:
            effective_department = current_user.get("department") or department
    else:
        # Employee view: Every user (including admins) ONLY sees their own created tickets.
        effective_requester = current_user.get("oid") or current_user.get("email")
        effective_department = None

    tickets_list = get_all_tickets(
        status=status,
        priority=priority,
        search=search,
        requester_id=effective_requester,
        department=effective_department,
        db=db,
    )
    return tickets_list


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_azure_user),
):
    ticket = get_ticket_by_id(ticket_id, db=db)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket


@router.put("/{ticket_id}", response_model=TicketResponse)
def handle_update_ticket(
    ticket_id: str,
    ticket_update: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_azure_user),
):
    updated = update_ticket(
        ticket_id,
        ticket_update,
        db=db,
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return updated


# ---------------------------------------------------------------------------
# Document Export (PDF / DOCX)
# ---------------------------------------------------------------------------


@router.get("/{ticket_id}/export")
def export_ticket_document(
    ticket_id: str,
    format: str = "pdf",
    current_user: dict = Depends(verify_azure_user),
):
    from fastapi import Response

    from services.document_service import generate_ticket_docx, generate_ticket_pdf

    doc_format = format.lower().strip()
    if doc_format == "docx":
        docx_bytes = generate_ticket_docx(ticket_id)
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=ticket_{ticket_id}.docx"
            },
        )

    pdf_bytes = generate_ticket_pdf(ticket_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=ticket_{ticket_id}.pdf"},
    )


# ---------------------------------------------------------------------------
# Threaded Ticket Comments / Chat
# ---------------------------------------------------------------------------


class CommentCreateRequest(BaseModel):
    message: str
    sender_id: Optional[str] = None
    sender_role: Optional[str] = None


@router.get("/{ticket_id}/comments")
def list_comments_for_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_azure_user),
):
    from database.crud import get_ticket_comments

    return get_ticket_comments(ticket_id, db=db)


@router.post("/{ticket_id}/comments", status_code=201)
def post_comment_to_ticket(
    ticket_id: str,
    req: CommentCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_azure_user),
):
    from database.crud import add_ticket_comment

    sender_id = current_user.get("oid") or current_user.get("email") or req.sender_id or "user"
    sender_role = current_user.get("role") or req.sender_role or "Employee"

    return add_ticket_comment(
        ticket_id=ticket_id,
        message=req.message,
        sender_id=sender_id,
        sender_role=sender_role,
        db=db,
    )
