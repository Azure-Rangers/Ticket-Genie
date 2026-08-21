"""Leave Calendar Management & .ics Export Router."""

from __future__ import annotations

import re

from fastapi import APIRouter, Depends, Response

from database.crud import get_leave_tickets
from services.jwt_verifier import verify_azure_user

router = APIRouter(prefix="/calendar", tags=["calendar"])


def _leave_dates(ticket: dict) -> tuple[str, str]:
    """Extract the submitted ISO date/range without fabricating calendar dates."""
    text = f"{ticket.get('title') or ''} {ticket.get('description') or ''}"
    dates = re.findall(r"\b\d{4}-\d{2}-\d{2}\b", text)
    fallback = ticket.get("date") or ticket.get("createdAt") or ""
    fallback = str(fallback)[:10]
    start = dates[0] if dates else fallback
    end = dates[1] if len(dates) > 1 else start
    return start, end


@router.get("/leave-events")
def get_leave_events(current_user: dict = Depends(verify_azure_user)):
    tickets = get_leave_tickets()
    events = []

    for t in tickets:
        start, end = _leave_dates(t)
        events.append(
            {
                "id": t["id"],
                "title": t.get("title") or "Leave request",
                "employee": t.get("requester") or "Employee",
                "type": t.get("category") or "Leave",
                "start": start,
                "end": end,
                "department": t.get("department") or "Unassigned",
                "status": t.get("status", "Open"),
                "color": "#10b981" if t.get("status") == "Approved" else "#f59e0b",
            }
        )

    return events


@router.get("/export.ics")
def export_calendar_ics(current_user: dict = Depends(verify_azure_user)):
    tickets = get_leave_tickets()
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//TicketGenie//Leave Calendar 1.0//EN",
        "X-WR-CALNAME:Company Leave Calendar",
    ]

    for t in tickets:
        start, end = _leave_dates(t)
        if not start:
            continue
        start_str = start.replace("-", "")
        end_str = end.replace("-", "")
        ics_lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{t['id']}@ticketgenie.internal",
                f"DTSTAMP:{start_str}T090000Z",
                f"DTSTART;VALUE=DATE:{start_str}",
                f"DTEND;VALUE=DATE:{end_str}",
                f"SUMMARY:[{t.get('status', 'Leave')}] {t['title']}",
                f"DESCRIPTION:Category: {t.get('category')} - Department: {t.get('department')}",
                "END:VEVENT",
            ]
        )

    ics_lines.append("END:VCALENDAR")
    ics_content = "\r\n".join(ics_lines)

    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={"Content-Disposition": "attachment; filename=leave_calendar.ics"},
    )
