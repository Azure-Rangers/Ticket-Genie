from backend.services.ai_service import ai_service


def predict_category(title: str, description: str) -> str:
    """
    Use GPT-5.2 to classify a ticket into the appropriate department.
    """

    prompt = f"""
You are the category classification agent for an internal company helpdesk.

Classify the ticket into exactly one category:

HR
IT
Accounting
Upper Management

Use the following routing rules.

HR:
- Benefits and employee policies
- Hiring, onboarding, offboarding, and termination
- Employee relations and workplace concerns
- Harassment, discrimination, workplace conduct, or personnel matters
- General HR questions that do not involve leave requests

IT:
- Laptops, computers, phones, printers, or company devices
- Passwords, login problems, accounts, permissions, or technical access
- Email, Teams, VPN, Wi-Fi, networks, or connectivity
- Software, applications, installations, and technical errors
- Cybersecurity or suspicious technical activity

Accounting:
- Payroll amounts or payroll discrepancies
- Expense reports and reimbursements
- Invoices, billing, vendor payments, and purchasing
- Financial transactions or accounting-related issues

Upper Management:
- ALL leave-related requests, including PTO, vacation, sick leave,
  maternity/paternity leave, personal leave, or other time-off requests
- Requests that require management approval
- Major organizational or strategic concerns
- Issues requiring senior leadership or executive review
- Cross-department matters that cannot reasonably be resolved by HR,
  IT, or Accounting
- Serious escalations where executive oversight is genuinely required

CRITICAL BUSINESS RULE:
Any request for leave, PTO, vacation, sick leave, maternity leave,
paternity leave, personal leave, or other time off MUST be classified
as Upper Management.

This rule overrides the normal HR classification.

Examples:
- "I want to take PTO next Friday" -> Upper Management
- "I need maternity leave" -> Upper Management
- "Can I take two sick days next week?" -> Upper Management
- "What benefits are included in my health plan?" -> HR
- "My paycheck amount is incorrect" -> Accounting
- "I cannot log into the payroll system" -> IT

Important rules:
- Choose the department primarily responsible for resolving the issue.
- Consider the meaning of the entire ticket, not individual keywords.
- Urgency does NOT automatically mean Upper Management.
- Priority and category are separate concepts.
- Do not invent information.
- Return ONLY one exact value:

HR
IT
Accounting
Upper Management

Ticket title:
{title}

Ticket description:
{description}
"""

    result = ai_service.generate(prompt).strip()

    valid_categories = {
        "HR",
        "IT",
        "Accounting",
        "Upper Management",
    }

    if result not in valid_categories:
        return "HR"

    return result