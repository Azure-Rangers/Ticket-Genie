"""Priority levels and definitions for ticket classification."""

from __future__ import annotations

ALLOWED_PRIORITIES: list[str] = ["Low", "Medium", "High", "Critical"]

PRIORITY_DESCRIPTIONS: dict[str, str] = {
    "Low": (
        "General or informational request. Little business impact. "
        "Work is not blocked. No important deadline."
    ),
    "Medium": (
        "Work is affected, but a workaround exists. Impact is limited. "
        "Should be handled soon."
    ),
    "High": (
        "Important work is blocked, there is serious individual impact, "
        "or an important deadline is approaching. Strongly affects the "
        "employee's ability to work."
    ),
    "Critical": (
        "Safety concern, security incident, serious legal/company risk, "
        "company-wide outage, many employees blocked, or severe "
        "organizational impact. The word 'urgent' by itself does NOT "
        "make a ticket Critical."
    ),
}


def is_valid_priority(priority: str) -> bool:
    """Return True if `priority` is one of the allowed priority levels."""
    return priority in ALLOWED_PRIORITIES
