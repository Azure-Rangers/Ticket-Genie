from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


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

    def fake_process_ticket_with_ai(
        title: str,
        description: str,
    ) -> dict:
        return {
            "category": {
                "category": "IT",
                "confidence": 0.99,
                "rationale": "VPN access issues belong to IT.",
            },
            "priority": {
                "priority": "High",
                "confidence": 0.95,
                "rationale": "Remote access is blocked.",
                "needs_human_review": False,
            },
            "summary": {
                "summary": "Employee cannot connect to the company VPN.",
                "requested_action": "Restore VPN access.",
                "key_facts": [
                    "VPN connection is unavailable",
                ],
                "missing_information": [],
            },
            "routing": {
                "destination": "IT",
                "queue": "IT - Service Desk",
                "escalation_required": False,
                "rationale": "Standard VPN support request.",
            },
            "suggested_response": {
                "message": "Thanks for reporting the VPN issue.",
                "suggested_actions": [],
                "safety_notice_required": False,
            },
        }

    monkeypatch.setattr(
        "services.ticket_service.process_ticket_with_ai",
        fake_process_ticket_with_ai,
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
    assert created["category"] == "IT"
    assert created["priority"] == "High"
    assert created["department"] == "IT"

    # Verify GET by ID.
    get_res = client.get(f"/api/tickets/{ticket_id}")

    assert get_res.status_code == 200

    ticket = get_res.json()

    assert ticket["id"] == ticket_id
    assert ticket["category"] == "IT"
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
