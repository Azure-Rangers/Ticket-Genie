from sqlalchemy.orm import Session

from agents.orchestrator import process_ticket_with_ai
from database.crud import create_ticket
from models.ticket import TicketCreate


def process_new_ticket(ticket: TicketCreate, db: Session):
    """
    Process a new ticket through the AI pipeline before saving it.
    """

    # Run the employee's ticket through all AI agents.
    ai_result = process_ticket_with_ai(
        title=ticket.title,
        description=ticket.description,
    )

    # Extract the values that our current database stores.
    category = ai_result["category"]["category"]
    priority = ai_result["priority"]["priority"]
    department = ai_result["routing"]["destination"]

    # Keep the employee's original ticket information,
    # but overwrite the AI-controlled fields.
    processed_ticket = ticket.model_copy(
        update={
            "category": category,
            "priority": priority,
            "department": department,
        }
    )

    # Save the processed ticket to the database.
    return create_ticket(processed_ticket, db=db)
