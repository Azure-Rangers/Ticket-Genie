from datetime import datetime
from typing import Optional

from models.ticket import TicketCreate

# Seed mock ticket dataset matching frontend schema
tickets = [
    {
        "id": "HD-1024",
        "title": "Payroll Issue",
        "category": "Payroll",
        "priority": "High",
        "status": "In Progress",
        "department": "HR",
        "description": "Having an issue with my latest paycheck.",
        "date": "2026-08-08",
        "createdAt": "2026-08-08T10:00:00",
        "is_anonymous": False,
        "attachment": None,
    },
    {
        "id": "HD-1025",
        "title": "Benefits Question",
        "category": "Benefits",
        "priority": "Medium",
        "status": "Open",
        "department": "HR",
        "description": "I have a question about my medical benefits coverage.",
        "date": "2026-08-07",
        "createdAt": "2026-08-07T10:00:00",
        "is_anonymous": False,
        "attachment": None,
    },
    {
        "id": "HD-1026",
        "title": "Laptop Request",
        "category": "IT Support",
        "priority": "Low",
        "status": "Resolved",
        "department": "IT",
        "description": "Requesting a replacement developer laptop.",
        "date": "2026-08-05",
        "createdAt": "2026-08-05T10:00:00",
        "is_anonymous": False,
        "attachment": None,
    },
    {
        "id": "HD-1027",
        "title": "PTO Request",
        "category": "Time Off",
        "priority": "Medium",
        "status": "Pending",
        "department": "HR",
        "description": "Requesting PTO for upcoming vacation.",
        "date": "2026-08-04",
        "createdAt": "2026-08-04T10:00:00",
        "is_anonymous": False,
        "attachment": None,
    },
    {
        "id": "HD-1028",
        "title": "Expense Reimbursement",
        "category": "Payroll",
        "priority": "Low",
        "status": "Resolved",
        "department": "HR",
        "description": "Submitting travel expense reimbursement request.",
        "date": "2026-08-02",
        "createdAt": "2026-08-02T10:00:00",
        "is_anonymous": False,
        "attachment": None,
    },
]


def _generate_next_id() -> str:
    highest = 1028
    for t in tickets:
        tid = t.get("id", "")
        if tid.startswith("HD-"):
            try:
                num = int(tid.replace("HD-", ""))
                if num > highest:
                    highest = num
            except ValueError:
                pass
    return f"HD-{highest + 1}"


def create_ticket(ticket: TicketCreate):
    now = datetime.now()
    now_str = now.isoformat()
    date_str = now.strftime("%Y-%m-%d")

    new_id = _generate_next_id()

    ticket_record = {
        "id": new_id,
        "title": ticket.title,
        "category": ticket.category or "IT Support",
        "priority": ticket.priority or "Medium",
        "status": "Open",
        "department": ticket.department or "IT",
        "description": ticket.description,
        "date": date_str,
        "createdAt": now_str,
        "is_anonymous": ticket.is_anonymous,
        "attachment": ticket.attachment,
    }

    tickets.insert(0, ticket_record)
    return ticket_record


def get_all_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
):
    result = list(tickets)

    if search:
        s = search.lower().strip()
        result = [
            t
            for t in result
            if s in t["title"].lower()
            or s in t["id"].lower()
            or s in t["category"].lower()
            or s in t["description"].lower()
        ]

    if status and status.lower() != "all":
        result = [t for t in result if t["status"].lower() == status.lower()]

    if priority and priority.lower() != "all":
        result = [t for t in result if t["priority"].lower() == priority.lower()]

    return result


def get_ticket_by_id(ticket_id: str):
    for t in tickets:
        if t["id"].lower() == ticket_id.lower():
            return t
    return None
