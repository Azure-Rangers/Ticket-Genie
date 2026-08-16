from typing import Optional

from sqlalchemy.orm import Session

from agents.orchestrator import classify_ticket
from database.crud import create_ticket
from models.ticket import CompletedTicket, TicketCreate


def process_new_ticket(ticket: TicketCreate, db: Optional[Session] = None):
    classification = classify_ticket(ticket.title, ticket.description)

    completed_ticket = CompletedTicket(
        **ticket.model_dump(exclude={"department", "category", "priority"}),
        department=classification.department,
        category=classification.category,
        priority=classification.priority,
        confidence=classification.confidence,
        reason=classification.reason,
        needs_human_review=classification.needs_human_review,
    )

    return create_ticket(completed_ticket, db=db)
