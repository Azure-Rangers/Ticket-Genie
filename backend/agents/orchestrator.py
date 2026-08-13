# backend/agents/orchestrator.py

from backend.agents.category_agent import categorize_ticket
from backend.agents.priority_agent import prioritize_ticket
from backend.agents.response_agent import draft_response
from backend.agents.routing_agent import route_ticket
from backend.agents.summary_agent import summarize_ticket


def process_ticket_with_ai(title: str, description: str) -> dict:
    category = categorize_ticket(title, description)

    priority = prioritize_ticket(
        title,
        description,
        category=category.category.value,
    )

    summary = summarize_ticket(title, description)

    routing = route_ticket(
        title,
        description,
        category=category.category,
        priority=priority.priority.value,
    )

    response = draft_response(
        title,
        description,
        category=category.category.value,
        priority=priority.priority.value,
        queue=routing.queue,
    )

    return {
        "category": category.model_dump(),
        "priority": priority.model_dump(),
        "summary": summary.model_dump(),
        "routing": routing.model_dump(),
        "suggested_response": response.model_dump(),
    }