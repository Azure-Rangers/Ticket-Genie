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


class RequestType(str, Enum):
    """
    Which of the three existing New Request tabs a ticket_draft is meant
    for: standardRequestTab, anonymousRequestTab, or leaveRequestTab (see
    frontend/employee_NM/new-request.html). This is separate from
    ChatIntent - intent says "the user wants to submit a request";
    request_type says which existing form that request belongs in.
    """

    STANDARD = "standard"
    ANONYMOUS = "anonymous"
    LEAVE_MANAGEMENT = "leave_management"


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


class ChatRequest(BaseModel):
    message: str
    role: Optional[str] = "Employee"
    department: Optional[str] = None
    history: List[ChatTurn] = Field(default_factory=list)
    draft: Optional[TicketDraft] = None
    # Set when the intent is already known without needing the model to
    # (re)classify it - either the user clicked a predefined option
    # (navigation/how-to don't need this; ticket-drafting/status/knowledge
    # buttons do), or this turn continues an in-progress drafting flow by
    # echoing the previous ChatResponse.intent.
    active_intent: Optional[ChatIntent] = None
    # Echo of the previous ChatResponse.request_type, so a continuation
    # turn doesn't have to re-derive (or risk flip-flopping) which of the
    # three forms this draft belongs to.
    active_request_type: Optional[RequestType] = None


class ChatResponse(BaseModel):
    message: str
    intent: ChatIntent
    action: Optional[ChatAction] = None
    request_type: Optional[RequestType] = None
    ticket_draft: Optional[TicketDraft] = None
    missing_fields: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    knowledge_verified: Optional[bool] = None
    # True only once the draft has every required field for its
    # request_type and the frontend should open/prefill the matching form.
    # Never implies auto-submit - the user still must click the existing
    # submit button on that form.
    ready_for_review: bool = False
