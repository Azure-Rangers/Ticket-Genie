"""Main entry point for AI ticket classification.

Coordinates a single AI request (services/ai_service.py) with the
department/category/priority validators (agents/category_agent.py,
agents/priority_agent.py, agents/routing_agent.py) and returns one
validated TicketClassification.

classify_ticket() never raises. Any failure (missing config, Azure error,
malformed output, invalid taxonomy) is turned into a fallback
TicketClassification with needs_human_review=True so callers can always
trust the return value.
"""

from __future__ import annotations

import logging
from typing import Any, Literal, Optional

from agents.routing_agent import validate_routing
from pydantic import BaseModel, Field, model_validator
from services import ai_service

logger = logging.getLogger(__name__)

Department = Literal[
    "HR Team",
    "Accounting Team",
    "Workplace Operations Team",
    "IT Team",
    "Upper Management",
]
Priority = Literal["Low", "Medium", "High", "Critical"]

FALLBACK_DEPARTMENT: Department = "Upper Management"
FALLBACK_CATEGORY = "Other Management Issue"
FALLBACK_PRIORITY: Priority = "Medium"

# Very short tickets rarely carry enough information to classify confidently.
_VAGUE_WORD_COUNT_THRESHOLD = 6

_SENSITIVE_KEYWORDS = (
    "harassment", "discrimination", "assault", "threat", "weapon",
    "lawsuit", "legal action", "safety concern", "security breach",
    "data breach", "self-harm",
)


class TicketClassification(BaseModel):
    department: Department
    category: str = Field(min_length=1, max_length=100)
    priority: Priority
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str = Field(min_length=1, max_length=500)
    needs_human_review: bool

    @model_validator(mode="after")
    def _check_routing(self) -> "TicketClassification":
        errors = validate_routing(self.department, self.category, self.priority)
        if errors:
            raise ValueError("; ".join(errors))
        return self


def _is_vague(title: str, description: str) -> bool:
    word_count = len(f"{title} {description}".split())
    return word_count < _VAGUE_WORD_COUNT_THRESHOLD


def _is_sensitive(title: str, description: str) -> bool:
    text = f"{title} {description}".lower()
    return any(keyword in text for keyword in _SENSITIVE_KEYWORDS)


def _fallback_classification(
    reason: str, priority: Priority = FALLBACK_PRIORITY
) -> TicketClassification:
    return TicketClassification(
        department=FALLBACK_DEPARTMENT,
        category=FALLBACK_CATEGORY,
        priority=priority,
        confidence=0.0,
        reason=reason,
        needs_human_review=True,
    )


def classify_ticket(
    title: str,
    description: str,
    context: Optional[dict[str, Any]] = None,
) -> TicketClassification:
    """Classify a ticket into department, category, and priority.

    `context` is any optional structured ticket data already available in
    the backend (e.g. requester role, location) that may help classification.
    Never raises — on failure, returns a fallback result flagged for
    human review.
    """
    if not title or not title.strip() or not description or not description.strip():
        return _fallback_classification(
            "Ticket title/description was empty; classification could not be trusted."
        )


    try:
        raw_result = ai_service.get_ai_classification(title, description, context)
    except ai_service.AIServiceError as exc:
        logger.warning("AI classification request failed: %s", exc)
        return _fallback_classification(f"AI classification unavailable: {exc}")
    except Exception:
        logger.exception("Unexpected error calling AI classification service.")
        return _fallback_classification(
            "AI classification unavailable due to an unexpected error."
        )

    if not isinstance(raw_result, dict):
        logger.error(
            "AI classification returned a non-dict result: %r", type(raw_result)
        )
        return _fallback_classification("AI classification returned an invalid result.")

    try:
        classification = TicketClassification(**raw_result)
    except Exception as exc:
        logger.error("AI classification output failed validation: %s", exc)
        return _fallback_classification(
            "AI classification output was invalid and could not be used."
        )

    needs_review = (
        classification.needs_human_review
        or classification.confidence < ai_service.get_confidence_threshold()
        or _is_vague(title, description)
        or _is_sensitive(title, description)
    )

    if needs_review and not classification.needs_human_review:
        classification = classification.model_copy(update={"needs_human_review": True})

    return classification
