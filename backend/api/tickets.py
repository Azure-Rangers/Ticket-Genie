from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from database.crud import (
    create_ticket,
    get_all_tickets,
    get_ticket_by_id,
    update_ticket,
)
from models.ticket import TicketCreate, TicketResponse, TicketUpdate

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", status_code=201, response_model=TicketResponse)
def handle_create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    created = create_ticket(ticket, db=db)
    return created


@router.get("", response_model=List[TicketResponse])
def list_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    tickets_list = get_all_tickets(
        status=status, priority=priority, search=search, db=db
    )
    return tickets_list


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = get_ticket_by_id(ticket_id, db=db)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.put("/{ticket_id}", response_model=TicketResponse)
def handle_update_ticket(
    ticket_id: str, ticket_update: TicketUpdate, db: Session = Depends(get_db)
):
    updated = update_ticket(ticket_id, ticket_update, db=db)
    if updated is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return updated
