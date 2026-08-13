"""Tests for the AI ticket classification module (backend/agents + ai_service.py).

These tests only exercise mock mode and monkeypatched stand-ins for the
Azure call, so they never require real Azure credentials or make network
requests.
"""

from __future__ import annotations

import pytest
from agents import orchestrator
from agents.orchestrator import classify_ticket
from services import ai_service


@pytest.fixture(autouse=True)
def _mock_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("USE_MOCK_AI", "true")
    monkeypatch.delenv("AI_CONFIDENCE_THRESHOLD", raising=False)


def test_it_ticket_identity_and_access_management() -> None:
    result = classify_ticket(
        "Cannot access company account",
        "My account is locked and I cannot log in.",
    )
    assert result.department == "IT Team"
    assert result.category == "Identity and Access Management"


def test_accounting_ticket_reimbursement() -> None:
    result = classify_ticket(
        "Travel reimbursement missing",
        "My reimbursement has not been paid.",
    )
    assert result.department == "Accounting Team"
    assert result.category == "Reimbursement Requests"


def test_workplace_ticket_badge_registration() -> None:
    result = classify_ticket(
        "Badge stopped working",
        "I cannot enter the office because my badge stopped working.",
    )
    assert result.department == "Workplace Operations Team"
    assert result.category == "Badge Registration"


def test_hr_ticket_benefits_inquiries() -> None:
    result = classify_ticket(
        "Benefits question",
        "I have a question about my employee benefits.",
    )
    assert result.department == "HR Team"
    assert result.category == "Benefits Inquiries"


def test_upper_management_ticket_company_wide_issue() -> None:
    result = classify_ticket(
        "Company-wide conflict escalation",
        "There is a serious company-wide conflict affecting operations.",
    )
    assert result.department == "Upper Management"


def test_company_wide_outage_is_critical_priority() -> None:
    result = classify_ticket(
        "Company-wide login outage",
        "Employees across the company cannot access internal systems.",
    )
    assert result.priority == "Critical"


def test_urgent_word_alone_does_not_force_critical_priority() -> None:
    result = classify_ticket(
        "URGENT mouse request",
        "I want another mouse but my current mouse still works.",
    )
    assert result.priority == "Low"


def test_low_confidence_result_flags_human_review(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        ai_service,
        "get_ai_classification",
        lambda title, description, context=None: {
            "department": "IT Team",
            "category": "Other IT Request",
            "priority": "Low",
            "confidence": 0.4,
            "reason": "Low-confidence stub result for testing.",
            "needs_human_review": False,
        },
    )

    result = classify_ticket(
        "Printer looks slightly different today",
        "Not sure if this matters, just noting it in case it's relevant.",
    )

    assert result.confidence == 0.4
    assert result.needs_human_review is True


def test_invalid_department_is_rejected_and_flagged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        ai_service,
        "get_ai_classification",
        lambda title, description, context=None: {
            "department": "Finance Team",  # not an allowed department
            "category": "Reimbursement Requests",
            "priority": "Medium",
            "confidence": 0.9,
            "reason": "Invalid department stub for testing.",
            "needs_human_review": False,
        },
    )

    result = classify_ticket(
        "This ticket has an invalid department",
        "Used to verify unknown departments are safely rejected.",
    )

    assert result.needs_human_review is True
    assert result.department == orchestrator.FALLBACK_DEPARTMENT
    assert result.confidence == 0.0


def test_invalid_category_for_department_is_rejected_and_flagged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        ai_service,
        "get_ai_classification",
        lambda title, description, context=None: {
            "department": "IT Team",
            "category": "Reimbursement Requests",  # not a valid IT Team category
            "priority": "Medium",
            "confidence": 0.9,
            "reason": "Mismatched department/category stub for testing.",
            "needs_human_review": False,
        },
    )

    result = classify_ticket(
        "This ticket has a mismatched department and category",
        "Used to verify invalid taxonomy combinations are safely rejected.",
    )

    assert result.needs_human_review is True
    assert result.department == orchestrator.FALLBACK_DEPARTMENT
    assert result.category == orchestrator.FALLBACK_CATEGORY


def test_invalid_priority_is_rejected_and_flagged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        ai_service,
        "get_ai_classification",
        lambda title, description, context=None: {
            "department": "IT Team",
            "category": "Laptop Requests",
            "priority": "Urgent!!",  # not an allowed priority
            "confidence": 0.9,
            "reason": "Invalid priority stub for testing.",
            "needs_human_review": False,
        },
    )

    result = classify_ticket(
        "This ticket has an invalid priority value",
        "Used to verify unknown priority values are safely rejected.",
    )

    assert result.needs_human_review is True
    assert result.priority == orchestrator.FALLBACK_PRIORITY
    assert result.confidence == 0.0


def test_confidence_out_of_range_is_rejected_and_flagged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        ai_service,
        "get_ai_classification",
        lambda title, description, context=None: {
            "department": "IT Team",
            "category": "Laptop Requests",
            "priority": "Medium",
            "confidence": 1.5,  # out of the allowed 0..1 range
            "reason": "Out-of-range confidence stub for testing.",
            "needs_human_review": False,
        },
    )

    result = classify_ticket(
        "This ticket has an out-of-range confidence value",
        "Used to verify confidence bounds are enforced.",
    )

    assert result.needs_human_review is True
    assert result.confidence == 0.0


def test_azure_failure_is_caught_and_flags_human_review(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _boom(title: str, description: str, context=None):
        raise ai_service.AIServiceError("Azure OpenAI authentication failed.")

    monkeypatch.setattr(ai_service, "get_ai_classification", _boom)

    result = classify_ticket("Any ticket", "Any description long enough to be valid.")

    assert result.needs_human_review is True
    assert result.confidence == 0.0
    assert "AI classification unavailable" in result.reason


def test_real_mode_missing_configuration_raises_ai_service_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("USE_MOCK_AI", "false")
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_DEPLOYMENT", raising=False)

    with pytest.raises(ai_service.AIServiceError):
        ai_service.get_ai_classification("Title", "Description text here.")


def test_empty_title_is_rejected_without_calling_ai_service(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _fail_if_called(*args, **kwargs):
        raise AssertionError("AI service should not be called for invalid input.")

    monkeypatch.setattr(ai_service, "get_ai_classification", _fail_if_called)

    result = classify_ticket("   ", "Some description that is long enough.")

    assert result.needs_human_review is True
    assert result.confidence == 0.0


def test_mock_mode_reason_is_labeled_as_mock() -> None:
    result = classify_ticket(
        "Need a new laptop",
        "My current laptop is too slow for development work.",
    )
    assert result.reason.startswith("[MOCK]")
