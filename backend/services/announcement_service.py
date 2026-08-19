"""Announcement AI Severity Classification Service for TicketGenie."""

from enum import Enum
import logging
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.crud import get_announcements
from services.ai_service import ai_service

logger = logging.getLogger(__name__)


class SeverityLevelEnum(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class AnnouncementSeverityDecision(BaseModel):
    severity: SeverityLevelEnum = Field(
        default=SeverityLevelEnum.MEDIUM,
        description="Must be strictly one of: Critical, High, Medium, Low",
    )
    reason: str = Field(
        default="",
        description="Brief explanation of why this announcement is important for this role",
    )


SEVERITY_MAPPING = {
    "critical": {
        "level": "critical",
        "label": "CRITICAL ALERT",
        "color_class": "severity-critical",
        "icon": "ph-warning-octagon",
    },
    "high": {
        "level": "critical",
        "label": "HIGH PRIORITY",
        "color_class": "severity-critical",
        "icon": "ph-warning-octagon",
    },
    "medium": {
        "level": "warning",
        "label": "SYSTEM NOTICE",
        "color_class": "severity-warning",
        "icon": "ph-warning",
    },
    "low": {
        "level": "info",
        "label": "ANNOUNCEMENT",
        "color_class": "severity-info",
        "icon": "ph-megaphone",
    },
}


def _heuristic_fallback(title: str, content: str, category: str) -> str:
    combined = f"{category} {title} {content}".lower()
    if any(k in combined for k in [
        "critical", "emergency", "outage", "security", "breach", "incident",
        "down", "ransomware", "p0", "sev-1", "strike", "striking", "union",
        "walkout", "disaster", "evacuation", "fatal", "shutdown", "hazard",
        "urgent", "alert"
    ]):
        return "Critical"
    if any(k in combined for k in [
        "maintenance", "warning", "system alert", "downtime", "interruption",
        "patch", "upgrade", "degradation", "reboot", "advisory", "delay"
    ]):
        return "Medium"
    return "Low"


def classify_announcement_severity(
    title: str,
    content: str,
    category: Optional[str] = "General Alert",
    role: str = "Employee",
) -> dict:
    """Classify how important an announcement is using the AI model from the perspective of a company employee role."""
    category_str = category or "General Alert"
    role_str = role or "Employee"

    system_prompt = (
        f'You are an Employee working at a company with role "{role_str}" '
        f"and you are looking at an announcement."
    )

    user_content = f"""Tell me how important this announcement is in the following options:
Critical
High
Medium
Low

Announcement:
Title: {title}
Category: {category_str}
Content: {content}
"""

    severity_choice = "Medium"
    reason = ""

    try:
        import concurrent.futures
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        try:
            future = executor.submit(
                ai_service.generate,
                system_prompt=system_prompt,
                user_content=user_content,
                response_model=AnnouncementSeverityDecision,
                max_tokens=25,
            )
            decision: AnnouncementSeverityDecision = future.result(timeout=1.5)
            if decision and decision.severity:
                val = decision.severity.value if hasattr(decision.severity, "value") else str(decision.severity)
                severity_choice = val.strip()
                reason = decision.reason
        finally:
            executor.shutdown(wait=False, cancel_futures=True)
    except Exception as exc:
        logger.info(f"AI severity generation falling back to role-aware heuristic: {exc}")
        severity_choice = _heuristic_fallback(title, content, category_str)
        reason = "Classified based on announcement operational scope."

    normalized_choice = severity_choice.lower()
    meta = SEVERITY_MAPPING.get(normalized_choice, SEVERITY_MAPPING["medium"])

    return {
        **meta,
        "raw_severity": severity_choice,
        "role": role_str,
        "reason": reason,
    }


_SEVERITY_CACHE: dict[str, dict] = {}


def get_latest_announcement_with_severity(
    role: str = "Employee",
    db: Optional[Session] = None,
) -> dict:
    """Retrieve the most recent announcement and its AI-computed severity for the current user's role."""
    announcements = get_announcements(db=db)
    if not announcements:
        return {"announcement": None, "severity": None}

    latest = announcements[0]
    cache_key = f"{latest.get('id')}_{role}_{latest.get('title')}"
    if cache_key in _SEVERITY_CACHE:
        return {
            "announcement": latest,
            "severity": _SEVERITY_CACHE[cache_key],
        }

    severity = classify_announcement_severity(
        title=latest.get("title", ""),
        content=latest.get("content", ""),
        category=latest.get("category", ""),
        role=role,
    )
    _SEVERITY_CACHE[cache_key] = severity

    return {
        "announcement": latest,
        "severity": severity,
    }
