from enum import Enum

from pydantic import BaseModel, Field

from backend.services.ai_service import ai_service as default_ai_service


class TicketPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class PriorityDecision(BaseModel):
    priority: TicketPriority
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
    needs_human_review: bool = False


PRIORITY_PROMPT = """
You are the priority classification agent for TicketGenie,
an internal company helpdesk.

Classify the ticket into exactly one priority:

Low
Medium
High

HIGH:
- Critical business function is blocked
- Employee cannot perform essential work
- Active security or account-compromise risk
- Time-sensitive payroll or business process is at risk
- Multiple employees or an entire team are affected
- Major deadline or significant business impact requires immediate attention

MEDIUM:
- Work is meaningfully affected but can continue
- Recurring or moderately disruptive issue
- HR, IT, Accounting, or management matter that needs timely attention
- There is a reasonable time constraint but no immediate critical impact

LOW:
- General question or informational request
- Routine request
- Minor inconvenience
- Little business impact
- No meaningful urgency or deadline

Important rules:
- Judge priority by actual business impact, not emotional wording.
- Words such as "urgent" or "ASAP" do not automatically mean High.
- Category and priority are separate concepts.
- Upper Management tickets are not automatically High.
- Do not invent missing facts.
- Set needs_human_review to true when the ticket is sensitive,
  ambiguous, high-risk, or would benefit from human judgment.

Return a structured priority decision containing:
- priority
- confidence from 0 to 1
- concise rationale
- needs_human_review
"""


def prioritize_ticket(
    title: str,
    description: str,
    *,
    category: str,
    ai_service=default_ai_service,
) -> PriorityDecision:
    user_content = f"""
Ticket title:
{title}

Ticket description:
{description}

Assigned category:
{category}
"""

    return ai_service.generate(
        system_prompt=PRIORITY_PROMPT,
        user_content=user_content,
        response_model=PriorityDecision,
    )
