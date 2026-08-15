"""Integration tests for POST /tickets calling the AI classifier end-to-end.

Verifies that a ticket submitted WITHOUT a department is classified by
classify_ticket() (in mock mode) and that the AI-generated department,
category, priority, confidence, reason, and needs_human_review values are
present on both the create response and a subsequent GET.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _mock_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("USE_MOCK_AI", "true")
    monkeypatch.delenv("AI_CONFIDENCE_THRESHOLD", raising=False)


def _create_ticket(title: str, description: str) -> dict:
    payload = {"title": title, "description": description}
    assert "department" not in payload
    response = client.post("/tickets", json=payload)
    assert response.status_code == 200
    return response.json()["ticket"]


def _assert_full_ai_shape(ticket: dict) -> None:
    assert ticket["priority"] in {"Low", "Medium", "High", "Critical"}
    assert isinstance(ticket["confidence"], float)
    assert 0.0 <= ticket["confidence"] <= 1.0
    assert isinstance(ticket["reason"], str) and ticket["reason"]
    assert isinstance(ticket["needs_human_review"], bool)


def test_it_ticket_is_classified_without_department() -> None:
    ticket = _create_ticket(
        "Login issue",
        "My account is locked and I cannot log in.",
    )
    assert ticket["department"] == "IT Team"
    assert ticket["category"] == "Identity and Access Management"
    _assert_full_ai_shape(ticket)


def test_accounting_ticket_is_classified_without_department() -> None:
    ticket = _create_ticket(
        "Reimbursement issue",
        "My reimbursement has not been paid.",
    )
    assert ticket["department"] == "Accounting Team"
    assert ticket["category"] == "Reimbursement Requests"
    _assert_full_ai_shape(ticket)


def test_workplace_ticket_is_classified_without_department() -> None:
    ticket = _create_ticket(
        "Badge issue",
        "My building badge stopped working.",
    )
    assert ticket["department"] == "Workplace Operations Team"
    assert ticket["category"] == "Badge Registration"
    _assert_full_ai_shape(ticket)


def test_hr_ticket_is_classified_without_department() -> None:
    ticket = _create_ticket(
        "Benefits question",
        "I have a question about employee benefits.",
    )
    assert ticket["department"] == "HR Team"
    assert ticket["category"] == "Benefits Inquiries"
    _assert_full_ai_shape(ticket)


def test_critical_ticket_is_classified_without_department() -> None:
    ticket = _create_ticket(
        "Company outage",
        "Employees across the entire company cannot access internal systems.",
    )
    assert ticket["priority"] == "Critical"
    _assert_full_ai_shape(ticket)


def test_completed_ticket_is_saved_and_retrievable_with_ai_fields() -> None:
    created = _create_ticket("Laptop request", "I need a new laptop for development work.")
    ticket_id = created["ticket_id"]

    response = client.get(f"/tickets/{ticket_id}")
    assert response.status_code == 200

    fetched = response.json()
    assert fetched["department"] == created["department"]
    assert fetched["category"] == created["category"]
    assert fetched["priority"] == created["priority"]
    assert fetched["confidence"] == created["confidence"]
    assert fetched["reason"] == created["reason"]
    assert fetched["needs_human_review"] == created["needs_human_review"]


def test_client_supplied_department_is_overridden_by_ai() -> None:
    response = client.post(
        "/tickets",
        json={
            "title": "Login issue",
            "description": "My account is locked and I cannot log in.",
            "department": "Upper Management",
        },
    )
    assert response.status_code == 200
    ticket = response.json()["ticket"]
    assert ticket["department"] == "IT Team"
