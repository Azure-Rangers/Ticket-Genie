from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)
client.headers["Authorization"] = (
    "Bearer eyJhbGciOiAiUlMyNTYiLCAidHlwIjogIkpXVCJ9.eyJvaWQiOiAiZGMzYjU2ZTktOTI4MC00MGRjLThkNzMtOThiZmQ4MWZkZDZhIiwgImVtYWlsIjogIkFkbWluMUB2aWduZXNocXVhZHJhbnRvdXRsb29rLm9ubWljcm9zb2Z0LmNvbSIsICJuYW1lIjogIkFkbWluIFVzZXIiLCAicm9sZSI6ICJTdXBlciBBZG1pbiIsICJleHAiOiAyNTM0MDIzMDA3OTl9.mock"
)


def test_get_upper_management_users() -> None:
    res = client.get("/api/users/upper-management")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0
    names = [u.get("name") for u in data]
    assert any("Greg Davis" in n or "Sarah Jenkins" in n or "Alex Vance" in n for n in names)


def test_submit_leave_request_with_upper_management_assignee() -> None:
    payload = {
        "title": "Leave Request: Paid Time Off (PTO)",
        "description": "Dates: 2026-09-01 to 2026-09-05. Handover Lead: Jane Doe. Vacation time.",
        "category": "Time Off",
        "priority": "Medium",
        "department": "Upper Management",
        "department_override": "Upper Management",
        "assigned_to": "Greg Davis",
    }
    res = client.post("/api/tickets", json=payload)
    assert res.status_code == 201
    ticket = res.json()
    assert ticket["department"] == "Upper Management"
    assert ticket["assigned_to"] == "Greg Davis"

    # Verify fetching ticket preserves assignee
    ticket_id = ticket["id"]
    get_res = client.get(f"/api/tickets/{ticket_id}")
    assert get_res.status_code == 200
    assert get_res.json()["assigned_to"] == "Greg Davis"
