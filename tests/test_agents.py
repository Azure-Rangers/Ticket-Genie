from agents.category_agent import (
    CATEGORY_PROMPT,
    CategoryDecision,
    TicketCategory,
    categorize_ticket,
)
from agents.priority_agent import PriorityDecision, TicketPriority, prioritize_ticket
from agents.response_agent import EmployeeResponse, draft_response
from agents.routing_agent import RoutingDecision, route_ticket
from agents.summary_agent import TicketSummary, summarize_ticket


class FakeAIService:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def generate(self, *, system_prompt, user_content, response_model):
        self.calls.append((system_prompt, user_content, response_model))
        return self.responses[response_model]


def test_category_agent_uses_closed_corporate_taxonomy():
    expected = CategoryDecision(
        category=TicketCategory.ACCOUNTING,
        confidence=0.96,
        rationale="Payroll owns incorrect salary payments.",
    )
    service = FakeAIService({CategoryDecision: expected})

    result = categorize_ticket(
        "Incorrect paycheck", "My overtime was not included.", ai_service=service
    )

    assert result == expected
    assert {item.value for item in TicketCategory} == {
        "HR",
        "IT",
        "Accounting",
        "Upper Management",
    }
    assert "Payroll" in CATEGORY_PROMPT
    assert "Incorrect paycheck" in service.calls[0][1]


def test_priority_agent_uses_closed_priority_scale():
    expected = PriorityDecision(
        priority=TicketPriority.HIGH,
        confidence=0.9,
        rationale="The report describes an active account compromise.",
        needs_human_review=True,
    )
    service = FakeAIService({PriorityDecision: expected})

    result = prioritize_ticket(
        "Account takeover",
        "Someone is actively using my account.",
        category="IT",
        ai_service=service,
    )

    assert result == expected
    assert {item.value for item in TicketPriority} == {"Low", "Medium", "High"}


def test_routing_agent_accepts_category_enum():
    expected = RoutingDecision(
        destination=TicketCategory.IT,
        queue="IT - Security",
        escalation_required=True,
        rationale="Active security incidents require the security queue.",
    )
    service = FakeAIService({RoutingDecision: expected})

    result = route_ticket(
        "Suspicious login",
        "An unknown login is active.",
        category=TicketCategory.IT,
        priority="High",
        ai_service=service,
    )

    assert result == expected
    assert "Assigned category: IT" in service.calls[0][1]


def test_summary_and_response_agents_return_typed_results():
    summary = TicketSummary(
        summary="The employee reports being unable to access the VPN.",
        requested_action="Restore VPN access.",
        key_facts=["VPN access is unavailable"],
        missing_information=["Displayed error message"],
    )
    response = EmployeeResponse(
        message="Your IT request has been received and assigned High priority.",
        suggested_actions=["Use the official IT helpdesk channel"],
        safety_notice_required=False,
    )
    service = FakeAIService({TicketSummary: summary, EmployeeResponse: response})

    assert summarize_ticket(
        "VPN unavailable", "I cannot connect.", ai_service=service
    ) == summary
    assert draft_response(
        "VPN unavailable",
        "I cannot connect.",
        category="IT",
        priority="High",
        queue="IT - Service Desk",
        ai_service=service,
    ) == response
