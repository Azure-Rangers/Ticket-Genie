from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)
client.headers["Authorization"] = "Bearer eyJhbGciOiAiUlMyNTYiLCAidHlwIjogIkpXVCJ9.eyJvaWQiOiAiZGMzYjU2ZTktOTI4MC00MGRjLThkNzMtOThiZmQ4MWZkZDZhIiwgImVtYWlsIjogIkFkbWluMUB2aWduZXNocXVhZHJhbnRvdXRsb29rLm9ubWljcm9zb2Z0LmNvbSIsICJuYW1lIjogIkFkbWluIFVzZXIiLCAicm9sZSI6ICJTdXBlciBBZG1pbiIsICJleHAiOiAyNTM0MDIzMDA3OTl9.mock"


def test_read_root() -> None:
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "Running"
    assert "message" in data


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "TicketGenie API"


def test_create_and_get_ticket(monkeypatch) -> None:
    """
    Test the ticket API flow without calling the real GPT-5.2 service.

    The AI result is mocked only during this test so CI does not
    require Azure/OpenAI credentials.
    """

    def fake_classify_ticket(title: str, description: str):
        from agents.orchestrator import TicketClassification

        return TicketClassification(
            department="IT Team",
            category="Identity and Access Management",
            priority="High",
            confidence=0.95,
            reason="VPN access issue.",
            needs_human_review=False,
        )

    monkeypatch.setattr(
        "services.ticket_service.classify_ticket",
        fake_classify_ticket,
    )

    payload = {
        "title": "VPN Connection Issue",
        "description": (
            "Unable to connect to company VPN network from remote location."
        ),
    }

    response = client.post(
        "/api/tickets",
        json=payload,
    )

    assert response.status_code == 201

    created = response.json()

    ticket_id = created["id"]

    assert ticket_id.startswith("HD-")
    assert created["title"] == payload["title"]
    assert created["status"] == "Open"

    # Verify the mocked AI output was applied correctly.
    assert created["category"] == "Identity and Access Management"
    assert created["priority"] == "High"
    assert created["department"] == "IT Team"

    # Verify GET by ID.
    get_res = client.get(f"/api/tickets/{ticket_id}")

    assert get_res.status_code == 200

    ticket = get_res.json()

    assert ticket["id"] == ticket_id
    assert ticket["category"] == "Identity and Access Management"
    assert ticket["priority"] == "High"

    # Verify UPDATE.
    update_payload = {
        "status": "Resolved",
        "priority": "Low",
    }

    update_res = client.put(
        f"/api/tickets/{ticket_id}",
        json=update_payload,
    )

    assert update_res.status_code == 200

    updated = update_res.json()

    assert updated["id"] == ticket_id
    assert updated["status"] == "Resolved"
    assert updated["priority"] == "Low"


def test_list_tickets() -> None:
    response = client.get("/api/tickets")

    assert response.status_code == 200

    tickets = response.json()

    assert isinstance(tickets, list)


def test_genie_chat() -> None:
    payload = {"message": "How do I check my payroll statement?"}

    response = client.post(
        "/api/genie/chat",
        json=payload,
    )

    assert response.status_code == 200

    reply = response.json()

    assert "reply" in reply
    assert "Payroll" in reply["reply"] or "payroll" in reply["reply"]


def test_get_ticket_not_found() -> None:
    response = client.get("/api/tickets/HD-9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_update_ticket_not_found() -> None:
    update_payload = {"status": "Resolved"}

    response = client.put(
        "/api/tickets/HD-9999",
        json=update_payload,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_azure_login_admin_check() -> None:
    payload = {
        "azure_object_id": "dc3b56e9-9280-40dc-8d73-98bfd81fdd6a",
        "email": "admin@company.com",
        "name": "Admin User"
    }

    response = client.post("/api/users/azure-login", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert data["azure_object_id"] == "dc3b56e9-9280-40dc-8d73-98bfd81fdd6a"
    assert data["is_admin"] is True
    assert data["role"] in ["Admin", "Super Admin"]

