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


def _is_admin_user(current_user: dict) -> bool:
    role = (current_user.get("role") or "").lower()
    return any(
        marker in role
        for marker in ("admin", "super", "operations", "management", "executive")
    )


def _admin_can_access_ticket(current_user: dict, ticket: dict) -> bool:
    role = (current_user.get("role") or "").lower()
    if any(
        marker in role for marker in ("super", "operations", "management", "executive")
    ):
        return True
    user_department = (current_user.get("department") or "").lower().strip()
    ticket_department = (ticket.get("department") or "").lower().strip()
    return bool(user_department and user_department in ticket_department)


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
    is_super = any(
        r in user_role for r in ["super", "operations", "upper management", "executive"]
    ) or current_user.get("is_dev", False)
    is_admin = is_super or ("admin" in user_role)

    if admin_view:
        if not is_admin:
            raise HTTPException(
                status_code=403,
                detail="Admin privileges required for admin_view access.",
            )
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
    ticket = get_ticket_by_id(ticket_id, db=db)
    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    if ticket_update.status is not None:
        new_status = ticket_update.status.strip().lower()
        if new_status in ("resolved", "closed"):
            current_user_oid = str(current_user.get("oid") or "").strip().lower()
            current_user_email = str(current_user.get("email") or "").strip().lower()

            ticket_requester = str(ticket.get("requester_id") or "").strip().lower()

            is_creator = False
            if ticket_requester:
                if current_user_oid and ticket_requester == current_user_oid:
                    is_creator = True
                elif current_user_email and ticket_requester == current_user_email:
                    is_creator = True
                else:
                    from database.crud import _resolve_user_email

                    resolved_email = str(
                        _resolve_user_email(ticket_requester, db) or ""
                    ).strip().lower()
                    if current_user_email and resolved_email == current_user_email:
                        is_creator = True

            if is_creator:
                raise HTTPException(
                    status_code=403,
                    detail="You cannot resolve tickets you created.",
                )

    updated = update_ticket(
        ticket_id,
        ticket_update,
        db=db,
    )

    return updated



# ---------------------------------------------------------------------------
# Document Export (PDF / DOCX)
# ---------------------------------------------------------------------------


@router.get("/{ticket_id}/export")
def export_ticket_document(
    ticket_id: str,
    format: str = "pdf",
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_azure_user),
):
    from fastapi import Response

    from database.crud import get_ticket_comments
    from services.document_service import generate_ticket_docx, generate_ticket_pdf

    ticket = get_ticket_by_id(ticket_id, db=db)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    user_role = (current_user.get("role") or "").lower()
    is_super = any(
        role in user_role for role in ("super", "operations", "management", "executive")
    )
    is_admin = is_super or "admin" in user_role
    if is_admin and not is_super:
        user_department = (current_user.get("department") or "").lower().strip()
        ticket_department = (ticket.get("department") or "").lower().strip()
        allowed = bool(user_department and user_department in ticket_department)
    elif is_super:
        allowed = True
    else:
        identities = {
            str(current_user.get("oid") or "").lower(),
            str(current_user.get("email") or "").lower(),
        }
        allowed = str(ticket.get("requester_id") or "").lower() in identities
    if not allowed:
        raise HTTPException(status_code=403, detail="Ticket access denied")

    comments = [
        comment
        for comment in get_ticket_comments(ticket_id, db=db)
        if is_admin or comment.get("sender_role") != "Private"
    ]

    doc_format = format.lower().strip()
    if doc_format == "docx":
        docx_bytes = generate_ticket_docx(ticket_id, ticket=ticket, comments=comments)
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=ticket_{ticket_id}.docx"
            },
        )

    pdf_bytes = generate_ticket_pdf(ticket_id, ticket=ticket, comments=comments)
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


@router.post("/{ticket_id}/suggested-response")
def suggest_response_for_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_azure_user),
):
    """Draft an AI response for an authorized human support agent to review."""
    from agents.response_agent import draft_response
    from database.crud import get_ticket_comments
    from services.ai_service import AIServiceError

    if not _is_admin_user(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")

    ticket = get_ticket_by_id(ticket_id, db=db)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if not _admin_can_access_ticket(current_user, ticket):
        raise HTTPException(status_code=403, detail="Ticket access denied")

    public_comments = [
        comment
        for comment in get_ticket_comments(ticket_id, db=db)
        if comment.get("sender_role") != "Private"
    ]
    history = (
        "\n".join(
            f"[{comment.get('createdAt', 'N/A')}] "
            f"{comment.get('sender_role', 'Unknown')}: {comment.get('message', '')}"
            for comment in public_comments
        )
        or "No prior public conversation."
    )

    try:
        return draft_response(
            ticket.get("title") or "Untitled ticket",
            ticket.get("description") or "No description provided.",
            category=ticket.get("category") or "General",
            priority=ticket.get("priority") or "Medium",
            queue=ticket.get("department") or "Support",
            conversation_history=history,
        )
    except AIServiceError as exc:
        raise HTTPException(
            status_code=503,
            detail="Suggested response service is temporarily unavailable.",
        ) from exc


@router.get("/{ticket_id}/comments")
def list_comments_for_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_azure_user),
):
    from database.crud import get_ticket_comments

    if get_ticket_by_id(ticket_id, db=db) is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    comments = get_ticket_comments(ticket_id, db=db)
    user_role = (current_user.get("role") or "").lower()
    is_admin = any(
        role in user_role
        for role in ("admin", "super", "operations", "management", "executive")
    )
    if not is_admin:
        comments = [c for c in comments if c.get("sender_role") != "Private"]
    return comments


@router.post("/{ticket_id}/comments", status_code=201)
def post_comment_to_ticket(
    ticket_id: str,
    req: CommentCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_azure_user),
):
    from database.crud import add_ticket_comment

    if get_ticket_by_id(ticket_id, db=db) is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    sender_id = current_user.get("oid") or current_user.get("email")
    user_role = (current_user.get("role") or "Employee").strip()
    user_role_lower = user_role.lower()
    is_admin = any(
        role in user_role_lower
        for role in ("admin", "super", "operations", "management", "executive")
    )

    if req.sender_role == "Private":
        if not is_admin:
            raise HTTPException(
                status_code=403, detail="Private notes require admin access"
            )
        sender_role = "Private"
    elif is_admin:
        department = (current_user.get("department") or "").lower()
        sender_role = "HR Support" if "hr" in department else "Support"
    else:
        sender_role = "Employee"

    return add_ticket_comment(
        ticket_id=ticket_id,
        message=req.message,
        sender_id=sender_id,
        sender_role=sender_role,
        db=db,
    )
