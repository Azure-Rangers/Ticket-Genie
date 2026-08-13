from backend.services.ai_service import ai_service


def predict_priority(title: str, description: str) -> str:
    """
    Use GPT-5.2 to classify ticket priority.
    """

    prompt = f"""
You are the priority classification agent for an internal company helpdesk.

Classify the ticket into exactly one priority level:

Low
Medium
High

Use the following guidelines:

HIGH:
- Critical business function is blocked
- Employee cannot perform essential work
- Security, account compromise, or serious access risk
- Payroll or another time-sensitive business process is at risk
- Multiple employees or an entire team are affected
- Major deadline or business impact requires immediate attention

MEDIUM:
- Employee's work is meaningfully affected but they can continue working
- Software, hardware, HR, accounting, or workplace issue needs attention
- Problem is recurring or causing moderate disruption
- There is a reasonable time constraint but no immediate critical impact

LOW:
- General question or informational request
- Routine HR, IT, accounting, or management request
- Minor inconvenience with little business impact
- No meaningful urgency or deadline

Important rules:
- Judge priority by actual business impact, not emotional wording.
- Do not classify something as High just because the user says "urgent",
  "ASAP", or uses strong language.
- Department does not automatically determine priority.
- Upper Management tickets are not automatically High.
- Consider both title and description.
- If information is limited, choose the most reasonable priority without
  inventing facts.
- Return ONLY one exact value:
  Low
  Medium
  High

Ticket title:
{title}

Ticket description:
{description}
"""

    result = ai_service.generate(prompt).strip()

    if result not in {"Low", "Medium", "High"}:
        return "Medium"

    return result