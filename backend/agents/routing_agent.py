"""Routing validation helpers.

Confirms a (department, category, priority) triple is internally consistent
before a classification result is trusted. This module never touches the
database — it is pure validation logic.
"""

from __future__ import annotations

from agents.category_agent import is_valid_category, is_valid_department
from agents.priority_agent import is_valid_priority


def validate_routing(department: str, category: str, priority: str) -> list[str]:
    """Return a list of human-readable validation errors.

    An empty list means the (department, category, priority) triple is
    valid and consistent.
    """
    errors: list[str] = []

    if not is_valid_department(department):
        errors.append(f"'{department}' is not an allowed department.")
    elif not is_valid_category(department, category):
        errors.append(f"'{category}' is not a valid category for department '{department}'.")

    if not is_valid_priority(priority):
        errors.append(f"'{priority}' is not a valid priority.")

    return errors


def is_valid_routing(department: str, category: str, priority: str) -> bool:
    """Return True if the (department, category, priority) triple is valid."""
    return not validate_routing(department, category, priority)
