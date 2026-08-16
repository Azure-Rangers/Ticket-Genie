from typing import Optional

from opentelemetry import trace
from sqlalchemy.orm import Session

from agents.category_agent import is_valid_department
from agents.orchestrator import classify_ticket
from database.crud import create_ticket
from models.ticket import CompletedTicket, TicketCreate

_EXCLUDED_FIELDS = {"department", "category", "priority", "department_override"}

tracer = trace.get_tracer("ticketgenie.services.ticket")


def process_new_ticket(ticket: TicketCreate, db: Optional[Session] = None):
    with tracer.start_as_current_span("ticket_service.process_new_ticket") as span:
        span.set_attribute("service.name", "ticket_service")
        span.set_attribute("service.method", "process_new_ticket")
        span.set_attribute("ticket.title", ticket.title)

        # Leave Management deterministic routing override
        if ticket.department_override and is_valid_department(ticket.department_override):
            span.set_attribute("ticket.assigned_department", ticket.department_override)
            span.set_attribute("ticket.assigned_category", ticket.category or "Other")
            span.set_attribute("ticket.assigned_priority", ticket.priority or "Medium")

            completed_ticket = CompletedTicket(
                **ticket.model_dump(exclude=_EXCLUDED_FIELDS),
                department=ticket.department_override,
                category=ticket.category or "Other",
                priority=ticket.priority or "Medium",
                confidence=1.0,
                reason="Deterministic routing rule: Leave Management always routes to Upper Management.",
                needs_human_review=False,
            )

            return create_ticket(completed_ticket, db=db)

        classification = classify_ticket(ticket.title, ticket.description)

        span.set_attribute("ticket.assigned_department", classification.department)
        span.set_attribute("ticket.assigned_category", classification.category)
        span.set_attribute("ticket.assigned_priority", classification.priority)

        completed_ticket = CompletedTicket(
            **ticket.model_dump(exclude=_EXCLUDED_FIELDS),
            department=classification.department,
            category=classification.category,
            priority=classification.priority,
            confidence=classification.confidence,
            reason=classification.reason,
            needs_human_review=classification.needs_human_review,
        )

        return create_ticket(completed_ticket, db=db)