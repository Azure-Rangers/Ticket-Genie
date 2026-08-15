from sqlalchemy import Boolean, Column, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TicketDB(Base):
    __tablename__ = "tickets"

    id = Column(String(50), primary_key=True, index=True)
    title = Column(String(250), nullable=False)
    category = Column(String(100), nullable=False, default="IT Support")
    priority = Column(String(50), nullable=False, default="Medium")
    status = Column(String(50), nullable=False, default="Open")
    department = Column(String(100), nullable=True, default="IT Team")
    queue = Column(String(100), nullable=True, default="IT - Service Desk")
    description = Column(Text, nullable=False)
    date = Column(String(50), nullable=False)
    createdAt = Column(String(50), nullable=False)
    updatedAt = Column(String(50), nullable=True)
    is_anonymous = Column(Boolean, default=False, nullable=False)
    attachment = Column(Text, nullable=True)
    parent_ticket_id = Column(String(50), nullable=True)
    auto_resolved = Column(Boolean, default=False, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "priority": self.priority,
            "status": self.status,
            "department": self.department or "IT Team",
            "queue": self.queue or "IT - Service Desk",
            "description": self.description,
            "date": self.date,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
            "is_anonymous": self.is_anonymous,
            "attachment": self.attachment,
            "parent_ticket_id": self.parent_ticket_id,
            "auto_resolved": self.auto_resolved,
        }


class TicketCommentDB(Base):
    __tablename__ = "ticket_comments"

    id = Column(String(50), primary_key=True, index=True)
    ticket_id = Column(String(50), index=True, nullable=False)
    sender_id = Column(String(100), nullable=False, default="user")
    sender_role = Column(String(50), nullable=False, default="Employee")
    message = Column(Text, nullable=False)
    createdAt = Column(String(50), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "ticket_id": self.ticket_id,
            "sender_id": self.sender_id,
            "sender_role": self.sender_role,
            "message": self.message,
            "createdAt": self.createdAt,
        }


class DepartmentDB(Base):
    __tablename__ = "departments"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    queue_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    createdAt = Column(String(50), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "queue_name": self.queue_name,
            "description": self.description,
            "createdAt": self.createdAt,
        }


class DepartmentUserDB(Base):
    __tablename__ = "department_users"

    id = Column(String(50), primary_key=True, index=True)
    department_name = Column(String(100), index=True, nullable=False)
    azure_object_id = Column(String(100), index=True, nullable=False)
    role = Column(String(50), nullable=False, default="Member")
    user_email = Column(String(150), nullable=True)
    createdAt = Column(String(50), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "department_name": self.department_name,
            "azure_object_id": self.azure_object_id,
            "role": self.role,
            "user_email": self.user_email,
            "createdAt": self.createdAt,
        }


class KnowledgeChunkDB(Base):
    __tablename__ = "knowledge_chunks"

    id = Column(String(50), primary_key=True, index=True)
    category = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(100), nullable=False, default="Ticketer Dynamic Ingestion")
    createdAt = Column(String(50), nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category,
            "title": self.title,
            "content": self.content,
            "source": self.source,
            "createdAt": self.createdAt,
        }
