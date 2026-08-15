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
from services.ticket_service import process_new_ticket

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", status_code=201, response_model=TicketResponse)
def handle_create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
):
    return process_new_ticket(ticket, db=db)


@router.get("", response_model=List[TicketResponse])
def list_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    tickets_list = get_all_tickets(
        status=status,
        priority=priority,
        search=search,
        db=db,
    )
    return tickets_list


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
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
def export_ticket_document(ticket_id: str, format: str = "pdf"):
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
    sender_id: Optional[str] = "user"
    sender_role: Optional[str] = "Employee"


@router.get("/{ticket_id}/comments")
def list_comments_for_ticket(ticket_id: str, db: Session = Depends(get_db)):
    from database.crud import get_ticket_comments

    return get_ticket_comments(ticket_id, db=db)


@router.post("/{ticket_id}/comments", status_code=201)
def post_comment_to_ticket(
    ticket_id: str, req: CommentCreateRequest, db: Session = Depends(get_db)
):
    from database.crud import add_ticket_comment

    return add_ticket_comment(
        ticket_id=ticket_id,
        message=req.message,
        sender_id=req.sender_id or "user",
        sender_role=req.sender_role or "Employee",
        db=db,
    )
