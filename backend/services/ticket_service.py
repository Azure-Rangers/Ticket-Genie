from typing import Optional

from opentelemetry import trace
from sqlalchemy.orm import Session

from agents.orchestrator import classify_ticket
from database.crud import create_ticket
from models.ticket import CompletedTicket, TicketCreate

tracer = trace.get_tracer("ticketgenie.services.ticket")


def process_new_ticket(ticket: TicketCreate, db: Optional[Session] = None):
    with tracer.start_as_current_span("ticket_service.process_new_ticket") as span:
        span.set_attribute("service.name", "ticket_service")
        span.set_attribute("service.method", "process_new_ticket")
        span.set_attribute("ticket.title", ticket.title)

        classification = classify_ticket(ticket.title, ticket.description)

        span.set_attribute("ticket.assigned_department", classification.department)
        span.set_attribute("ticket.assigned_category", classification.category)
        span.set_attribute("ticket.assigned_priority", classification.priority)

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
