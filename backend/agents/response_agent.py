# backend/agents/response_agent.py

from pydantic import BaseModel, Field

from backend.services.ai_service import ai_service as default_ai_service


class EmployeeResponse(BaseModel):
    message: str
    suggested_actions: list[str] = Field(default_factory=list)
    safety_notice_required: bool = False


RESPONSE_PROMPT = """
You are the suggested-response agent for TicketGenie.

Draft a concise professional response for a human support agent to review.

Important rules:
- Do not claim an action was completed unless explicitly stated.
- Do not claim something was escalated, approved, resolved, assigned,
  investigated, or fixed unless that is known.
- Do not invent company policy.
- Do not promise a resolution time.
- For sensitive HR, security, or executive matters, keep the response cautious.
- Ask for missing information only when it is actually needed.
- suggested_actions should contain useful next steps for the human agent.
- safety_notice_required should be true for sensitive/high-risk cases.

Return:
- message
- suggested_actions
- safety_notice_required
"""


def draft_response(
    title: str,
    description: str,
    *,
    category: str,
    priority: str,
    queue: str,
    ai_service=default_ai_service,
) -> EmployeeResponse:
    user_content = f"""
Ticket title:
{title}

Ticket description:
{description}

Category:
{category}

Priority:
{priority}

Assigned queue:
{queue}
"""

    return ai_service.generate(
        system_prompt=RESPONSE_PROMPT,
        user_content=user_content,
        response_model=EmployeeResponse,
    )
