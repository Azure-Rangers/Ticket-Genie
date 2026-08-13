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


def test_create_and_get_ticket() -> None:
    payload = {
        "title": "VPN Connection Issue",
        "category": "IT Support",
        "priority": "High",
        "department": "IT",
        "description": "Unable to connect to company VPN network from remote location.",
    }
    response = client.post("/api/tickets", json=payload)
    assert response.status_code == 201
    created = response.json()
    ticket_id = created["id"]
    assert ticket_id.startswith("HD-")
    assert created["title"] == payload["title"]
    assert created["status"] == "Open"

    # Verify GET by ID
    get_res = client.get(f"/api/tickets/{ticket_id}")
    assert get_res.status_code == 200
    ticket = get_res.json()
    assert ticket["id"] == ticket_id

    # Verify UPDATE
    update_payload = {"status": "Resolved", "priority": "Low"}
    update_res = client.put(f"/api/tickets/{ticket_id}", json=update_payload)
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
    response = client.post("/api/genie/chat", json=payload)
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
    response = client.put("/api/tickets/HD-9999", json=update_payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"
