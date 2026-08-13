import json

from backend.services.ai_service import ai_service


def generate_suggested_response(
    title: str,
    description: str,
    category: str,
    priority: str,
) -> dict:
    """
    Use GPT-5.2 to decide whether a ticket should receive
    an AI-generated suggested response.

    The response is meant for a human support agent to review,
    edit, and send.
    """

    prompt = f"""
You are the suggested-response agent for an internal company helpdesk.

Your job has TWO parts:

1. Decide whether this ticket is appropriate for an AI-generated
   suggested response.
2. If appropriate, generate a concise professional draft that a human
   support agent can review, edit, and send.

Return valid JSON in exactly this shape:

{{
  "should_suggest_response": true,
  "suggested_response": "..."
}}

or:

{{
  "should_suggest_response": false,
  "suggested_response": null
}}

WHEN TO SUGGEST A RESPONSE:
- Routine or straightforward support questions
- Common IT troubleshooting guidance
- Simple process explanations
- Basic accounting or payroll follow-up questions
- General HR information where the answer does not require a sensitive judgment
- Tickets where a safe, useful first response can be drafted from the information provided

WHEN NOT TO SUGGEST A RESPONSE:
- Harassment, discrimination, threats, retaliation, or serious workplace conduct
- Highly sensitive employee-relations situations
- Legal or compliance issues requiring human judgment
- Serious security incidents or suspected account compromise
- Major executive or organizational escalations
- Situations where the correct answer depends on missing company policy or facts
- Situations where generating a response could falsely imply that an action,
  approval, investigation, escalation, or resolution has already occurred

IMPORTANT RULES:
- The draft is only a suggestion for a human agent.
- Never claim an action has already been completed unless the ticket explicitly says so.
- Never claim that a ticket has been escalated, approved, resolved, investigated,
  assigned, or fixed.
- Never invent company policies, deadlines, approvals, procedures, or facts.
- Never promise a specific resolution time.
- Keep suggested responses concise and professional.
- Acknowledge the employee's issue.
- If more information is needed, politely ask for the specific missing information.
- Do not include markdown formatting.
- Return ONLY valid JSON.

Ticket title:
{title}

Ticket description:
{description}

Category:
{category}

Priority:
{priority}
"""

    result = ai_service.generate(prompt).strip()

    try:
        parsed = json.loads(result)
    except json.JSONDecodeError:
        return {
            "should_suggest_response": False,
            "suggested_response": None,
        }

    should_suggest = parsed.get("should_suggest_response")
    suggested_response = parsed.get("suggested_response")

    if should_suggest is not True:
        return {
            "should_suggest_response": False,
            "suggested_response": None,
        }

    if not isinstance(suggested_response, str) or not suggested_response.strip():
        return {
            "should_suggest_response": False,
            "suggested_response": None,
        }

    return {
        "should_suggest_response": True,
        "suggested_response": suggested_response.strip(),
    }