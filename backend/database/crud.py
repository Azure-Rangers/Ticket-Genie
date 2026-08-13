from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.models_db import TicketDB
from models.ticket import TicketCreate, TicketUpdate


def _generate_next_id(db: Session) -> str:
    highest = 1000
    try:
        records = db.query(TicketDB.id).all()
        for (tid,) in records:
            if tid and tid.startswith("HD-"):
                try:
                    num = int(tid.replace("HD-", ""))
                    if num > highest:
                        highest = num
                except ValueError:
                    pass
    except Exception:
        pass
    return f"HD-{highest + 1}"


def create_ticket(ticket: TicketCreate, db: Optional[Session] = None) -> dict:
    session = db or SessionLocal()
    should_close = db is None

    try:
        now = datetime.now()
        now_str = now.isoformat()
        date_str = now.strftime("%Y-%m-%d")

        new_id = _generate_next_id(session)

        db_ticket = TicketDB(
            id=new_id,
            title=ticket.title,
            category=ticket.category or "IT Support",
            priority=ticket.priority or "Medium",
            status="Open",
            department=ticket.department or "IT",
            description=ticket.description,
            date=date_str,
            createdAt=now_str,
            is_anonymous=ticket.is_anonymous,
            attachment=ticket.attachment,
        )

        session.add(db_ticket)
        session.commit()
        session.refresh(db_ticket)
        return db_ticket.to_dict()
    finally:
        if should_close:
            session.close()


def get_all_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    db: Optional[Session] = None,
) -> List[dict]:
    session = db or SessionLocal()
    should_close = db is None

    try:
        query = session.query(TicketDB)

        if search:
            s = f"%{search.lower().strip()}%"
            query = query.filter(
                or_(
                    func.lower(TicketDB.title).like(s),
                    func.lower(TicketDB.id).like(s),
                    func.lower(TicketDB.category).like(s),
                    func.lower(TicketDB.description).like(s),
                )
            )

        if status and status.lower() != "all":
            query = query.filter(func.lower(TicketDB.status) == status.lower())

        if priority and priority.lower() != "all":
            query = query.filter(func.lower(TicketDB.priority) == priority.lower())

        results = query.all()
        return [t.to_dict() for t in results]
    finally:
        if should_close:
            session.close()


def get_ticket_by_id(ticket_id: str, db: Optional[Session] = None) -> Optional[dict]:
    session = db or SessionLocal()
    should_close = db is None

    try:
        ticket = (
            session.query(TicketDB)
            .filter(func.lower(TicketDB.id) == ticket_id.lower())
            .first()
        )
        return ticket.to_dict() if ticket else None
    finally:
        if should_close:
            session.close()


def update_ticket(
    ticket_id: str, ticket_update: TicketUpdate, db: Optional[Session] = None
) -> Optional[dict]:
    session = db or SessionLocal()
    should_close = db is None

    try:
        ticket = (
            session.query(TicketDB)
            .filter(func.lower(TicketDB.id) == ticket_id.lower())
            .first()
        )
        if ticket is None:
            return None

        update_data = ticket_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None and hasattr(ticket, field):
                setattr(ticket, field, value)

        ticket.updatedAt = datetime.now().isoformat()
        session.commit()
        session.refresh(ticket)
        return ticket.to_dict()
    finally:
        if should_close:
            session.close()
