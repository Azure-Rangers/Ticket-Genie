"""
Ticket Drafting: deterministic validation + merge layer.

Semantic extraction (what the user meant, what fields that implies) is
GPT-5.2's job (backend/agents/chatbot_agent.py). This module never guesses
meaning from the message text - it only validates what the model
extracted against the schema TicketCreate/the Standard/Anonymous Request
form actually allows, and merges it into the running TicketDraft.
`priority` is never set here - that's an internal routing field owned by
Saketh's classification agents (backend/agents/*), not something the
chatbot should guess. `department` is only ever set here for the one hard
business rule that isn't a guess: every Leave Management request routes
deterministically to LEAVE_DEPARTMENT, never through classification.
"""

import re
from datetime import datetime
from typing import List, Optional, Tuple

from agents.category_agent import is_valid_department
from agents.chatbot_agent import ExtractedTicketFields
from agents.orchestrator import classify_ticket as default_classify_ticket
from models.chatbot import ChatIntent, RequestType, TicketDraft

STANDARD_CATEGORIES = [
    "HR & Workforce Operations",
    "IT & Technology",
    "Account Management",
    "Upper Executive Management",
    "Other",
]

LEAVE_TYPES = [
    "Paid Time Off (PTO)",
    "Medical Leave",
    "Parental Leave",
    "Bereavement",
    "Unpaid Leave",
    "Other",
]

# Hard business rule: every Leave Management request routes directly to
# this department, deterministically, skipping normal classification.
# Reused straight from agents/category_agent.ALLOWED_DEPARTMENTS (the
# single source of truth Saketh's classifier also uses, and the exact
# spelling models.ticket.TicketCreate.department accepts) rather than a
# second hardcoded vocabulary - see also services/ticket_service.py's
# department_override, which is what makes this rule hold at submission
# time too (classify_ticket() would otherwise silently overwrite it).
LEAVE_DEPARTMENT = "Upper Management"
assert is_valid_department(LEAVE_DEPARTMENT)

# Deterministic map from the classifier's department taxonomy onto the
# Standard/Anonymous Request form's own (coarser) category dropdown, used
# only to fix up a draft that landed on "Other". "Workplace Operations
# Team" has no equivalent bucket in that dropdown, so it intentionally has
# no entry here - reclassify_other_category() falls back to leaving the
# draft at "Other" (a real, valid value) rather than inventing one.
_DEPARTMENT_TO_STANDARD_CATEGORY = {
    "HR Team": "HR & Workforce Operations",
    "IT Team": "IT & Technology",
    "Accounting Team": "Account Management",
    "Upper Management": "Upper Executive Management",
}

_ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_TICKET_ID_PATTERN = re.compile(r"^HD-\d+$", re.IGNORECASE)

_MISSING_TITLE_MARKERS = ("title", "subject")
_MISSING_DESCRIPTION_MARKERS = ("description", "detail", "reason", "what happened")
_MISSING_CATEGORY_MARKERS = ("categ", "leave type", "type of leave")
_MISSING_DATE_MARKERS = ("date",)
_MISSING_START_DATE_MARKERS = (
    "start date",
    "starting date",
    "when your leave starts",
    "when it starts",
    "begin date",
)
_MISSING_END_DATE_MARKERS = (
    "end date",
    "ending date",
    "return date",
    "when you return",
    "when your leave ends",
    "when it ends",
)


def validate_category(value: Optional[str], allowed: List[str]) -> Optional[str]:
    """Snap a model-proposed category to the exact allowed value, or reject it."""

    if not value:
        return None
    normalized = value.strip().lower()
    for option in allowed:
        if option.lower() == normalized:
            return option
    return None


def validate_iso_date(value: Optional[str]) -> Optional[str]:
    """Accept only a well-formed, real calendar date in YYYY-MM-DD."""

    if not value:
        return None
    value = value.strip()
    if not _ISO_DATE_PATTERN.match(value):
        return None
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return None
    return value


def validate_ticket_id(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    value = value.strip().upper()
    if not value.startswith("HD-"):
        value = f"HD-{value}" if value.isdigit() else value
    return value if _TICKET_ID_PATTERN.match(value) else None


def _fallback_title(description: str, *, max_words: int = 10) -> str:
    words = description.strip().split()
    if not words:
        return "Support Request"
    title = " ".join(words[:max_words])
    return title[:1].upper() + title[1:]


def _merge_description(
    existing: Optional[str], extracted: Optional[str]
) -> Optional[str]:
    """
    The model is shown the full conversation and the current draft every
    turn and is instructed to return the complete, up-to-date summary in
    `description` (not just this turn's new sentence) - so a fresh
    non-empty extraction replaces the running draft's description rather
    than being appended to it. Appending here is what previously produced
    transcript-style, ever-growing descriptions.
    """
    return extracted if extracted else existing


def _filter_missing_fields(
    gpt_missing: List[str], draft: TicketDraft, *, intent: ChatIntent
) -> List[str]:
    """
    Hard backstop: never re-ask for something the draft already has, even
    if the model's own missing_fields list forgot to drop it.

    Leave Management needs BOTH startDate and endDate, tracked
    separately - a generic "date" mention from the model is only dropped
    once both sides are known; a mention that specifically names "start"
    or "end" is dropped as soon as that specific side is known. Standard/
    Anonymous only ever have the single optional preferredDate, unchanged.
    """

    is_leave = intent == ChatIntent.LEAVE_MANAGEMENT
    kept = []
    for field in gpt_missing:
        lowered = field.lower()
        if draft.title and any(marker in lowered for marker in _MISSING_TITLE_MARKERS):
            continue
        if draft.description and any(
            marker in lowered for marker in _MISSING_DESCRIPTION_MARKERS
        ):
            continue
        if draft.category and any(
            marker in lowered for marker in _MISSING_CATEGORY_MARKERS
        ):
            continue
        if is_leave:
            if draft.startDate and any(
                marker in lowered for marker in _MISSING_START_DATE_MARKERS
            ):
                continue
            if draft.endDate and any(
                marker in lowered for marker in _MISSING_END_DATE_MARKERS
            ):
                continue
            if (
                draft.startDate
                and draft.endDate
                and any(marker in lowered for marker in _MISSING_DATE_MARKERS)
            ):
                continue
        elif draft.preferredDate and any(
            marker in lowered for marker in _MISSING_DATE_MARKERS
        ):
            continue
        kept.append(field)
    return kept


def merge_extracted_fields(
    extracted: Optional[ExtractedTicketFields],
    *,
    existing_draft: Optional[TicketDraft],
    gpt_missing_fields: List[str],
    intent: ChatIntent,
    request_type: Optional[RequestType] = None,
) -> Tuple[TicketDraft, List[str]]:
    """
    Deterministically fold the model's extraction into the running draft,
    validating category/date against the schema's exact allowed values.
    Returns (draft, missing_fields).
    """

    extracted = extracted or ExtractedTicketFields()
    draft = existing_draft.model_copy() if existing_draft else TicketDraft()
    is_leave = intent == ChatIntent.LEAVE_MANAGEMENT

    draft.description = _merge_description(draft.description, extracted.description)

    if not draft.category:
        allowed = LEAVE_TYPES if is_leave else STANDARD_CATEGORIES
        draft.category = validate_category(extracted.category, allowed)

    invalid_range = False
    if is_leave:
        # Backward compatibility only: an older persisted draft (from
        # before startDate/endDate existed) may carry just preferredDate -
        # treat it as the start date going forward rather than losing it.
        # New responses always use startDate/endDate directly.
        if not draft.startDate and draft.preferredDate:
            draft.startDate = draft.preferredDate

        new_start = validate_iso_date(extracted.start_date)
        new_end = validate_iso_date(extracted.end_date)

        # What the range would be if this turn's new value(s) were
        # applied on top of what's already known.
        tentative_start = draft.startDate or new_start
        tentative_end = draft.endDate or new_end

        if tentative_start and tentative_end and tentative_end < tentative_start:
            # Never silently accept, flip, or guess-correct a reversed
            # range - drop this turn's new value(s) so a later correction
            # can still take effect, and flag it for the missing-fields
            # section below to ask the user to fix it explicitly.
            invalid_range = True
        else:
            if not draft.startDate and new_start:
                draft.startDate = new_start
            if not draft.endDate and new_end:
                draft.endDate = new_end

        # Keep preferredDate in sync as an alias for startDate, since
        # submission (frontend + TicketCreate) still only has one date.
        if draft.startDate:
            draft.preferredDate = draft.startDate
    else:
        if not draft.preferredDate:
            draft.preferredDate = validate_iso_date(extracted.preferred_date)

    if not draft.title:
        if extracted.title:
            draft.title = extracted.title[:200]
        elif draft.description:
            draft.title = _fallback_title(draft.description)

    if request_type == RequestType.ANONYMOUS:
        draft.is_anonymous = True

    if is_leave:
        # Deterministic, never GPT-controlled - see LEAVE_DEPARTMENT.
        draft.department = LEAVE_DEPARTMENT

    missing = _filter_missing_fields(gpt_missing_fields, draft, intent=intent)

    if not draft.description and not any(
        m in field.lower() for field in missing for m in _MISSING_DESCRIPTION_MARKERS
    ):
        missing.append("more detail about what's going on")

    if not draft.category and not any(
        m in field.lower() for field in missing for m in _MISSING_CATEGORY_MARKERS
    ):
        label = "leave type" if is_leave else "category"
        missing.append(label)

    if is_leave:
        if invalid_range and not any(
            "range" in field.lower() or "corrected" in field.lower()
            for field in missing
        ):
            missing.append(
                "a corrected leave date range (the end date must be on or "
                "after the start date)"
            )
        if not draft.startDate and not any(
            m in field.lower() for field in missing for m in _MISSING_START_DATE_MARKERS
        ):
            missing.append("the leave start date")
        if not draft.endDate and not any(
            m in field.lower() for field in missing for m in _MISSING_END_DATE_MARKERS
        ):
            missing.append("the leave end date")

    return draft, missing


def reclassify_other_category(
    title: str,
    description: str,
    *,
    classify_ticket=default_classify_ticket,
) -> Optional[str]:
    """
    A Standard/Anonymous draft landed on "Other". Reuse Saketh's existing,
    already-wired-into-real-ticket-submission classifier
    (agents.orchestrator.classify_ticket) - the same one
    services/ticket_service.py calls at actual submission time - rather
    than building a second classifier inside the chatbot. classify_ticket
    never raises, so this only guards against it returning something that
    doesn't map onto the Standard Request form's own category vocabulary.
    Returns None (safe fallback - leave the draft at "Other", a real
    allowed value) when nothing confidently maps.
    """

    try:
        classification = classify_ticket(title, description)
    except Exception:
        return None
    return _DEPARTMENT_TO_STANDARD_CATEGORY.get(classification.department)
