from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ChatIntent(str, Enum):
    NAVIGATION = "navigation"
    HOW_TO = "how_to"
    KNOWLEDGE = "knowledge"
    CREATE_TICKET = "create_ticket"
    LEAVE_MANAGEMENT = "leave_management"
    TICKET_STATUS = "ticket_status"
    SUPPORT_ISSUE = "support_issue"
    GENERAL = "general"


class ChatAction(BaseModel):
    """A machine-actionable follow-up the frontend can execute."""

    type: str
    target: Optional[str] = None
    label: Optional[str] = None
    ticket_id: Optional[str] = None


class ChatTurn(BaseModel):
    role: str  # "user" | "assistant"
    message: str


class TicketDraft(BaseModel):
    """
    Mirrors models.ticket.TicketCreate exactly (all fields optional here
    since a draft may still be incomplete). This is never auto-submitted;
    the frontend places it into the existing Standard Request form for the
    user to review, edit, and submit via the existing POST /api/tickets flow.
    """

    title: Optional[str] = Field(default=None, max_length=200)
    category: Optional[str] = None
    priority: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None
    preferredDate: Optional[str] = None
    is_anonymous: bool = False
    attachment: Optional[str] = None

    def is_complete(self) -> bool:
        return bool(
            self.title
            and len(self.title) >= 3
            and self.description
            and len(self.description) >= 5
            and self.category
        )


class ChatRequest(BaseModel):
    message: str
    role: Optional[str] = "Employee"
    department: Optional[str] = None
    history: List[ChatTurn] = Field(default_factory=list)
    draft: Optional[TicketDraft] = None
    # Echoes ChatResponse.intent from the previous turn so a follow-up
    # answer (e.g. supplying a missing field) continues the same
    # drafting flow instead of being re-classified from scratch.
    active_intent: Optional[ChatIntent] = None


class ChatResponse(BaseModel):
    message: str
    intent: ChatIntent
    action: Optional[ChatAction] = None
    ticket_draft: Optional[TicketDraft] = None
    missing_fields: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    knowledge_verified: Optional[bool] = None
