from database.crud import create_ticket
from models.ticket import TicketCreate


def process_new_ticket(ticket: TicketCreate):
    return create_ticket(ticket)
