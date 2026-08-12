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


def test_list_tickets() -> None:
    response = client.get("/api/tickets")
    assert response.status_code == 200
    tickets = response.json()
    assert isinstance(tickets, list)
    assert len(tickets) >= 5


def test_create_ticket() -> None:
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
    assert created["id"].startswith("HD-")
    assert created["title"] == payload["title"]
    assert created["status"] == "Open"


def test_genie_chat() -> None:
    payload = {"message": "How do I check my payroll statement?"}
    response = client.post("/api/genie/chat", json=payload)
    assert response.status_code == 200
    reply = response.json()
    assert "reply" in reply
    assert "Payroll" in reply["reply"] or "payroll" in reply["reply"]

