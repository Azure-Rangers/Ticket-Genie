from models.ticket import TicketCreate
from database.crud import create_ticket


def process_new_ticket(ticket: TicketCreate):

    return create_ticket(ticket)