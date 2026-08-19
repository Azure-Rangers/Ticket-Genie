# backend/agents/chatbot_agent.py

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from models.chatbot import ChatIntent, ChatScope, ChatTurn, RequestType, TicketDraft
from services.ai_service import ai_service as default_ai_service


class ChatActionType(str, Enum):
    RESPOND = "respond"
    NAVIGATE = "navigate"
    SEARCH_KNOWLEDGE = "search_knowledge"
    START_TICKET_DRAFT = "start_ticket_draft"
    ASK_FOLLOWUP = "ask_followup"
    SHOW_TICKET_DRAFT = "show_ticket_draft"
    CHECK_TICKET_STATUS = "check_ticket_status"
    # Single action for all three management write intents (reassign_ticket /
    # change_priority / create_portal_employee) - services.management_action_service
    # owns the deterministic ask/confirm/execute state machine from here,
    # this action just says "route to that service".
    MANAGEMENT_ACTION = "management_action"


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
    # Standard/Anonymous Request's single date field only - leave null for
    # leave_management (use start_date/end_date below instead).
    preferred_date: Optional[str] = None
    # Leave Management's date range - independent fields so a partially
    # known range (only one date given so far) is representable exactly.
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    ticket_id: Optional[str] = None


class ManagementActionFields(BaseModel):
    """
    Semantic extraction only for the 3 management write intents - GPT's job
    ends here. services.management_action_service independently validates
    every value against the canonical vocabulary, resolves ticket ambiguity
    deterministically, and re-checks authorization before ever writing
    anything; nothing here is trusted as-is.
    """

    ticket_id: Optional[str] = None
    target_department: Optional[str] = None
    target_priority: Optional[str] = None
    employee_name: Optional[str] = None
    employee_email: Optional[str] = None
    employee_object_id: Optional[str] = None
    employee_role: Optional[str] = None
    employee_department: Optional[str] = None


class ChatbotDecision(BaseModel):
    # Required, no default: the workplace-scope guardrail
    # (services.chatbot_service.handle_message) must never silently treat
    # a missing/malformed scope as workplace. If GPT omits this field (or
    # the response otherwise fails schema validation), ai_service.generate
    # raises AIServiceError - handle_message's existing AI-failure path
    # returns its safe fallback, and the out-of-scope early exit is never
    # reached. A default here would let a malformed response fail open
    # straight into the normal pipeline instead.
    scope: ChatScope = Field(
        description=(
            "workplace if this turn is about company/workplace matters "
            "(policy, HR, IT, accounting, tickets, leave, or how the reply "
            "should be produced for one of those); out_of_scope if it's "
            "about something unrelated to work (recipes, movies/TV, "
            "sports, celebrities, general politics, weather, trivia, "
            "etc). Judged by meaning, not by whether a topic word appears "
            "- see the SCOPE section above for the exact test and "
            "examples. Always set this field explicitly - only set "
            "out_of_scope when genuinely confident the turn is unrelated "
            "to work; when unsure, choose workplace."
        ),
    )
    intent: ChatIntent
    action: ChatActionType
    message: str
    navigation_target: Optional[NavigationTarget] = None
    knowledge_query: Optional[str] = None
    ticket_fields: Optional[ExtractedTicketFields] = None
    management_fields: Optional[ManagementActionFields] = None
    missing_fields: List[str] = Field(default_factory=list)
    request_type: Optional[RequestType] = None
    anonymity_requested: bool = Field(
        default=False,
        description=(
            "True only if the user's own words explicitly asked to remain "
            "anonymous or not have their name/identity attached. Must be "
            "true whenever request_type=anonymous is chosen - the backend "
            "deterministically downgrades an anonymous request_type back "
            "to standard when this is false."
        ),
    )


CHATBOT_DECISION_PROMPT = """
You are the semantic router for TicketGenie's workplace assistant chatbot.
Read the employee's message (and the conversation so far) and return a
single structured decision. Do not answer company-policy questions
yourself here - that happens in a separate step after authorized
knowledge is retrieved. Just decide what the user wants and extract any
facts they already gave you.

SCOPE (decide this first, independently of everything else below):
Genie exists to help with workplace matters only - company policy, HR,
IT, accounting, workplace operations, tickets, leave, payroll, benefits,
company devices/software, and similar. Set `scope`:
- workplace: the turn is about a workplace matter, OR it's a normal
  conversational continuation of one (e.g. answering a follow-up
  question Genie itself just asked, giving more detail about an issue
  already being discussed).
- out_of_scope: the turn is about something with no genuine connection
  to work - general trivia, recipes, movies/TV/streaming
  recommendations, sports, celebrities, general politics/elections
  (who to vote for), weather forecasts, poetry/creative writing about
  non-work topics, or similar.
Judge by MEANING, not by whether a topic word appears - a topic word
alone (e.g. "movie", "weather", "politics") does not decide it either
way. What decides it is whether the subject is genuinely the company/
workplace or something personal/unrelated:
- "Can you help me write an email to HR about my benefits?" -> workplace
- "Write me an email inviting my friends to a movie." -> out_of_scope
- "What is the company's policy on political discussions at work?" ->
  workplace (the subject is a company policy, not politics itself)
- "Who should I vote for?" -> out_of_scope
- "Can I watch Netflix on my company laptop?" -> workplace (it's about
  a company device/policy)
- "Recommend me a Netflix show." -> out_of_scope
- "What's the weather policy for office closures?" -> workplace
- "What's tomorrow's weather?" -> out_of_scope
- "My VPN isn't working." / "How do reimbursements work?" / "Can I take
  leave next Friday?" / "Move HD-1023 to IT." -> workplace
- "Give me a biryani recipe." / "What movie should I watch?" / "Tell me
  about Taylor Swift." / "Explain the NBA playoffs." -> out_of_scope

This must be judged fresh on THIS turn's actual message, even when the
intent below is already fixed by an in-progress flow (ticket drafting or
a management action awaiting more info): if the user abandons that flow
and asks something with no workplace connection, scope is out_of_scope
for this turn regardless of what came before. Conversely, don't mark an
on-topic continuation (e.g. a plain date, a department name, "yes") as
out_of_scope just because it's short - short is not the same as
unrelated. When genuinely unsure, prefer workplace - only choose
out_of_scope when confident the turn has no real workplace connection.

INTENTS (choose exactly one; irrelevant when scope is out_of_scope, but
still classify honestly):
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
- reassign_ticket: the user wants to change which department an EXISTING
  ticket belongs to (e.g. "move HD-1032 to IT", "this belongs to
  Accounting", "reassign that request to HR"). Only for an existing
  ticket, never a new request.
- change_priority: the user wants to change the priority of an EXISTING
  ticket (e.g. "make HD-1050 low priority", "this shouldn't be
  Critical, move it to High").
- create_portal_employee: the user wants to add/create/assign a new
  person to the portal (e.g. "add a new employee", "assign Priya Shah
  to the portal", "create a portal user for..."). Do not confuse with
  create_ticket/support_issue - this is about portal user accounts, not
  a support request.
- general: greetings, small talk, or anything that doesn't fit above.
  This includes reassign_ticket/change_priority/create_portal_employee
  messages from a user who turns out not to be authorized - still
  classify the intent honestly here; the backend independently verifies
  the caller's authenticated role and denies unauthorized attempts on
  its own, so you never need to guess at permissions.

ACTIONS: respond, navigate, search_knowledge, start_ticket_draft,
ask_followup, show_ticket_draft, check_ticket_status, management_action.
Pick the action that matches the intent (e.g. knowledge ->
search_knowledge, ticket_status -> check_ticket_status, a leave/support
request that is missing required info -> ask_followup, a complete one ->
show_ticket_draft or start_ticket_draft, reassign_ticket/change_priority/
create_portal_employee -> management_action).

MANAGEMENT ACTION FIELD EXTRACTION (reassign_ticket / change_priority /
create_portal_employee only - populate `management_fields`, leave
`ticket_fields` null for these three intents):
- ticket_id: only if the user gave an explicit ticket number (e.g.
  "HD-1032"). Never guess or invent one - leave null if not given, the
  backend will ask the user to choose from their real tickets.
- target_department: only set this to one of the allowed departments
  listed below (Ticket departments), matched by meaning (e.g. "IT" ->
  the IT department option). If the user's wording doesn't clearly map
  to exactly one allowed department, leave it null - never invent a
  department name that isn't in the list.
- target_priority: only set this to one of the allowed priorities
  listed below (Ticket priorities), matched by meaning (e.g. "urgent"
  might mean High or Critical - if genuinely ambiguous, leave null).
- employee_name, employee_email, employee_object_id, employee_role,
  employee_department: only for create_portal_employee, only facts the
  user actually stated. employee_role and employee_department must be
  matched to one of the allowed lists below (Employee roles / Employee
  departments) by meaning, or left null if unclear - never invent a
  role or department that isn't in the list. Never invent an email or
  object id.

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
- `preferred_date` must be an ISO date (YYYY-MM-DD), and is only used for
  support_issue/create_ticket (the Standard Request form's single
  preferred date). If the user gave a relative reference ("before
  Friday", "next Monday", "tomorrow"), resolve it relative to today's
  date, which is provided below. If you cannot confidently resolve a
  date, leave preferred_date null instead of guessing. Always leave
  preferred_date null for leave_management - use start_date/end_date
  instead (next rule).
- For leave_management specifically, extract `start_date` and, when the
  user gave one, `end_date` as separate ISO dates (YYYY-MM-DD) - e.g.
  "August 24 through August 28" -> start_date=2026-08-24,
  end_date=2026-08-28 (resolve relative references against today's date,
  provided below). If the user gives only one date for the leave, that
  is start_date - leave end_date null rather than guessing one. Never
  invent either date. Still restate the full range in `description` for
  readability, but start_date/end_date are the fields the leave form
  actually uses - never omit them just because the range is also
  mentioned in prose.
- `category` must be chosen from the allowed list provided below for
  the current flow (support vs leave), matched by meaning - e.g. a
  laptop problem is "IT & Technology", a request for medical leave is
  "Medical Leave". If nothing fits confidently, leave it null.
- `description` is a concise, professional SUMMARY of the request as a
  whole - not a transcript and not a per-turn restatement. Every turn,
  re-synthesize the full up-to-date description from everything relevant
  said across the WHOLE conversation so far (shown below), replacing any
  previous description rather than adding a new sentence onto it. Aim
  for roughly 3-4 sentences (shorter is fine, and preferred, if little
  has been said) covering whichever of these are actually known: what
  the issue/request is, relevant symptoms/details, the device/system/
  context involved, when it started, business impact, troubleshooting
  already tried, and important dates/constraints. Do not quote the
  user's own phrasing verbatim, do not write "the user said...", and
  never state the same fact twice. Never invent a detail that was not
  actually stated - preserve every important fact already established,
  do not drop one just to shorten the summary.
- `title` stays short and descriptive - roughly 3-8 words identifying
  the request (e.g. "VPN connection timeout on Mac") - never a full
  sentence or a fragment of what the user typed.
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
- standard: the DEFAULT for every ordinary support/workplace
  request/issue (e.g. "my VPN isn't working", "I need two monitors", "I
  need help with a reimbursement"). Most requests are standard - when in
  doubt, choose standard.
- anonymous: choose this ONLY when the user's own words explicitly ask
  for anonymity - they say they don't want their name/identity attached,
  ask to stay anonymous, or explicitly say they want the Anonymous
  Request option. When (and only when) you choose anonymous, also set
  anonymity_requested=true. Never choose anonymous just because a topic
  is sensitive, personal, or uncomfortable (e.g. harassment, conflict,
  a health issue) - the user has to actually ask for anonymity in their
  own words. If they haven't, choose standard even for a sensitive
  topic.
For create_ticket or support_issue, never leave request_type null and
never ask the user to pick between Standard and Anonymous - default to
standard whenever anonymity wasn't explicitly requested.

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
    ticket_departments: List[str] = None,
    ticket_priorities: List[str] = None,
    employee_departments: List[str] = None,
    employee_roles: List[str] = None,
    pending_action_context: Optional[str] = None,
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
Ticket departments (for reassign_ticket): {", ".join(ticket_departments or [])}
Ticket priorities (for change_priority): {", ".join(ticket_priorities or [])}
Employee departments (for create_portal_employee): {", ".join(employee_departments or [])}
Employee roles (for create_portal_employee): {", ".join(employee_roles or [])}

Conversation so far:
{_format_history(history)}

Current ticket draft (already-known fields - do not re-ask for these):
{_format_draft(existing_draft)}

Current management action in progress (already-known fields - do not
re-ask for these; only relevant for reassign_ticket / change_priority /
create_portal_employee):
{pending_action_context or "(none)"}

Latest user message:
{message}
"""

    return ai_service.generate(
        system_prompt=CHATBOT_DECISION_PROMPT,
        user_content=user_content,
        response_model=ChatbotDecision,
    )
