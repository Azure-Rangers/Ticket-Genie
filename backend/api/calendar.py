"""Leave Calendar Management & .ics Export Router."""

from __future__ import annotations

from fastapi import APIRouter, Response

from database.crud import get_leave_tickets

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/leave-events")
def get_leave_events():
    tickets = get_leave_tickets()
    events = []

    for t in tickets:
        events.append(
            {
                "id": t["id"],
                "title": f"{t['category']}: {t['title']}",
                "start": t.get("date", "2026-08-15"),
                "end": t.get("date", "2026-08-15"),
                "department": t.get("department", "Upper Executive Management"),
                "status": t.get("status", "Open"),
                "color": "#10b981" if t.get("status") == "Approved" else "#f59e0b",
            }
        )

    return events


@router.get("/export.ics")
def export_calendar_ics():
    tickets = get_leave_tickets()
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//TicketGenie//Leave Calendar 1.0//EN",
        "X-WR-CALNAME:Company Leave Calendar",
    ]

    for t in tickets:
        date_str = (t.get("date") or "2026-08-15").replace("-", "")
        ics_lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{t['id']}@ticketgenie.internal",
                f"DTSTAMP:{date_str}T090000Z",
                f"DTSTART;VALUE=DATE:{date_str}",
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
