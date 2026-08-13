"""Allowed department/category taxonomy for ticket classification.

This is the single source of truth for which categories belong to which
department. The AI classifier is not allowed to invent labels outside of
this list.
"""

from __future__ import annotations

ALLOWED_CATEGORIES: dict[str, list[str]] = {
    "HR Team": [
        "Employee Relationships",
        "Onboarding and Offboarding",
        "Benefits Inquiries",
        "Other HR Request",
    ],
    "Accounting Team": [
        "Company Card Management",
        "Reimbursement Requests",
        "Business Development Management",
        "Other Accounting Request",
    ],
    "Workplace Operations Team": [
        "Maintenance",
        "Badge Registration",
        "Office Equipment Issues",
        "Other Workplace Request",
    ],
    "IT Team": [
        "Laptop Requests",
        "Identity and Access Management",
        "Software Licensing",
        "Other IT Request",
    ],
    "Upper Management": [
        "High-Impact Company Conflict",
        "Executive Review",
        "Company-Wide Issue",
        "Other Management Issue",
    ],
}

ALLOWED_DEPARTMENTS: list[str] = list(ALLOWED_CATEGORIES.keys())


def is_valid_department(department: str) -> bool:
    """Return True if `department` is one of the allowed departments."""
    return department in ALLOWED_CATEGORIES


def is_valid_category(department: str, category: str) -> bool:
    """Return True if `category` is a valid category for `department`."""
    if not is_valid_department(department):
        return False
    return category in ALLOWED_CATEGORIES[department]


def get_categories_for_department(department: str) -> list[str]:
    """Return the allowed categories for `department`, or [] if unknown."""
    return list(ALLOWED_CATEGORIES.get(department, []))
