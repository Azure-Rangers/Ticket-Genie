"""
Chatbot Agent: role-aware workplace assistant.

Semantic understanding (what the user means) comes from a single GPT-5.2
structured-output call per turn (agents/chatbot_agent.py). Everything that
must be trustworthy regardless of what the model says stays deterministic
Python here: route mapping, the leave-management business rule, knowledge
authorization/retrieval, ticket-field validation, and failure handling.
Knowledge answers get one additional GPT-5.2 call to compose a grounded
response from already-authorized, already-retrieved content - the model
never chooses what it's allowed to see.
"""

from typing import List, Optional

from agents import chatbot_agent, knowledge_agent
from agents.chatbot_agent import ChatbotDecision, NavigationTarget
from database.crud import get_ticket_by_id as default_get_ticket_by_id
from models.chatbot import ChatAction, ChatIntent, ChatRequest, ChatResponse
from services import ticket_draft_service
from services.ai_service import ai_service as default_ai_service
from services.knowledge_service import (
    KnowledgeRetriever,
    SearchUnavailableError,
    default_knowledge_retriever,
)
from services.role_service import get_allowed_scopes
from services.ticket_draft_service import merge_extracted_fields, validate_ticket_id

PREDEFINED_SUGGESTIONS = [
    "Ask a question",
    "Help me create a ticket",
    "Check my ticket status",
]

GPT_UNAVAILABLE_MESSAGE = (
    "I'm having trouble reaching the assistant service right now. Please "
    "try again in a moment, or use New Request / Knowledge Base directly "
    "from the navigation."
)
SEARCH_UNAVAILABLE_MESSAGE = (
    "I can't reach the knowledge search service right now, so I can't "
    "verify an answer to that. You can browse the Knowledge Base directly, "
    "or I can help you open a support request."
)
COULD_NOT_VERIFY_MESSAGE = (
    "I couldn't verify an answer to that from the knowledge sources you're "
    "authorized to access. You can browse the Knowledge Base for related "
    "articles, or I can help you open a support request."
)

_MANAGEMENT_HOME = "pages/management-portal.html"


def _route(employee_page: str, management_page: str = None) -> dict:
    return {"employee": employee_page, "management": management_page or employee_page}


_ROUTE_MAP = {
    NavigationTarget.DASHBOARD: _route("index.html", _MANAGEMENT_HOME),
    NavigationTarget.NEW_REQUEST: _route("new-request.html"),
    NavigationTarget.MY_TICKETS: _route("my-tickets.html"),
    NavigationTarget.KNOWLEDGE_BASE: _route("knowledge-base.html"),
    NavigationTarget.NOTIFICATIONS: _route("notifications.html"),
    NavigationTarget.CHAT_HISTORY: _route("chat-history.html"),
}

_TICKET_DRAFT_INTENTS = (
    ChatIntent.CREATE_TICKET,
    ChatIntent.SUPPORT_ISSUE,
    ChatIntent.LEAVE_MANAGEMENT,
)

_KNOWLEDGE_BASE_ACTION = ChatAction(
    type="navigate", target="knowledge-base.html", label="Browse Knowledge Base"
)


def _resolve_route_target(target: NavigationTarget, role: Optional[str]) -> str:
    routes = _ROUTE_MAP[target]
    is_management = (role or "").strip().lower() == "management"
    return routes["management"] if is_management else routes["employee"]


def _shortcut_for_intent(intent: ChatIntent) -> ChatResponse:
    """A predefined button was clicked with no free-text yet - no GPT call needed."""

    if intent == ChatIntent.TICKET_STATUS:
        return ChatResponse(
            message=(
                "You can view all your requests and their status under My "
                "Tickets, or tell me a ticket number and I'll pull it up."
            ),
            intent=intent,
            action=ChatAction(
                type="navigate", target="my-tickets.html", label="My Tickets"
            ),
            suggestions=PREDEFINED_SUGGESTIONS,
        )
    if intent in _TICKET_DRAFT_INTENTS:
        return ChatResponse(
            message=(
                "Sure - briefly describe what's going on and I'll help put "
                "together a request."
            ),
            intent=intent,
            missing_fields=["a description of the issue"],
        )
    if intent == ChatIntent.KNOWLEDGE:
        return ChatResponse(message="What would you like to know?", intent=intent)
    return ChatResponse(
        message="What can I help you with?",
        intent=ChatIntent.GENERAL,
        suggestions=PREDEFINED_SUGGESTIONS,
    )


def _handle_navigation(decision: ChatbotDecision, role: Optional[str]) -> ChatResponse:
    if decision.navigation_target is None:
        return ChatResponse(
            message=decision.message,
            intent=ChatIntent.HOW_TO,
            suggestions=PREDEFINED_SUGGESTIONS,
        )

    target = _resolve_route_target(decision.navigation_target, role)
    label = decision.navigation_target.value.replace("_", " ").title()
    return ChatResponse(
        message=decision.message,
        intent=ChatIntent.NAVIGATION,
        action=ChatAction(type="navigate", target=target, label=label),
        suggestions=PREDEFINED_SUGGESTIONS,
    )


def _handle_ticket_status(decision: ChatbotDecision, *, ticket_lookup) -> ChatResponse:
    ticket_id = None
    if decision.ticket_fields:
        # Validate the format BEFORE it ever reaches a database call.
        ticket_id = validate_ticket_id(decision.ticket_fields.ticket_id)

    if ticket_id:
        ticket = ticket_lookup(ticket_id)
        if ticket is None:
            return ChatResponse(
                message=(
                    f"I couldn't find a ticket {ticket_id}. Double-check the "
                    "number, or browse My Tickets to find it."
                ),
                intent=ChatIntent.TICKET_STATUS,
                action=ChatAction(
                    type="navigate", target="my-tickets.html", label="My Tickets"
                ),
                suggestions=PREDEFINED_SUGGESTIONS,
            )
        return ChatResponse(
            message=(
                f"Ticket {ticket_id} ({ticket['title']}) is currently "
                f"'{ticket['status']}'."
            ),
            intent=ChatIntent.TICKET_STATUS,
            action=ChatAction(
                type="lookup_ticket", target="my-tickets.html", ticket_id=ticket_id
            ),
            suggestions=PREDEFINED_SUGGESTIONS,
        )

    fallback_message = "You can view your requests and their status under My Tickets."
    return ChatResponse(
        message=decision.message or fallback_message,
        intent=ChatIntent.TICKET_STATUS,
        action=ChatAction(
            type="navigate", target="my-tickets.html", label="My Tickets"
        ),
        suggestions=PREDEFINED_SUGGESTIONS,
    )


def _handle_ticket_drafting(
    request: ChatRequest, decision: ChatbotDecision, intent: ChatIntent
) -> ChatResponse:
    draft, missing = merge_extracted_fields(
        decision.ticket_fields,
        existing_draft=request.draft,
        gpt_missing_fields=decision.missing_fields,
        intent=intent,
    )

    if missing:
        return ChatResponse(
            message=decision.message or _missing_fields_prompt(missing),
            intent=intent,
            ticket_draft=draft,
            missing_fields=missing,
        )

    return ChatResponse(
        message=(
            decision.message
            or "Here's a draft based on what you told me - review it, edit "
            "anything that's not quite right, and submit it when you're ready."
        ),
        intent=intent,
        ticket_draft=draft,
        missing_fields=[],
    )


def _missing_fields_prompt(missing: List[str]) -> str:
    if len(missing) == 1:
        return f"Could you tell me more about {missing[0]}?"
    joined = ", ".join(missing[:-1]) + f", and {missing[-1]}"
    return f"Could you tell me more about {joined}?"


def _handle_knowledge(
    request: ChatRequest,
    decision: ChatbotDecision,
    *,
    retriever: KnowledgeRetriever,
    ai_service,
) -> ChatResponse:
    # TODO(auth): request.role/request.department are client-supplied, not
    # verified server-side (no auth/session system exists yet - see
    # role_service.py's module docstring for the tracked gap). This is NOT
    # production-secure: a caller could claim any role/department. Once
    # real authentication exists, resolve these from the trusted
    # session/JWT here instead of trusting the request body.
    allowed_scopes = get_allowed_scopes(request.role, request.department)
    query = decision.knowledge_query or request.message

    try:
        documents = retriever.search(query, allowed_scopes)
    except SearchUnavailableError:
        return ChatResponse(
            message=SEARCH_UNAVAILABLE_MESSAGE,
            intent=ChatIntent.KNOWLEDGE,
            knowledge_verified=False,
            action=_KNOWLEDGE_BASE_ACTION,
            suggestions=PREDEFINED_SUGGESTIONS,
        )

    if not documents:
        return ChatResponse(
            message=COULD_NOT_VERIFY_MESSAGE,
            intent=ChatIntent.KNOWLEDGE,
            knowledge_verified=False,
            action=_KNOWLEDGE_BASE_ACTION,
            suggestions=PREDEFINED_SUGGESTIONS,
        )

    try:
        grounded = knowledge_agent.answer_from_context(
            query, documents, ai_service=ai_service
        )
    except Exception:
        return ChatResponse(
            message=GPT_UNAVAILABLE_MESSAGE,
            intent=ChatIntent.KNOWLEDGE,
            knowledge_verified=False,
            action=_KNOWLEDGE_BASE_ACTION,
            suggestions=PREDEFINED_SUGGESTIONS,
        )

    return ChatResponse(
        message=grounded.answer,
        intent=ChatIntent.KNOWLEDGE,
        knowledge_verified=grounded.verified,
        action=None if grounded.verified else _KNOWLEDGE_BASE_ACTION,
        suggestions=PREDEFINED_SUGGESTIONS,
    )


def handle_message(
    request: ChatRequest,
    *,
    ai_service=default_ai_service,
    retriever: KnowledgeRetriever = None,
    ticket_lookup=default_get_ticket_by_id,
) -> ChatResponse:
    retriever = retriever or default_knowledge_retriever
    message = request.message.strip()

    if not message:
        if request.active_intent:
            return _shortcut_for_intent(request.active_intent)
        return ChatResponse(
            message="I'm Genie, your workplace assistant. What can I help you with?",
            intent=ChatIntent.GENERAL,
            suggestions=PREDEFINED_SUGGESTIONS,
        )

    try:
        decision = chatbot_agent.decide(
            message,
            history=request.history,
            existing_draft=request.draft,
            known_intent=request.active_intent,
            standard_categories=ticket_draft_service.STANDARD_CATEGORIES,
            leave_types=ticket_draft_service.LEAVE_TYPES,
            ai_service=ai_service,
        )
    except Exception:
        return ChatResponse(
            message=GPT_UNAVAILABLE_MESSAGE,
            intent=ChatIntent.GENERAL,
            suggestions=PREDEFINED_SUGGESTIONS,
        )

    # A continuation always keeps the flow's intent - the model doesn't get
    # to silently change it mid-draft.
    intent = request.active_intent or decision.intent

    if intent == ChatIntent.LEAVE_MANAGEMENT:
        # Hard business rule: leave requests always go through the
        # Standard Request ticket-drafting flow, regardless of the
        # action the model proposed.
        return _handle_ticket_drafting(request, decision, intent)

    if intent == ChatIntent.TICKET_STATUS:
        return _handle_ticket_status(decision, ticket_lookup=ticket_lookup)

    if intent == ChatIntent.NAVIGATION:
        return _handle_navigation(decision, request.role)

    if intent in (ChatIntent.CREATE_TICKET, ChatIntent.SUPPORT_ISSUE):
        return _handle_ticket_drafting(request, decision, intent)

    if intent == ChatIntent.KNOWLEDGE:
        return _handle_knowledge(
            request, decision, retriever=retriever, ai_service=ai_service
        )

    return ChatResponse(
        message=decision.message,
        intent=intent,
        suggestions=PREDEFINED_SUGGESTIONS,
    )
