"""
Chatbot Agent: role-aware workplace assistant.

Routing is done with plain deterministic Python logic (no model call) so a
single user message doesn't fan out into several independent LLM calls.
The Knowledge Agent and Ticket Drafting Agent are invoked as ordinary
service calls from here, not as separate autonomous agents.
"""

import re
from typing import List, Optional

from models.chatbot import ChatAction, ChatIntent, ChatRequest, ChatResponse
from services import ticket_draft_service
from services.knowledge_service import answer_question
from services.role_service import get_allowed_scopes
from services.ticket_draft_service import contains_any_keyword, contains_keyword

PREDEFINED_SUGGESTIONS = [
    "Ask a question",
    "Help me create a ticket",
    "Check my ticket status",
]

_MANAGEMENT_HOME = "pages/management-portal.html"


def _route(employee_page: str, management_page: str = None) -> dict:
    return {"employee": employee_page, "management": management_page or employee_page}


_ROUTES = {
    "dashboard": _route("index.html", _MANAGEMENT_HOME),
    "home": _route("index.html", _MANAGEMENT_HOME),
    "help & support": _route("index.html", _MANAGEMENT_HOME),
    "my tickets": _route("my-tickets.html"),
    "tickets": _route("my-tickets.html"),
    "new request": _route("new-request.html"),
    "knowledge base": _route("knowledge-base.html"),
    "policies": _route("knowledge-base.html"),
    "notifications": _route("notifications.html"),
    "chat history": _route("chat-history.html"),
}

_NAV_VERBS = (
    "access",
    "open",
    "find",
    "get to",
    "navigate",
    "go to",
    "where is",
    "where's",
)

_LEAVE_NOUNS = (
    "medical leave",
    "parental leave",
    "family leave",
    "extended leave",
    "sick leave",
    "maternity leave",
    "paternity leave",
    "bereavement leave",
    "bereavement",
    "personal leave",
    "unpaid leave",
    "leave request",
    "returning from leave",
    "extending leave",
    "pto",
    "time off",
    "vacation",
    "leave",
)

_LEAVE_ACTION_PHRASES = (
    "i need",
    "i want",
    "requesting",
    "request for",
    "request leave",
    "apply for",
    "applying for",
    "need to take",
    "want to take",
    "start my",
    "starting my",
    "extend my",
    "extending my",
    "returning from",
    "return from",
    "how do i request",
    "can i request",
    "need leave",
    "need time off",
)

_POLICY_MARKERS = (
    "what is",
    "what's",
    "policy",
    "how many days",
    "how much",
    "am i eligible",
    "am i entitled",
    "eligib",
    "accrual",
    "how does",
    "explain",
    "what are the rules",
)

_TICKET_STATUS_PHRASES = (
    "ticket status",
    "status of my ticket",
    "where is ticket",
    "check my ticket",
)
_TICKET_ID_PATTERN = re.compile(r"\b(hd-\d+|ticket\s*#?\s*(\d+))\b", re.IGNORECASE)

_CREATE_TICKET_PHRASES = (
    "create a ticket",
    "help me create a ticket",
    "open a ticket",
    "file a ticket",
    "submit a ticket",
    "raise a ticket",
    "start a ticket",
    "create a request",
    "help me create a request",
)

_HOW_TO_PHRASES = ("how do i", "how to", "where do i", "where can i")

_SUPPORT_ISSUE_KEYWORDS = (
    "won't turn on",
    "not working",
    "not paid",
    "hasn't been paid",
    "has not been paid",
    "broken",
    "crashes",
    "crashed",
    "error",
    "cannot access",
    "can't access",
    "unable to",
    "stopped working",
    "issue with",
    "problem with",
    "won't start",
    "not received",
)


def _normalize(message: str) -> str:
    return message.lower().strip()


def _match_route(lowered: str) -> Optional[str]:
    for noun in _ROUTES:
        if contains_keyword(lowered, noun):
            return noun
    return None


def _resolve_route_target(noun: str, role: Optional[str]) -> str:
    routes = _ROUTES[noun]
    is_management = (role or "").strip().lower() == "management"
    return routes["management"] if is_management else routes["employee"]


def _is_leave_intent(lowered: str) -> bool:
    if not contains_any_keyword(lowered, _LEAVE_NOUNS):
        return False

    has_policy_marker = contains_any_keyword(lowered, _POLICY_MARKERS)
    has_action_phrase = contains_any_keyword(lowered, _LEAVE_ACTION_PHRASES)

    if has_policy_marker and not has_action_phrase:
        return False

    return True


def classify_intent(message: str) -> ChatIntent:
    lowered = _normalize(message)

    has_status_phrase = contains_any_keyword(lowered, _TICKET_STATUS_PHRASES)
    if has_status_phrase or _TICKET_ID_PATTERN.search(lowered):
        return ChatIntent.TICKET_STATUS

    if _is_leave_intent(lowered):
        return ChatIntent.LEAVE_MANAGEMENT

    matched_route = _match_route(lowered)
    if matched_route and contains_any_keyword(lowered, _NAV_VERBS):
        return ChatIntent.NAVIGATION

    if contains_any_keyword(lowered, _CREATE_TICKET_PHRASES):
        return ChatIntent.CREATE_TICKET

    if contains_any_keyword(lowered, _POLICY_MARKERS):
        return ChatIntent.KNOWLEDGE

    if contains_any_keyword(lowered, _SUPPORT_ISSUE_KEYWORDS):
        return ChatIntent.SUPPORT_ISSUE

    if contains_any_keyword(lowered, _HOW_TO_PHRASES):
        return ChatIntent.HOW_TO

    if lowered.endswith("?"):
        return ChatIntent.KNOWLEDGE

    return ChatIntent.GENERAL


def _history_user_messages(request: ChatRequest) -> List[str]:
    return [turn.message for turn in request.history if turn.role == "user"]


def _handle_navigation(request: ChatRequest, lowered: str) -> ChatResponse:
    noun = _match_route(lowered)
    target = _resolve_route_target(noun, request.role)
    label = noun.title() if noun else "that page"
    return ChatResponse(
        message=f"You can get to {label} from the main navigation.",
        intent=ChatIntent.NAVIGATION,
        action=ChatAction(type="navigate", target=target, label=label.title()),
        suggestions=PREDEFINED_SUGGESTIONS,
    )


def _handle_how_to(request: ChatRequest, lowered: str) -> ChatResponse:
    if "reimburs" in lowered or "expense" in lowered:
        return ChatResponse(
            message=(
                "Submit reimbursements from New Request using the Account "
                "Management category, with receipts attached."
            ),
            intent=ChatIntent.HOW_TO,
            action=ChatAction(
                type="navigate", target="new-request.html", label="New Request"
            ),
            suggestions=PREDEFINED_SUGGESTIONS,
        )

    if "ticket" in lowered or "request" in lowered or "submit" in lowered:
        return ChatResponse(
            message=(
                "Go to New Request, fill in a subject, category, and "
                "description, then submit. You can track it afterward under "
                "My Tickets."
            ),
            intent=ChatIntent.HOW_TO,
            action=ChatAction(
                type="navigate", target="new-request.html", label="New Request"
            ),
            suggestions=PREDEFINED_SUGGESTIONS,
        )

    if "polic" in lowered or "find" in lowered:
        return ChatResponse(
            message="Check the Knowledge Base for policies and how-to articles.",
            intent=ChatIntent.HOW_TO,
            action=ChatAction(
                type="navigate", target="knowledge-base.html", label="Knowledge Base"
            ),
            suggestions=PREDEFINED_SUGGESTIONS,
        )

    return ChatResponse(
        message=(
            "Tell me a bit more about what you're trying to do and I can "
            "point you to the right place or help you get it done."
        ),
        intent=ChatIntent.HOW_TO,
        suggestions=PREDEFINED_SUGGESTIONS,
    )


def _handle_knowledge(request: ChatRequest) -> ChatResponse:
    allowed_scopes = get_allowed_scopes(request.role, request.department)
    result = answer_question(request.message, allowed_scopes=allowed_scopes)

    return ChatResponse(
        message=result.answer,
        intent=ChatIntent.KNOWLEDGE,
        action=result.action,
        knowledge_verified=result.verified,
        suggestions=PREDEFINED_SUGGESTIONS,
    )


def _handle_ticket_status(request: ChatRequest, lowered: str) -> ChatResponse:
    match = _TICKET_ID_PATTERN.search(lowered)
    ticket_id = None
    if match:
        full_match = match.group(1)
        if full_match.startswith("hd"):
            ticket_id = full_match.upper()
        else:
            ticket_id = f"HD-{match.group(2)}"

    if ticket_id:
        return ChatResponse(
            message=f"Let me pull up ticket {ticket_id} for you.",
            intent=ChatIntent.TICKET_STATUS,
            action=ChatAction(
                type="lookup_ticket", target="my-tickets.html", ticket_id=ticket_id
            ),
            suggestions=PREDEFINED_SUGGESTIONS,
        )

    return ChatResponse(
        message="You can view your requests and their status under My Tickets.",
        intent=ChatIntent.TICKET_STATUS,
        action=ChatAction(
            type="navigate", target="my-tickets.html", label="My Tickets"
        ),
        suggestions=PREDEFINED_SUGGESTIONS,
    )


def _handle_ticket_drafting(request: ChatRequest) -> ChatResponse:
    draft, missing = ticket_draft_service.build_support_draft(
        request.message,
        history_user_messages=_history_user_messages(request),
        existing_draft=request.draft,
    )

    if missing:
        return ChatResponse(
            message=_missing_fields_prompt(missing),
            intent=ChatIntent.SUPPORT_ISSUE,
            ticket_draft=draft,
            missing_fields=missing,
        )

    return ChatResponse(
        message=(
            "Here's a draft based on what you told me - review it, edit "
            "anything that's not quite right, and submit it when you're ready."
        ),
        intent=ChatIntent.SUPPORT_ISSUE,
        ticket_draft=draft,
        missing_fields=[],
    )


def _handle_leave_management(request: ChatRequest) -> ChatResponse:
    draft, missing = ticket_draft_service.build_leave_draft(
        request.message,
        history_user_messages=_history_user_messages(request),
        existing_draft=request.draft,
    )

    if missing:
        return ChatResponse(
            message=_missing_fields_prompt(missing),
            intent=ChatIntent.LEAVE_MANAGEMENT,
            ticket_draft=draft,
            missing_fields=missing,
        )

    return ChatResponse(
        message=(
            "Here's your leave request draft - review it, edit anything "
            "that's not quite right, and submit it when you're ready."
        ),
        intent=ChatIntent.LEAVE_MANAGEMENT,
        ticket_draft=draft,
        missing_fields=[],
    )


def _missing_fields_prompt(missing: List[str]) -> str:
    if len(missing) == 1:
        return f"Could you tell me more about the {missing[0]}?"
    joined = ", ".join(missing[:-1]) + f", and {missing[-1]}"
    return f"Could you tell me more about the {joined}?"


def handle_message(request: ChatRequest) -> ChatResponse:
    lowered = _normalize(request.message)

    if not lowered:
        return ChatResponse(
            message="I'm Genie, your workplace assistant. What can I help you with?",
            intent=ChatIntent.GENERAL,
            suggestions=PREDEFINED_SUGGESTIONS,
        )

    if request.draft is not None or request.active_intent in (
        ChatIntent.LEAVE_MANAGEMENT,
        ChatIntent.SUPPORT_ISSUE,
        ChatIntent.CREATE_TICKET,
    ):
        if request.active_intent == ChatIntent.LEAVE_MANAGEMENT:
            return _handle_leave_management(request)
        return _handle_ticket_drafting(request)

    intent = classify_intent(request.message)

    if intent == ChatIntent.TICKET_STATUS:
        return _handle_ticket_status(request, lowered)
    if intent == ChatIntent.LEAVE_MANAGEMENT:
        return _handle_leave_management(request)
    if intent == ChatIntent.NAVIGATION:
        return _handle_navigation(request, lowered)
    if intent == ChatIntent.CREATE_TICKET:
        return _handle_ticket_drafting(request)
    if intent == ChatIntent.KNOWLEDGE:
        return _handle_knowledge(request)
    if intent == ChatIntent.SUPPORT_ISSUE:
        return _handle_ticket_drafting(request)
    if intent == ChatIntent.HOW_TO:
        return _handle_how_to(request, lowered)

    return ChatResponse(
        message=(
            "I'm Genie, your workplace assistant. I can help you navigate "
            "TicketGenie, answer policy questions, or start a support "
            "request."
        ),
        intent=ChatIntent.GENERAL,
        suggestions=PREDEFINED_SUGGESTIONS,
    )
