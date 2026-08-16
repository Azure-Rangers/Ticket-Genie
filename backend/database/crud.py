import os
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
            requester_id=ticket.requester_id,
            classification_status=(
                "Pending AI Triage"
                if getattr(ticket, "confidence", 0.0) == 0.0
                else "Classified"
            ),
            classification_confidence=str(getattr(ticket, "confidence", "")) or None,
            classification_reason=getattr(ticket, "reason", None),
            needs_human_review=getattr(ticket, "needs_human_review", False),
            model_deployment=(
                "mock"
                if os.getenv("USE_MOCK_AI", "false").lower() == "true"
                else os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.2")
            ),
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
    requester_id: Optional[str] = None,
    db: Optional[Session] = None,
) -> List[dict]:
    session = db or SessionLocal()
    should_close = db is None

    try:
        query = session.query(TicketDB)

        if requester_id:
            query = query.filter(
                func.lower(TicketDB.requester_id) == requester_id.lower().strip()
            )

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
        import uuid

        from database.models_db import TicketCommentDB

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


def get_ticket_comments(ticket_id: str, db: Optional[Session] = None) -> List[dict]:
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
        import uuid

        from database.models_db import DepartmentDB

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
                {
                    "name": "Upper Executive Management",
                    "queue_name": "Upper Management - Leave Approval",
                },
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
        import uuid

        from database.models_db import DepartmentUserDB

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
        leave_keywords = [
            "leave",
            "pto",
            "vacation",
            "medical",
            "parental",
            "bereavement",
            "sick",
        ]
        query = session.query(TicketDB)

        conditions = [
            func.lower(TicketDB.category).like(f"%{kw}%") for kw in leave_keywords
        ]
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
        resolved_count = sum(
            1 for t in all_tickets if (t.status or "").lower() == "resolved"
        )
        auto_resolved_count = sum(
            1 for t in all_tickets if getattr(t, "auto_resolved", False)
        )

        by_category = {}
        by_department = {}
        for t in all_tickets:
            cat = t.category or "Other"
            dept = t.department or "IT Team"
            by_category[cat] = by_category.get(cat, 0) + 1
            by_department[dept] = by_department.get(dept, 0) + 1

        auto_res_rate = (
            round((auto_resolved_count / total_count * 100), 1)
            if total_count > 0
            else 40.0
        )

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


# ---------------------------------------------------------------------------
# Announcements CRUD
# ---------------------------------------------------------------------------


def get_announcements(db: Optional[Session] = None) -> List[dict]:
    session = db or SessionLocal()
    should_close = db is None

    try:
        from database.models_db import AnnouncementDB

        records = (
            session.query(AnnouncementDB)
            .order_by(AnnouncementDB.createdAt.desc())
            .all()
        )
        if not records:
            # Seed standard announcements
            now_str = datetime.now().isoformat()
            defaults = [
                AnnouncementDB(
                    id="anc-1",
                    title="System Maintenance Notice",
                    content="Scheduled infrastructure maintenance on Saturday at 2 AM EST.",
                    category="System Alert",
                    author="IT Ops",
                    createdAt=now_str,
                ),
                AnnouncementDB(
                    id="anc-2",
                    title="New HR Policy Handbook Released",
                    content="Please review the updated employee handbook for 2026.",
                    category="HR Announcement",
                    author="HR Relations",
                    createdAt=now_str,
                ),
            ]
            for d in defaults:
                session.add(d)
            session.commit()
            records = (
                session.query(AnnouncementDB)
                .order_by(AnnouncementDB.createdAt.desc())
                .all()
            )

        return [r.to_dict() for r in records]
    finally:
        if should_close:
            session.close()


def create_announcement(
    title: str,
    content: str,
    category: str = "General Alert",
    author: str = "Admin Operations",
    db: Optional[Session] = None,
) -> dict:
    session = db or SessionLocal()
    should_close = db is None

    try:
        import uuid

        from database.models_db import AnnouncementDB

        anc_id = f"anc-{uuid.uuid4().hex[:8]}"
        now_str = datetime.now().isoformat()

        anc = AnnouncementDB(
            id=anc_id,
            title=title,
            content=content,
            category=category,
            author=author,
            createdAt=now_str,
        )
        session.add(anc)
        session.commit()
        session.refresh(anc)
        return anc.to_dict()
    finally:
        if should_close:
            session.close()


def delete_announcement(anc_id: str, db: Optional[Session] = None) -> bool:
    session = db or SessionLocal()
    should_close = db is None

    try:
        from database.models_db import AnnouncementDB

        anc = session.query(AnnouncementDB).filter(AnnouncementDB.id == anc_id).first()
        if anc:
            session.delete(anc)
            session.commit()
            return True
        return False
    finally:
        if should_close:
            session.close()


# ---------------------------------------------------------------------------
# Notifications CRUD
# ---------------------------------------------------------------------------


def get_notifications(
    user_id: str = "user", db: Optional[Session] = None
) -> List[dict]:
    session = db or SessionLocal()
    should_close = db is None

    try:
        from database.models_db import NotificationDB

        records = (
            session.query(NotificationDB)
            .filter(
                or_(NotificationDB.user_id == user_id, NotificationDB.user_id == "all")
            )
            .order_by(NotificationDB.createdAt.desc())
            .all()
        )

        if not records:
            now_str = datetime.now().isoformat()
            defaults = [
                NotificationDB(
                    id="notif-1",
                    user_id="all",
                    title="Ticket Updated",
                    message="Your ticket HD-1025 status has been updated to In Progress.",
                    is_read=False,
                    createdAt=now_str,
                ),
                NotificationDB(
                    id="notif-2",
                    user_id="all",
                    title="New Announcement",
                    message="System Maintenance Notice has been published.",
                    is_read=False,
                    createdAt=now_str,
                ),
                NotificationDB(
                    id="notif-3",
                    user_id="all",
                    title="Leave Request Approved",
                    message="Your PTO request for next Friday was approved.",
                    is_read=True,
                    createdAt=now_str,
                ),
            ]
            for d in defaults:
                session.add(d)
            session.commit()
            records = (
                session.query(NotificationDB)
                .order_by(NotificationDB.createdAt.desc())
                .all()
            )

        return [r.to_dict() for r in records]
    finally:
        if should_close:
            session.close()


def create_notification(
    title: str, message: str, user_id: str = "all", db: Optional[Session] = None
) -> dict:
    session = db or SessionLocal()
    should_close = db is None

    try:
        import uuid

        from database.models_db import NotificationDB

        notif_id = f"notif-{uuid.uuid4().hex[:8]}"
        now_str = datetime.now().isoformat()

        notif = NotificationDB(
            id=notif_id,
            user_id=user_id,
            title=title,
            message=message,
            is_read=False,
            createdAt=now_str,
        )
        session.add(notif)
        session.commit()
        session.refresh(notif)
        return notif.to_dict()
    finally:
        if should_close:
            session.close()


def mark_notification_read(notif_id: str, db: Optional[Session] = None) -> bool:
    session = db or SessionLocal()
    should_close = db is None

    try:
        from database.models_db import NotificationDB

        notif = (
            session.query(NotificationDB).filter(NotificationDB.id == notif_id).first()
        )
        if notif:
            notif.is_read = True
            session.commit()
            return True
        return False
    finally:
        if should_close:
            session.close()


# ---------------------------------------------------------------------------
# Onboarding & Visas CRUD
# ---------------------------------------------------------------------------


def get_onboarding_records(db: Optional[Session] = None) -> List[dict]:
    session = db or SessionLocal()
    should_close = db is None

    try:
        from database.models_db import OnboardingDB

        records = (
            session.query(OnboardingDB).order_by(OnboardingDB.createdAt.desc()).all()
        )
        if not records:
            now_str = datetime.now().isoformat()
            defaults = [
                OnboardingDB(
                    id="onb-101",
                    employee_name="Aarav Sharma",
                    role="Senior Software Engineer",
                    department="IT Engineering",
                    visa_status="H-1B Active",
                    start_date="2026-09-01",
                    status="Completed",
                    createdAt=now_str,
                ),
                OnboardingDB(
                    id="onb-102",
                    employee_name="Elena Rostova",
                    role="Product Designer",
                    department="UX Design",
                    visa_status="OPT STEM",
                    start_date="2026-09-15",
                    status="In Progress",
                    createdAt=now_str,
                ),
                OnboardingDB(
                    id="onb-103",
                    employee_name="Marcus Vance",
                    role="Data Analyst",
                    department="HR Analytics",
                    visa_status="TN Visa",
                    start_date="2026-10-01",
                    status="Pending Documents",
                    createdAt=now_str,
                ),
            ]
            for d in defaults:
                session.add(d)
            session.commit()
            records = (
                session.query(OnboardingDB)
                .order_by(OnboardingDB.createdAt.desc())
                .all()
            )

        return [r.to_dict() for r in records]
    finally:
        if should_close:
            session.close()


def create_onboarding_record(
    employee_name: str,
    role: str,
    department: str,
    visa_status: str = "H1-B",
    start_date: str = "2026-09-01",
    status: str = "In Progress",
    db: Optional[Session] = None,
) -> dict:
    session = db or SessionLocal()
    should_close = db is None

    try:
        import uuid

        from database.models_db import OnboardingDB

        onb_id = f"onb-{uuid.uuid4().hex[:6]}"
        now_str = datetime.now().isoformat()

        rec = OnboardingDB(
            id=onb_id,
            employee_name=employee_name,
            role=role,
            department=department,
            visa_status=visa_status,
            start_date=start_date,
            status=status,
            createdAt=now_str,
        )
        session.add(rec)
        session.commit()
        session.refresh(rec)
        return rec.to_dict()
    finally:
        if should_close:
            session.close()


def update_onboarding_status(
    rec_id: str, new_status: str, db: Optional[Session] = None
) -> Optional[dict]:
    session = db or SessionLocal()
    should_close = db is None

    try:
        from database.models_db import OnboardingDB

        rec = session.query(OnboardingDB).filter(OnboardingDB.id == rec_id).first()
        if rec:
            rec.status = new_status
            session.commit()
            session.refresh(rec)
            return rec.to_dict()
        return None
    finally:
        if should_close:
            session.close()


# ---------------------------------------------------------------------------
# User Profile CRUD
# ---------------------------------------------------------------------------


def get_user_profile(user_id: str = "usr-1", db: Optional[Session] = None) -> dict:
    session = db or SessionLocal()
    should_close = db is None

    try:
        from database.models_db import UserProfileDB

        user = session.query(UserProfileDB).filter(UserProfileDB.id == user_id).first()
        if not user:
            user = UserProfileDB(
                id=user_id,
                name="Nishita",
                email="nishita@ticketgenie.com",
                role="Employee",
                department="HR & Operations",
                phone="+1 (555) 019-2834",
                avatar="NM",
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        return user.to_dict()
    finally:
        if should_close:
            session.close()


def update_user_profile(
    user_id: str = "usr-1",
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    department: Optional[str] = None,
    db: Optional[Session] = None,
) -> dict:
    session = db or SessionLocal()
    should_close = db is None

    try:
        from database.models_db import UserProfileDB

        user = session.query(UserProfileDB).filter(UserProfileDB.id == user_id).first()
        if not user:
            user = UserProfileDB(
                id=user_id,
                name=name or "Nishita",
                email=email or "nishita@ticketgenie.com",
            )
            session.add(user)

        if name:
            user.name = name
        if email:
            user.email = email
        if phone:
            user.phone = phone
        if department:
            user.department = department

        session.commit()
        session.refresh(user)
        return user.to_dict()
    finally:
        if should_close:
            session.close()
