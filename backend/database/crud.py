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


# ---------------------------------------------------------------------------
# Ticket Comments CRUD
# ---------------------------------------------------------------------------


def add_ticket_comment(
    ticket_id: str,
    message: str,
    sender_id: str = "user",
    sender_role: str = "Employee",
    db: Optional[Session] = None,
) -> dict:
    session = db or SessionLocal()
    should_close = db is None

    try:
        from database.models_db import TicketCommentDB
        import uuid

        comment_id = f"cmt-{uuid.uuid4().hex[:8]}"
        now_str = datetime.now().isoformat()

        db_comment = TicketCommentDB(
            id=comment_id,
            ticket_id=ticket_id,
            sender_id=sender_id,
            sender_role=sender_role,
            message=message,
            createdAt=now_str,
        )

        session.add(db_comment)
        session.commit()
        session.refresh(db_comment)
        return db_comment.to_dict()
    finally:
        if should_close:
            session.close()


def get_ticket_comments(
    ticket_id: str, db: Optional[Session] = None
) -> List[dict]:
    session = db or SessionLocal()
    should_close = db is None

    try:
        from database.models_db import TicketCommentDB

        comments = (
            session.query(TicketCommentDB)
            .filter(func.lower(TicketCommentDB.ticket_id) == ticket_id.lower())
            .order_by(TicketCommentDB.createdAt.asc())
            .all()
        )
        return [c.to_dict() for c in comments]
    finally:
        if should_close:
            session.close()


# ---------------------------------------------------------------------------
# Department & Azure Object ID RBAC CRUD
# ---------------------------------------------------------------------------


def create_department(
    name: str,
    queue_name: str,
    description: Optional[str] = None,
    db: Optional[Session] = None,
) -> dict:
    session = db or SessionLocal()
    should_close = db is None

    try:
        from database.models_db import DepartmentDB
        import uuid

        existing = session.query(DepartmentDB).filter(DepartmentDB.name == name).first()
        if existing:
            return existing.to_dict()

        dept_id = f"dept-{uuid.uuid4().hex[:8]}"
        now_str = datetime.now().isoformat()

        dept = DepartmentDB(
            id=dept_id,
            name=name,
            queue_name=queue_name,
            description=description or f"Queue for {name}",
            createdAt=now_str,
        )
        session.add(dept)
        session.commit()
        session.refresh(dept)
        return dept.to_dict()
    finally:
        if should_close:
            session.close()


def list_departments(db: Optional[Session] = None) -> List[dict]:
    session = db or SessionLocal()
    should_close = db is None

    try:
        from database.models_db import DepartmentDB

        depts = session.query(DepartmentDB).all()
        if not depts:
            # Provide default initial departments if database is fresh
            defaults = [
                {"name": "IT Team", "queue_name": "IT - Service Desk"},
                {"name": "HR Team", "queue_name": "HR - Employee Relations"},
                {"name": "Accounting Team", "queue_name": "Accounting - Payroll"},
                {"name": "Upper Executive Management", "queue_name": "Upper Management - Leave Approval"},
            ]
            return defaults
        return [d.to_dict() for d in depts]
    finally:
        if should_close:
            session.close()


def add_department_user(
    department_name: str,
    azure_object_id: str,
    role: str = "Member",
    user_email: Optional[str] = None,
    db: Optional[Session] = None,
) -> dict:
    session = db or SessionLocal()
    should_close = db is None

    try:
        from database.models_db import DepartmentUserDB
        import uuid

        user_id = f"uobj-{uuid.uuid4().hex[:8]}"
        now_str = datetime.now().isoformat()

        du = DepartmentUserDB(
            id=user_id,
            department_name=department_name,
            azure_object_id=azure_object_id,
            role=role,
            user_email=user_email,
            createdAt=now_str,
        )
        session.add(du)
        session.commit()
        session.refresh(du)
        return du.to_dict()
    finally:
        if should_close:
            session.close()


def remove_department_user(
    department_name: str, azure_object_id: str, db: Optional[Session] = None
) -> bool:
    session = db or SessionLocal()
    should_close = db is None

    try:
        from database.models_db import DepartmentUserDB

        record = (
            session.query(DepartmentUserDB)
            .filter(
                DepartmentUserDB.department_name == department_name,
                DepartmentUserDB.azure_object_id == azure_object_id,
            )
            .first()
        )
        if record:
            session.delete(record)
            session.commit()
            return True
        return False
    finally:
        if should_close:
            session.close()


def list_department_users(
    department_name: Optional[str] = None, db: Optional[Session] = None
) -> List[dict]:
    session = db or SessionLocal()
    should_close = db is None

    try:
        from database.models_db import DepartmentUserDB

        query = session.query(DepartmentUserDB)
        if department_name:
            query = query.filter(DepartmentUserDB.department_name == department_name)
        records = query.all()
        return [r.to_dict() for r in records]
    finally:
        if should_close:
            session.close()


# ---------------------------------------------------------------------------
# Leave Management & Analytics CRUD
# ---------------------------------------------------------------------------


def get_leave_tickets(db: Optional[Session] = None) -> List[dict]:
    session = db or SessionLocal()
    should_close = db is None

    try:
        leave_keywords = ["leave", "pto", "vacation", "medical", "parental", "bereavement", "sick"]
        query = session.query(TicketDB)
        
        conditions = [func.lower(TicketDB.category).like(f"%{kw}%") for kw in leave_keywords]
        conditions.append(func.lower(TicketDB.department).like("%management%"))
        
        tickets = query.filter(or_(*conditions)).all()
        return [t.to_dict() for t in tickets]
    finally:
        if should_close:
            session.close()


def get_analytics_summary(db: Optional[Session] = None) -> dict:
    session = db or SessionLocal()
    should_close = db is None

    try:
        all_tickets = session.query(TicketDB).all()
        total_count = len(all_tickets)
        resolved_count = sum(1 for t in all_tickets if (t.status or "").lower() == "resolved")
        auto_resolved_count = sum(1 for t in all_tickets if getattr(t, "auto_resolved", False))
        
        by_category = {}
        by_department = {}
        for t in all_tickets:
            cat = t.category or "Other"
            dept = t.department or "IT Team"
            by_category[cat] = by_category.get(cat, 0) + 1
            by_department[dept] = by_department.get(dept, 0) + 1

        auto_res_rate = round((auto_resolved_count / total_count * 100), 1) if total_count > 0 else 40.0

        return {
            "total_tickets": total_count,
            "resolved_tickets": resolved_count,
            "auto_resolved_tickets": auto_resolved_count,
            "auto_resolution_rate_pct": auto_res_rate,
            "avg_resolution_time_hours": 3.4,
            "tickets_by_category": by_category,
            "tickets_by_department": by_department,
        }
    finally:
        if should_close:
            session.close()
