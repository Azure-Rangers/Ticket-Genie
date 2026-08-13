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
    department = Column(String(100), nullable=True, default="IT")
    description = Column(Text, nullable=False)
    date = Column(String(50), nullable=False)
    createdAt = Column(String(50), nullable=False)
    updatedAt = Column(String(50), nullable=True)
    is_anonymous = Column(Boolean, default=False, nullable=False)
    attachment = Column(Text, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "priority": self.priority,
            "status": self.status,
            "department": self.department or "IT",
            "description": self.description,
            "date": self.date,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
            "is_anonymous": self.is_anonymous,
            "attachment": self.attachment,
        }
