# backend/agents/chatbot_agent.py

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from models.chatbot import ChatIntent, ChatTurn, RequestType, TicketDraft
from services.ai_service import ai_service as default_ai_service


class ChatActionType(str, Enum):
    RESPOND = "respond"
    NAVIGATE = "navigate"
    SEARCH_KNOWLEDGE = "search_knowledge"
    START_TICKET_DRAFT = "start_ticket_draft"
    ASK_FOLLOWUP = "ask_followup"
    SHOW_TICKET_DRAFT = "show_ticket_draft"
    CHECK_TICKET_STATUS = "check_ticket_status"


class NavigationTarget(str, Enum):
    DASHBOARD = "dashboard"
    NEW_REQUEST = "new_request"
    MY_TICKETS = "my_tickets"
    KNOWLEDGE_BASE = "knowledge_base"
    NOTIFICATIONS = "notifications"
    CHAT_HISTORY = "chat_history"


class ExtractedTicketFields(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    preferred_date: Optional[str] = None
    ticket_id: Optional[str] = None


class ChatbotDecision(BaseModel):
    intent: ChatIntent
    action: ChatActionType
    message: str
    navigation_target: Optional[NavigationTarget] = None
    knowledge_query: Optional[str] = None
    ticket_fields: Optional[ExtractedTicketFields] = None
    missing_fields: List[str] = Field(default_factory=list)
    request_type: Optional[RequestType] = None


CHATBOT_DECISION_PROMPT = """
You are the semantic router for TicketGenie's workplace assistant chatbot.
Read the employee's message (and the conversation so far) and return a
single structured decision. Do not answer company-policy questions
yourself here - that happens in a separate step after authorized
knowledge is retrieved. Just decide what the user wants and extract any
facts they already gave you.

INTENTS (choose exactly one):
- navigation: the user wants to get to a page/feature in the app
  (e.g. "how do I get to my dashboard", "where can I see my open
  requests", "take me to notifications"). Never offer to create a
  ticket for a trivial navigation question.
- how_to: the user wants to know how to do something the app already
  supports through self-service (e.g. "how do I submit a
  reimbursement", "where do I upload a document"). Prefer explaining or
  pointing to the right page over offering a ticket.
- knowledge: the user is asking a company policy / process / factual
  question (e.g. "what is the PTO policy", "how many sick days do I
  get"). This includes pure policy questions about leave.
- support_issue / create_ticket: the user is describing a problem that
  needs a support request, or has explicitly asked to create a ticket.
- leave_management: the user is personally requesting, starting,
  extending, or returning from a leave of absence (medical, parental,
  family, bereavement, PTO/vacation, sick, unpaid, etc). This is a hard
  business rule: ANY personal leave request or "how do I request/take
  X leave" question MUST be classified leave_management, even though it
  looks like a question, because it always needs a Standard Request
  ticket draft. Only classify a leave-related message as `knowledge`
  when the user is asking a general policy question with no personal
  request intent (e.g. "what is the PTO accrual policy").
- ticket_status: the user is asking about the status of a ticket they
  already submitted, whether or not they give a ticket number.
- general: greetings, small talk, or anything that doesn't fit above.

ACTIONS: respond, navigate, search_knowledge, start_ticket_draft,
ask_followup, show_ticket_draft, check_ticket_status.
Pick the action that matches the intent (e.g. knowledge ->
search_knowledge, ticket_status -> check_ticket_status, a leave/support
request that is missing required info -> ask_followup, a complete one ->
show_ticket_draft or start_ticket_draft).

NAVIGATION RULES:
- Only choose from these exact navigation targets: dashboard,
  new_request, my_tickets, knowledge_base, notifications, chat_history.
  Never invent a target or a URL - the backend maps the target to a
  real page.
- If the message doesn't clearly match one of those targets, treat it
  as how_to instead of guessing a navigation target.

TICKET FIELD EXTRACTION RULES (support_issue / create_ticket /
leave_management):
- Only extract facts the user actually stated. Never invent a date,
  category, or detail they did not give you.
- `preferred_date` must be an ISO date (YYYY-MM-DD). If the user gave a
  relative reference ("before Friday", "next Monday", "tomorrow"),
  resolve it relative to today's date, which is provided below. If you
  cannot confidently resolve a date, leave preferred_date null instead
  of guessing. For leave_management, if the user gives a date range
  (e.g. "August 20 to August 28"), preferred_date is the START date -
  still restate the full range (both dates) in `description` so nothing
  is lost, but never invent a second date field.
- `category` must be chosen from the allowed list provided below for
  the current flow (support vs leave), matched by meaning - e.g. a
  laptop problem is "IT & Technology", a request for medical leave is
  "Medical Leave". If nothing fits confidently, leave it null.
- `description` should restate what the user told you in their own
  words - do not add details they did not provide.
- missing_fields should list, in plain language, only what is still
  genuinely needed to complete the ticket (e.g. "a bit more detail
  about the issue", "which type of leave", "the start date"). Never
  list something the user (or the existing draft, shown below) already
  gave you.

TICKET STATUS:
- If the user gives a ticket number (e.g. "HD-1024", "ticket 1024"),
  put it in ticket_fields.ticket_id exactly as given.

REQUEST TYPE (only meaningful for create_ticket / support_issue /
leave_management - leave it null for every other intent):
The product has exactly three request forms - decide which existing one
this belongs in:
- leave_management: whenever intent is leave_management. This is fixed by
  a hard business rule downstream regardless of what you put here, but
  set it anyway for clarity.
- anonymous: the user explicitly asks for the request to be anonymous,
  says they don't want their name/identity attached, or explicitly says
  they want to use the Anonymous Request option. Never choose this just
  because a topic is sensitive - the user has to actually ask for
  anonymity.
- standard: an actual support/workplace request where the user has not
  asked for anonymity.
If intent is create_ticket or support_issue and you cannot confidently
tell standard from anonymous from what's been said so far, leave
request_type null and use action=ask_followup with a short message
asking which one they want (Standard Request or Anonymous Request) - do
not guess.

For sensitive workplace issues (e.g. harassment, conflict, safety), stay
neutral and factual in `description` and do not editorialize - and never
assume the user wants anonymity unless they say so.

Never fabricate company policy, ticket data, or URLs. Keep `message`
short, professional, and appropriate for the chosen action (e.g. for
ask_followup, `message` IS the follow-up question to show the user).
"""


def _format_history(history: List[ChatTurn]) -> str:
    if not history:
        return "(none)"
    lines = [f"{turn.role}: {turn.message}" for turn in history]
    return "\n".join(lines)


def _format_draft(draft: Optional[TicketDraft]) -> str:
    if draft is None:
        return "(no draft yet)"
    fields = draft.model_dump(exclude_none=True, exclude_defaults=True)
    if not fields:
        return "(no draft yet)"
    return ", ".join(f"{key}={value}" for key, value in fields.items())


def decide(
    message: str,
    *,
    history: List[ChatTurn] = None,
    existing_draft: Optional[TicketDraft] = None,
    known_intent: Optional[ChatIntent] = None,
    standard_categories: List[str],
    leave_types: List[str],
    ai_service=default_ai_service,
) -> ChatbotDecision:
    history = history or []
    today = datetime.now().strftime("%Y-%m-%d (%A)")

    known_intent_line = (
        f"The intent for this turn is already fixed as `{known_intent.value}` "
        "(the user picked a predefined option or is continuing that flow) - "
        "keep that intent, and focus on extracting fields / composing the "
        "right follow-up or response for it."
        if known_intent
        else "The intent is not yet known - classify it from the message."
    )

    user_content = f"""
Today's date: {today}

{known_intent_line}

Allowed support-ticket categories: {", ".join(standard_categories)}
Allowed leave types: {", ".join(leave_types)}

Conversation so far:
{_format_history(history)}

Current ticket draft (already-known fields - do not re-ask for these):
{_format_draft(existing_draft)}

Latest user message:
{message}
"""

    return ai_service.generate(
        system_prompt=CHATBOT_DECISION_PROMPT,
        user_content=user_content,
        response_model=ChatbotDecision,
    )
