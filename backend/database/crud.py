from models.ticket import TicketCreate

tickets = []


def create_ticket(ticket: TicketCreate):

    ticket_record = {
        "ticket_id": len(tickets) + 1,
        **ticket.model_dump()
    }

    tickets.append(ticket_record)

    return {
        "message": "Ticket saved successfully!",
        "ticket": ticket_record
    }


def get_all_tickets():
    return tickets


def get_ticket_by_id(ticket_id: int):

    for ticket in tickets:
        if ticket["ticket_id"] == ticket_id:
            return ticket

    return None