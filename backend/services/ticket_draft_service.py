"""
Ticket Drafting Agent.

Extracts whatever it safely can from the user's own words into a
TicketDraft that matches models.ticket.TicketCreate exactly. It never
invents facts and never sets `priority` or `department` - those are
internal routing fields owned by Saketh's classification/prioritization
agents (backend/agents/*), not something the chatbot should guess. The
resulting draft is always returned for the user to review/edit; nothing is
ever auto-submitted here.
"""

import re
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from models.chatbot import TicketDraft

_WORD_PATTERN_CACHE = {}


def contains_keyword(text: str, keyword: str) -> bool:
    """
    Membership check for a keyword list. Single-word keywords are matched
    on word boundaries so short tokens (e.g. "pto", "hr") don't false-match
    inside unrelated words (e.g. "laptop", "threshold"); phrases containing
    a space are matched as plain substrings since their own word boundaries
    already make accidental embedding unlikely.
    """

    if " " in keyword:
        return keyword in text

    pattern = _WORD_PATTERN_CACHE.get(keyword)
    if pattern is None:
        pattern = re.compile(rf"\b{re.escape(keyword)}\b")
        _WORD_PATTERN_CACHE[keyword] = pattern
    return bool(pattern.search(text))


def contains_any_keyword(text: str, keywords) -> bool:
    return any(contains_keyword(text, keyword) for keyword in keywords)


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

_CATEGORY_KEYWORDS = [
    (
        "IT & Technology",
        (
            "laptop",
            "computer",
            "password",
            "login",
            "vpn",
            "wifi",
            "wi-fi",
            "software",
            "printer",
            "teams",
            "email",
            "network",
            "access",
            "account locked",
        ),
    ),
    (
        "Account Management",
        (
            "reimbursement",
            "payroll",
            "paycheck",
            "salary",
            "invoice",
            "expense",
            "billing",
            "vendor payment",
        ),
    ),
    (
        "HR & Workforce Operations",
        (
            "benefits",
            "onboarding",
            "offboarding",
            "harassment",
            "hr",
            "employee relations",
            "policy",
        ),
    ),
    (
        "Upper Executive Management",
        ("executive", "strategic", "leadership decision", "organizational"),
    ),
]

_WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

MIN_DESCRIPTION_WORDS = 6


def guess_category(text: str) -> Optional[str]:
    lowered = text.lower()
    for category, keywords in _CATEGORY_KEYWORDS:
        if contains_any_keyword(lowered, keywords):
            return category
    return None


def guess_leave_type(text: str) -> Optional[str]:
    lowered = text.lower()
    if contains_any_keyword(lowered, ("pto", "paid time off", "vacation")):
        return "Paid Time Off (PTO)"
    if contains_any_keyword(lowered, ("medical", "sick")):
        return "Medical Leave"
    if contains_any_keyword(lowered, ("parental", "maternity", "paternity")):
        return "Parental Leave"
    if contains_any_keyword(lowered, ("bereavement",)):
        return "Bereavement"
    if contains_any_keyword(lowered, ("unpaid",)):
        return "Unpaid Leave"
    return None


def extract_preferred_date(
    text: str, *, today: Optional[datetime] = None
) -> Optional[str]:
    lowered = text.lower()
    reference = today or datetime.now()

    iso_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    if iso_match:
        return iso_match.group(1)

    for weekday_name, weekday_index in _WEEKDAYS.items():
        if weekday_name in lowered:
            days_ahead = (weekday_index - reference.weekday()) % 7
            days_ahead = days_ahead or 7
            target = reference + timedelta(days=days_ahead)
            return target.strftime("%Y-%m-%d")

    if "tomorrow" in lowered:
        return (reference + timedelta(days=1)).strftime("%Y-%m-%d")

    return None


def derive_title(text: str, *, max_words: int = 10) -> str:
    first_sentence = re.split(r"[.!?\n]", text.strip())[0].strip()
    words = first_sentence.split()
    if not words:
        return "Support Request"
    title = " ".join(words[:max_words])
    return title[:1].upper() + title[1:]


def _combined_text(message: str, history_user_messages: List[str]) -> str:
    return " ".join([*history_user_messages, message]).strip()


def _accumulate_description(
    draft: TicketDraft, message: str, combined: str
) -> str:
    """
    Fold a new message into the draft's running description without losing
    earlier turns, even if the caller doesn't resend full chat history.
    """

    if draft.description and message not in draft.description:
        return f"{draft.description} {message}".strip()
    return draft.description or combined


def build_support_draft(
    message: str,
    *,
    history_user_messages: List[str] = None,
    existing_draft: Optional[TicketDraft] = None,
) -> Tuple[TicketDraft, List[str]]:
    """Build/extend a general support-issue ticket draft.

    Returns (draft, missing_fields).
    """

    history_user_messages = history_user_messages or []
    combined = _combined_text(message, history_user_messages)
    draft = existing_draft.model_copy() if existing_draft else TicketDraft()
    draft.description = _accumulate_description(draft, message, combined)

    if not draft.title:
        draft.title = derive_title(draft.description)

    if not draft.category:
        draft.category = guess_category(draft.description)

    if not draft.preferredDate:
        date = extract_preferred_date(draft.description)
        if date:
            draft.preferredDate = date

    missing: List[str] = []
    if len(draft.description.split()) < MIN_DESCRIPTION_WORDS:
        missing.append("description")
    if not draft.category:
        missing.append("category")

    return draft, missing


def build_leave_draft(
    message: str,
    *,
    history_user_messages: List[str] = None,
    existing_draft: Optional[TicketDraft] = None,
) -> Tuple[TicketDraft, List[str]]:
    """
    Build/extend a Leave Management draft using the existing TicketCreate
    schema. The Standard Request form's dedicated Leave Management tab
    doesn't map onto TicketCreate 1:1 (it has separate start/end date
    fields that TicketCreate doesn't), so per the "don't invent fields"
    rule: leave type -> category (using the exact existing leaveType
    values), start date -> preferredDate (the only date field the schema
    has), and the leave dates/reason are folded into description text.
    """

    history_user_messages = history_user_messages or []
    combined = _combined_text(message, history_user_messages)
    draft = existing_draft.model_copy() if existing_draft else TicketDraft()
    draft.description = _accumulate_description(draft, message, combined)

    if not draft.category:
        draft.category = guess_leave_type(draft.description)

    start_date = extract_preferred_date(draft.description)
    if start_date and not draft.preferredDate:
        draft.preferredDate = start_date

    if not draft.title:
        leave_label = draft.category or "Leave"
        draft.title = f"{leave_label} Request"

    missing: List[str] = []
    if not draft.category:
        missing.append("leave type (PTO, Medical, Parental, Bereavement, or Unpaid)")
    if not draft.preferredDate:
        missing.append("start date")
    if len(draft.description.split()) < MIN_DESCRIPTION_WORDS:
        missing.append("reason for the leave")

    return draft, missing
