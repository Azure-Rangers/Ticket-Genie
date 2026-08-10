from database.crud import get_all_tickets, get_ticket_by_id
from fastapi import APIRouter, HTTPException
from models.ticket import TicketCreate
from services.ticket_service import process_new_ticket

router = APIRouter()


@router.post("/tickets")
def create_ticket(ticket: TicketCreate):
    return process_new_ticket(ticket)


@router.get("/tickets")
def list_tickets():
    return {"tickets": get_all_tickets()}


@router.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int):

    ticket = get_ticket_by_id(ticket_id)

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket
