from __future__ import annotations

import os


def get_backend_url() -> str:
    """Retrieve backend API base URL from environment variable."""
    return os.getenv("BACKEND_API_URL", "http://localhost:8000").rstrip("/")


def get_sample_tickets() -> list[dict[str, str]]:
    return [
        {"id": "TCK-1001", "title": "VPN access request", "status": "open"},
        {"id": "TCK-1002", "title": "Laptop replacement", "status": "in_progress"},
        {"id": "TCK-1003", "title": "Password reset", "status": "resolved"},
    ]


def summarize_ticket_queue(tickets: list[dict[str, str]]) -> dict[str, int]:
    summary = {"open": 0, "in_progress": 0, "resolved": 0}

    for ticket in tickets:
        status = ticket.get("status", "")
        if status in summary:
            summary[status] += 1

    return summary
