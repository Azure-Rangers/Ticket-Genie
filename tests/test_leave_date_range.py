"""
Leave Management start/end date tests.

Previously TicketDraft/ExtractedTicketFields only had a single
preferredDate, and the chatbot prompt explicitly forced preferred_date to
the START of any range while only mentioning the end date in free-text
description - meaning the frontend never had an end-date value to
prefill leaveEndDate with. TicketDraft now carries explicit
startDate/endDate (backend/models/chatbot.py), fed by ExtractedTicketFields
.start_date/.end_date (backend/agents/chatbot_agent.py), merged
deterministically in ticket_draft_service.merge_extracted_fields():
- both given -> both stored, no missing fields
- only one given -> only the other is asked for (never re-asking for the
  one already known)
- a reversed range (end before start) is never silently accepted,
  flipped, or "corrected" - it's rejected and the user is asked to fix it
- preferredDate is kept as an alias for startDate for backward
  compatibility with anything still reading it (ticket submission).

All GPT calls are faked - no live Azure requests.
"""

from agents.chatbot_agent import ChatActionType, ChatbotDecision, ExtractedTicketFields
from models.chatbot import ChatIntent, ChatRequest, RequestType, TicketDraft
from services import chatbot_service
from services.ticket_draft_service import merge_extracted_fields


class FakeAIService:
    def __init__(self, decision):
        self.decision = decision

    def generate(self, *, system_prompt, user_content, response_model):
        return self.decision


def _no_ticket_found(ticket_id):
    return None


def _no_classify_call(*args, **kwargs):
    raise AssertionError("classify_ticket must not be called for leave drafts")


def ask(message, *, decision, **kwargs):
    request = ChatRequest(message=message, **kwargs)
    return chatbot_service.handle_message(
        request,
        ai_service=FakeAIService(decision),
        ticket_lookup=_no_ticket_found,
        classify_ticket=_no_classify_call,
    )


def _leave_decision(**overrides):
    fields = dict(
        intent=ChatIntent.LEAVE_MANAGEMENT,
        action=ChatActionType.SHOW_TICKET_DRAFT,
        message="Here's your leave request.",
        ticket_fields=ExtractedTicketFields(
            description="Requesting PTO.", category="Paid Time Off (PTO)"
        ),
        missing_fields=[],
        request_type=RequestType.LEAVE_MANAGEMENT,
    )
    fields.update(overrides)
    return ChatbotDecision(**fields)


# ---------------------------------------------------------------------------
# merge_extracted_fields() - deterministic date-range merge logic
# ---------------------------------------------------------------------------


def test_both_dates_supplied_together_are_both_stored():
    extracted = ExtractedTicketFields(
        description="PTO trip.",
        category="Paid Time Off (PTO)",
        start_date="2026-08-20",
        end_date="2026-08-28",
    )
    draft, missing = merge_extracted_fields(
        extracted,
        existing_draft=None,
        gpt_missing_fields=[],
        intent=ChatIntent.LEAVE_MANAGEMENT,
    )
    assert draft.startDate == "2026-08-20"
    assert draft.endDate == "2026-08-28"
    assert draft.preferredDate == "2026-08-20"
    assert missing == []


def test_only_start_supplied_asks_only_for_end():
    extracted = ExtractedTicketFields(
        description="Medical leave starting soon.",
        category="Medical Leave",
        start_date="2026-08-25",
    )
    draft, missing = merge_extracted_fields(
        extracted,
        existing_draft=None,
        gpt_missing_fields=[],
        intent=ChatIntent.LEAVE_MANAGEMENT,
    )
    assert draft.startDate == "2026-08-25"
    assert draft.endDate is None
    assert missing == ["the leave end date"]


def test_only_end_supplied_asks_only_for_start():
    extracted = ExtractedTicketFields(
        description="Returning from leave on this date.",
        category="Medical Leave",
        end_date="2026-08-28",
    )
    draft, missing = merge_extracted_fields(
        extracted,
        existing_draft=None,
        gpt_missing_fields=[],
        intent=ChatIntent.LEAVE_MANAGEMENT,
    )
    assert draft.endDate == "2026-08-28"
    assert draft.startDate is None
    assert missing == ["the leave start date"]


def test_both_dates_present_produces_no_date_follow_up():
    existing = TicketDraft(
        description="PTO.",
        category="Paid Time Off (PTO)",
        startDate="2026-08-20",
        endDate="2026-08-28",
    )
    draft, missing = merge_extracted_fields(
        ExtractedTicketFields(),
        existing_draft=existing,
        gpt_missing_fields=[],
        intent=ChatIntent.LEAVE_MANAGEMENT,
    )
    assert not any("date" in m.lower() for m in missing)


def test_start_then_end_across_two_turns_fills_both():
    draft1, missing1 = merge_extracted_fields(
        ExtractedTicketFields(
            description="Medical leave.",
            category="Medical Leave",
            start_date="2026-08-25",
        ),
        existing_draft=None,
        gpt_missing_fields=[],
        intent=ChatIntent.LEAVE_MANAGEMENT,
    )
    assert missing1 == ["the leave end date"]

    draft2, missing2 = merge_extracted_fields(
        ExtractedTicketFields(end_date="2026-08-30"),
        existing_draft=draft1,
        gpt_missing_fields=[],
        intent=ChatIntent.LEAVE_MANAGEMENT,
    )
    assert draft2.startDate == "2026-08-25"
    assert draft2.endDate == "2026-08-30"
    assert missing2 == []


def test_reversed_range_in_one_turn_is_rejected_not_flipped():
    extracted = ExtractedTicketFields(
        description="PTO.",
        category="Paid Time Off (PTO)",
        start_date="2026-08-28",
        end_date="2026-08-20",
    )
    draft, missing = merge_extracted_fields(
        extracted,
        existing_draft=None,
        gpt_missing_fields=[],
        intent=ChatIntent.LEAVE_MANAGEMENT,
    )
    # Never silently flipped/corrected - both rejected, draft stays empty.
    assert draft.startDate is None
    assert draft.endDate is None
    assert any("range" in m.lower() for m in missing)


def test_reversed_range_across_turns_rejects_the_conflicting_new_value():
    existing = TicketDraft(
        description="PTO.", category="Paid Time Off (PTO)", startDate="2026-08-28"
    )
    draft, missing = merge_extracted_fields(
        ExtractedTicketFields(end_date="2026-08-20"),
        existing_draft=existing,
        gpt_missing_fields=[],
        intent=ChatIntent.LEAVE_MANAGEMENT,
    )
    # The already-known start date is preserved; the conflicting end date
    # is NOT merged in.
    assert draft.startDate == "2026-08-28"
    assert draft.endDate is None
    assert any("range" in m.lower() for m in missing)


def test_invalid_iso_dates_are_rejected_not_guessed():
    extracted = ExtractedTicketFields(
        description="PTO.",
        category="Paid Time Off (PTO)",
        start_date="not-a-date",
        end_date="2026-13-40",
    )
    draft, missing = merge_extracted_fields(
        extracted,
        existing_draft=None,
        gpt_missing_fields=[],
        intent=ChatIntent.LEAVE_MANAGEMENT,
    )
    assert draft.startDate is None
    assert draft.endDate is None
    assert "the leave start date" in missing
    assert "the leave end date" in missing


def test_old_persisted_draft_with_only_preferred_date_is_treated_as_start():
    # Backward compatibility: a draft saved before startDate/endDate
    # existed only had preferredDate.
    existing = TicketDraft(
        description="PTO.", category="Paid Time Off (PTO)", preferredDate="2026-08-20"
    )
    draft, missing = merge_extracted_fields(
        ExtractedTicketFields(end_date="2026-08-28"),
        existing_draft=existing,
        gpt_missing_fields=[],
        intent=ChatIntent.LEAVE_MANAGEMENT,
    )
    assert draft.startDate == "2026-08-20"
    assert draft.endDate == "2026-08-28"
    assert missing == []


def test_gpt_missing_fields_never_repeat_a_known_side():
    # GPT's own free-text missing_fields must not cause a re-ask for a
    # side that's already known, even if GPT forgets to drop it.
    existing = TicketDraft(
        description="PTO.", category="Paid Time Off (PTO)", startDate="2026-08-20"
    )
    draft, missing = merge_extracted_fields(
        ExtractedTicketFields(),
        existing_draft=existing,
        gpt_missing_fields=["the start date please", "the end date"],
        intent=ChatIntent.LEAVE_MANAGEMENT,
    )
    assert not any(
        "start date" in m.lower() and "leave" not in m.lower() for m in missing
    )
    assert any("end date" in m.lower() for m in missing)


def test_standard_flow_preferred_date_unaffected_by_leave_changes():
    extracted = ExtractedTicketFields(
        description="Reimbursement request.",
        category="Account Management",
        preferred_date="2026-08-22",
    )
    draft, missing = merge_extracted_fields(
        extracted,
        existing_draft=None,
        gpt_missing_fields=[],
        intent=ChatIntent.SUPPORT_ISSUE,
    )
    assert draft.preferredDate == "2026-08-22"
    assert draft.startDate is None
    assert draft.endDate is None


# ---------------------------------------------------------------------------
# Full handle_message() flow
# ---------------------------------------------------------------------------


def test_pto_from_august_20_to_28_extracts_correct_range():
    decision = _leave_decision(
        ticket_fields=ExtractedTicketFields(
            description="Requesting PTO from August 20 to August 28.",
            category="Paid Time Off (PTO)",
            start_date="2026-08-20",
            end_date="2026-08-28",
        )
    )
    response = ask(
        "I need PTO from August 20 to August 28.",
        decision=decision,
        active_intent=ChatIntent.LEAVE_MANAGEMENT,
    )
    assert response.ticket_draft.startDate == "2026-08-20"
    assert response.ticket_draft.endDate == "2026-08-28"
    assert response.ready_for_review is True
    assert response.ticket_draft.department == "Upper Management"


def test_medical_leave_starting_august_25_asks_for_end_only():
    decision = _leave_decision(
        message="Got it - when will your leave end?",
        ticket_fields=ExtractedTicketFields(
            description="Medical leave starting August 25.",
            category="Medical Leave",
            start_date="2026-08-25",
        ),
        missing_fields=["the end date"],
    )
    response = ask(
        "I need medical leave starting August 25.",
        decision=decision,
        active_intent=ChatIntent.LEAVE_MANAGEMENT,
    )
    assert response.ready_for_review is False
    assert response.ticket_draft.startDate == "2026-08-25"
    assert response.ticket_draft.endDate is None
    assert response.missing_fields == ["the end date"]
    assert not any("start date" in m.lower() for m in response.missing_fields)


def test_ready_for_review_requires_both_dates():
    decision = _leave_decision(
        ticket_fields=ExtractedTicketFields(
            description="PTO next week.",
            category="Paid Time Off (PTO)",
            start_date="2026-08-20",
        )
    )
    response = ask(
        "I want PTO starting next week.",
        decision=decision,
        active_intent=ChatIntent.LEAVE_MANAGEMENT,
    )
    assert response.ready_for_review is False


def test_invalid_range_end_to_end_does_not_go_ready_for_review():
    decision = _leave_decision(
        ticket_fields=ExtractedTicketFields(
            description="PTO.",
            category="Paid Time Off (PTO)",
            start_date="2026-08-28",
            end_date="2026-08-20",
        )
    )
    response = ask(
        "I need PTO from August 28 to August 20.",
        decision=decision,
        active_intent=ChatIntent.LEAVE_MANAGEMENT,
    )
    assert response.ready_for_review is False
    assert response.ticket_draft.startDate is None
    assert response.ticket_draft.endDate is None
