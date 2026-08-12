from typing import Optional
from database.crud import create_ticket, get_all_tickets, get_ticket_by_id
from fastapi import APIRouter, HTTPException
from models.ticket import TicketCreate

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", status_code=201)
def handle_create_ticket(ticket: TicketCreate):
    created = create_ticket(ticket)
    return created


@router.get("")
def list_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
):
    tickets_list = get_all_tickets(status=status, priority=priority, search=search)
    return tickets_list


@router.get("/{ticket_id}")
def get_ticket(ticket_id: str):
    ticket = get_ticket_by_id(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

