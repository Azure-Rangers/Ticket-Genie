"""Azure OpenAI client wrapper for AI ticket classification.

Responsible for:
- deciding whether to run in mock mode or call Azure OpenAI for real
- building the system prompt
- making the actual model request
- translating Azure/OpenAI SDK errors into a single AIServiceError

This module does NOT validate the classification result against the
department/category/priority taxonomy — that happens in
agents/orchestrator.py. This module only guarantees it returns either a
dict or raises AIServiceError.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Optional

from agents.category_agent import ALLOWED_CATEGORIES
from agents.priority_agent import ALLOWED_PRIORITIES, PRIORITY_DESCRIPTIONS

logger = logging.getLogger(__name__)

try:  # local .env support for developer machines; safe no-op if unavailable
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

DEFAULT_CONFIDENCE_THRESHOLD = 0.70
DEFAULT_AZURE_API_VERSION = "2024-08-01-preview"


class AIServiceError(Exception):
    """Raised whenever a classification request cannot be completed.

    The message is safe to log and safe to surface to callers — it never
    contains API keys, stack traces, or other sensitive internal details.
    """


def use_mock_ai() -> bool:
    """Return True when the module should use deterministic local rules
    instead of calling Azure OpenAI."""
    return os.getenv("USE_MOCK_AI", "true").strip().lower() in {"1", "true", "yes", "on"}


def get_confidence_threshold() -> float:
    """Return the minimum confidence below which a result must be flagged
    for human review."""
    raw = os.getenv("AI_CONFIDENCE_THRESHOLD", str(DEFAULT_CONFIDENCE_THRESHOLD))
    try:
        threshold = float(raw)
    except ValueError:
        logger.warning("Invalid AI_CONFIDENCE_THRESHOLD=%r, using default.", raw)
        return DEFAULT_CONFIDENCE_THRESHOLD
    return min(max(threshold, 0.0), 1.0)


def get_ai_classification(
    title: str,
    description: str,
    context: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Classify a ticket and return a raw (not-yet-validated) result dict.

    Raises AIServiceError if the classification cannot be produced.
    """
    if use_mock_ai():
        return _mock_classify(title, description, context)
    return _call_azure_openai(title, description, context)


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------


def build_system_prompt() -> str:
    departments_block = "\n".join(
        f"- {department}: {', '.join(categories)}"
        for department, categories in ALLOWED_CATEGORIES.items()
    )
    priorities_block = "\n".join(
        f"- {priority}: {PRIORITY_DESCRIPTIONS[priority]}" for priority in ALLOWED_PRIORITIES
    )

    return (
        "You are a workplace ticket classifier for an internal company "
        "helpdesk. Given a ticket title and description, classify it.\n\n"
        "Allowed departments and their allowed categories. You must choose "
        "exactly one department and exactly one category that belongs to "
        "that department. Never invent a department or category that is "
        "not in this list:\n"
        f"{departments_block}\n\n"
        "Priority levels:\n"
        f"{priorities_block}\n\n"
        "Rules:\n"
        "- Base priority on business impact, not on emotional language. "
        "The word \"urgent\" appearing in the ticket text does NOT by "
        "itself justify a \"Critical\" priority.\n"
        "- If the ticket is vague, could reasonably belong to more than "
        "one department, or is missing information needed to classify it "
        "confidently, lower your confidence and set needs_human_review "
        "to true.\n"
        "- If the ticket describes something unusually sensitive or "
        "high-risk (legal, safety, security, executive-level conflict), "
        "set needs_human_review to true even if you are otherwise "
        "confident.\n"
        "- \"reason\" must be one short, concise, factual sentence.\n"
        "- Respond with a single JSON object and no other text, matching "
        "exactly this shape and no additional keys:\n"
        "{\n"
        '  "department": string,\n'
        '  "category": string,\n'
        '  "priority": "Low" | "Medium" | "High" | "Critical",\n'
        '  "confidence": number between 0 and 1,\n'
        '  "reason": string,\n'
        '  "needs_human_review": boolean\n'
        "}"
    )


# ---------------------------------------------------------------------------
# Real Azure OpenAI call
# ---------------------------------------------------------------------------


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise AIServiceError(f"Missing required Azure OpenAI configuration: {name}.")
    return value


def _call_azure_openai(
    title: str,
    description: str,
    context: Optional[dict[str, Any]],
) -> dict[str, Any]:
    endpoint = _require_env("AZURE_OPENAI_ENDPOINT")
    api_key = _require_env("AZURE_OPENAI_API_KEY")
    deployment = _require_env("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", DEFAULT_AZURE_API_VERSION)

    try:
        from openai import (
            APIConnectionError,
            AuthenticationError,
            AzureOpenAI,
            NotFoundError,
            OpenAIError,
            RateLimitError,
        )
    except ImportError as exc:
        raise AIServiceError(
            "The 'openai' package is required for real AI mode but is not installed."
        ) from exc

    user_content = f"Title: {title}\nDescription: {description}"
    if context:
        user_content += f"\nAdditional context: {json.dumps(context, default=str)}"

    try:
        client = AzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version=api_version)
        response = client.chat.completions.create(
            model=deployment,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": user_content},
            ],
        )
    except AuthenticationError as exc:
        raise AIServiceError("Azure OpenAI authentication failed.") from exc
    except NotFoundError as exc:
        raise AIServiceError("Azure OpenAI deployment was not found.") from exc
    except RateLimitError as exc:
        raise AIServiceError("Azure OpenAI rate limit exceeded.") from exc
    except APIConnectionError as exc:
        raise AIServiceError("Could not connect to the Azure OpenAI endpoint.") from exc
    except OpenAIError as exc:
        logger.error("Azure OpenAI request failed: %s", exc)
        raise AIServiceError("Azure OpenAI request failed.") from exc
    except Exception as exc:  # unexpected SDK/transport failure
        logger.exception("Unexpected error calling Azure OpenAI.")
        raise AIServiceError("Unexpected error calling Azure OpenAI.") from exc

    raw_content = response.choices[0].message.content

    try:
        return json.loads(raw_content)
    except (json.JSONDecodeError, TypeError) as exc:
        logger.error("Azure OpenAI returned non-JSON content: %r", raw_content)
        raise AIServiceError("Azure OpenAI returned malformed output.") from exc


# ---------------------------------------------------------------------------
# Mock mode — deterministic local rules, no network calls
# ---------------------------------------------------------------------------

# category -> keywords that, if present in the ticket text, select it.
# Order matters: first department whose category matches wins.
_MOCK_KEYWORD_RULES: dict[str, dict[str, list[str]]] = {
    "IT Team": {
        "Identity and Access Management": [
            "password", "login", "log in", "account", "locked out",
            "access", "vpn", "credentials",
        ],
        "Laptop Requests": ["laptop"],
        "Software Licensing": ["software", "license", "licensing"],
    },
    "Accounting Team": {
        "Reimbursement Requests": ["reimbursement", "reimburse", "expense"],
        "Company Card Management": ["company card", "corporate card"],
        "Business Development Management": ["business development"],
    },
    "Workplace Operations Team": {
        "Badge Registration": ["badge"],
        "Maintenance": ["maintenance", "repair"],
        "Office Equipment Issues": [
            "office equipment", "mouse", "keyboard", "monitor", "printer",
            "desk", "chair",
        ],
    },
    "HR Team": {
        "Benefits Inquiries": ["benefits", "benefit"],
        "Onboarding and Offboarding": [
            "onboarding", "offboarding", "onboard", "offboard", "new hire",
        ],
        "Employee Relationships": [
            "employee relationship", "harassment", "coworker conflict",
            "workplace conflict",
        ],
    },
    "Upper Management": {
        "High-Impact Company Conflict": [
            "serious company-wide conflict", "major organizational conflict",
            "company-wide conflict",
        ],
        "Executive Review": ["executive issue", "executive review"],
        "Company-Wide Issue": ["company-wide issue", "company wide issue"],
    },
}

_CRITICAL_SIGNALS = [
    "company-wide", "company wide", "entire company", "all employees",
    "every employee", "many employees", "across the company",
    "safety concern", "security incident", "security breach",
    "data breach", "legal risk",
]
_LOW_SIGNALS = [
    "still works", "no rush", "not urgent", "just a question",
    "just curious", "whenever you get a chance",
]
_HIGH_SIGNALS = [
    "cannot work", "can't work", "unable to work", "blocked",
    "locked out", "cannot log in", "can't log in", "important deadline",
    "approaching deadline", "cannot access", "can't access",
]


def _mock_priority(text: str) -> str:
    if any(signal in text for signal in _CRITICAL_SIGNALS):
        return "Critical"
    if any(signal in text for signal in _LOW_SIGNALS):
        return "Low"
    if any(signal in text for signal in _HIGH_SIGNALS):
        return "High"
    return "Medium"


def _mock_classify(
    title: str,
    description: str,
    context: Optional[dict[str, Any]],
) -> dict[str, Any]:
    text = f"{title} {description}".lower()
    if context:
        text += " " + " ".join(str(value) for value in context.values()).lower()

    matches: list[tuple[str, str]] = []
    for department, categories in _MOCK_KEYWORD_RULES.items():
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                matches.append((department, category))

    priority = _mock_priority(text)

    if not matches:
        return {
            "department": "Upper Management",
            "category": "Other Management Issue",
            "priority": priority,
            "confidence": 0.3,
            "reason": "[MOCK] No keyword rule matched this ticket; routed for manual triage.",
            "needs_human_review": True,
        }

    department, category = matches[0]
    ambiguous = len({matched_department for matched_department, _ in matches}) > 1

    return {
        "department": department,
        "category": category,
        "priority": priority,
        "confidence": 0.55 if ambiguous else 0.95,
        "reason": (
            f"[MOCK] Deterministic keyword rule matched '{category}' under '{department}'."
        ),
        "needs_human_review": ambiguous,
    }
