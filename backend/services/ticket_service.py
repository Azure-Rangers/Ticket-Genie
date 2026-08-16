from typing import Optional

from sqlalchemy.orm import Session

from agents.category_agent import is_valid_department
from agents.orchestrator import classify_ticket
from database.crud import create_ticket
from models.ticket import CompletedTicket, TicketCreate

_EXCLUDED_FIELDS = {"department", "category", "priority", "department_override"}


def process_new_ticket(ticket: TicketCreate, db: Optional[Session] = None):
    # Deterministic routing bypass: when the caller (currently only the
    # Leave Management form) supplies a validated department_override,
    # that department is used as-is and classify_ticket() is never called
    # for department/category - a hard business rule requires Leave
    # Management to route to Upper Management regardless of what an AI
    # classifier would have said about the ticket text. Priority stays a
    # fixed, deterministic default rather than AI-derived for the same
    # reason.
    if ticket.department_override and is_valid_department(ticket.department_override):
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
