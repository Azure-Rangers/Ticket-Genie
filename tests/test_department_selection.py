"""
Tests verifying that selecting a department when creating or transferring tickets
is fully respected and persisted across all supported departments.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)
client.headers["Authorization"] = (
    "Bearer eyJhbGciOiAiUlMyNTYiLCAidHlwIjogIkpXVCJ9.eyJvaWQiOiAiZGMzYjU2ZTktOTI4MC00MGRjLThkNzMtOThiZmQ4MWZkZDZhIiwgImVtYWlsIjogIkFkbWluMUB2aWduZXNocXVhZHJhbnRvdXRsb29rLm9ubWljcm9zb2Z0LmNvbSIsICJuYW1lIjogIkFkbWluIFVzZXIiLCAicm9sZSI6ICJBZG1pbiIsICJleHAiOiAyNTM0MDIzMDA3OTl9.mock"
)


@pytest.fixture(autouse=True)
def _mock_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("USE_MOCK_AI", "true")


@pytest.mark.parametrize(
    "selected_dept",
    [
        "HR Team",
        "Accounting Team",
        "Workplace Operations Team",
        "IT Team",
        "Upper Management",
    ],
)
def test_explicit_department_selection_on_ticket_creation(selected_dept: str) -> None:
    response = client.post(
        "/api/tickets",
        json={
            "title": f"Test request for {selected_dept}",
            "description": f"Detailed description for verifying explicit selection of {selected_dept}.",
            "department": selected_dept,
            "priority": "High",
        },
    )
    assert response.status_code == 201
    ticket = response.json()
    assert ticket["department"] == selected_dept
    assert ticket["priority"] == "High"
    assert "Department explicitly selected" in (ticket.get("classification_reason") or "")


def test_transfer_ticket_department() -> None:
    # 1. Create initial ticket in IT Team
    response = client.post(
        "/api/tickets",
        json={
            "title": "Initial IT Department Ticket",
            "description": "Initial setup request created in IT Team for transfer testing.",
            "department": "IT Team",
        },
    )
    assert response.status_code == 201
    ticket_id = response.json()["id"]

    # 2. Transfer to Workplace Operations Team
    update_res = client.put(
        f"/api/tickets/{ticket_id}",
        json={"department": "Workplace Operations Team"},
    )
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["department"] == "Workplace Operations Team"

    # 3. Verify via GET
    get_res = client.get(f"/api/tickets/{ticket_id}")
    assert get_res.status_code == 200
    assert get_res.json()["department"] == "Workplace Operations Team"
