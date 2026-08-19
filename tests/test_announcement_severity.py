from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)
client.headers["Authorization"] = (
    "Bearer eyJhbGciOiAiUlMyNTYiLCAidHlwIjogIkpXVCJ9.eyJvaWQiOiAiZGMzYjU2ZTktOTI4MC00MGRjLThkNzMtOThiZmQ4MWZkZDZhIiwgImVtYWlsIjogIkFkbWluMUB2aWduZXNocXVhZHJhbnRvdXRsb29rLm9ubWljcm9zb2Z0LmNvbSIsICJuYW1lIjogIkFkbWluIFVzZXIiLCAicm9sZSI6ICJTdXBlciBBZG1pbiIsICJleHAiOiAyNTM0MDIzMDA3OTl9.mock"
)


def test_get_latest_announcement_with_severity() -> None:
    res = client.get("/api/announcements/latest")
    assert res.status_code == 200
    data = res.json()
    assert "announcement" in data
    assert "severity" in data
    if data["announcement"]:
        sev = data["severity"]
        assert sev["level"] in ["critical", "warning", "info"]
        assert "label" in sev
        assert "color_class" in sev
        assert "icon" in sev


def test_evaluate_announcement_severity_critical() -> None:
    payload = {
        "title": "Emergency Data Center Power Outage",
        "content": "All core database clusters are down due to an emergency outage. Incident response active.",
        "category": "Incident Alert",
    }
    res = client.post("/api/announcements/severity", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["level"] == "critical"
    assert data["label"] == "CRITICAL ALERT"
    assert data["color_class"] == "severity-critical"


def test_evaluate_announcement_severity_warning() -> None:
    payload = {
        "title": "Scheduled VPN Server Maintenance",
        "content": "Routine maintenance and patch upgrade will occur this Saturday at 2 AM.",
        "category": "System Maintenance",
    }
    res = client.post("/api/announcements/severity", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["level"] == "warning"
    assert data["label"] == "SYSTEM NOTICE"
    assert data["color_class"] == "severity-warning"


def test_evaluate_announcement_severity_info() -> None:
    payload = {
        "title": "Annual Company Picnic & Summer Townhall",
        "content": "Join us next Friday for the annual corporate celebration and product showcase.",
        "category": "Company Event",
    }
    res = client.post("/api/announcements/severity", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["level"] == "info"
    assert data["label"] == "ANNOUNCEMENT"
    assert data["color_class"] == "severity-info"
