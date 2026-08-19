"""Announcement AI Severity Classification and Management Service for TicketGenie."""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Optional

from sqlalchemy.orm import Session

from database.crud import get_announcements

logger = logging.getLogger(__name__)

SEVERITY_METADATA = {
    "critical": {
        "level": "critical",
        "label": "CRITICAL ALERT",
        "color_class": "severity-critical",
        "icon": "ph-warning-octagon",
    },
    "warning": {
        "level": "warning",
        "label": "SYSTEM NOTICE",
        "color_class": "severity-warning",
        "icon": "ph-warning",
    },
    "info": {
        "level": "info",
        "label": "ANNOUNCEMENT",
        "color_class": "severity-info",
        "icon": "ph-megaphone",
    },
}

CRITICAL_KEYWORDS = {
    "critical",
    "emergency",
    "outage",
    "security",
    "vulnerability",
    "incident",
    "breach",
    "ransomware",
    "sev-1",
    "p0",
    "down",
    "compromised",
    "attack",
    "zero-day",
}

WARNING_KEYWORDS = {
    "maintenance",
    "warning",
    "system alert",
    "downtime",
    "interruption",
    "scheduled",
    "upgrade",
    "patch",
    "degradation",
    "reboot",
    "advisory",
    "temporary",
}


def _classify_severity_heuristically(
    title: str,
    content: str,
    category: str = "",
) -> dict:
    """Deterministic NLP heuristic fallback for announcement severity classification."""
    combined = f"{category} {title} {content}".lower()
    words = set(re.findall(r"[a-z0-9\-]+", combined))

    if words & CRITICAL_KEYWORDS or any(kw in combined for kw in ["system down", "major outage", "security alert"]):
        meta = SEVERITY_METADATA["critical"]
        return {
            **meta,
            "confidence": 0.95,
            "reason": "Identified critical operational, security, or outage indicators.",
        }

    if words & WARNING_KEYWORDS or any(kw in combined for kw in ["system maintenance", "scheduled downtime"]):
        meta = SEVERITY_METADATA["warning"]
        return {
            **meta,
            "confidence": 0.90,
            "reason": "Identified scheduled maintenance, downtime, or operational advisory indicators.",
        }

    meta = SEVERITY_METADATA["info"]
    return {
        **meta,
        "confidence": 0.85,
        "reason": "Standard informational announcement or company update.",
    }


def classify_announcement_severity(
    title: str,
    content: str,
    category: Optional[str] = "General Alert",
) -> dict:
    """Classify the severity level of an announcement using Azure OpenAI or heuristic fallback."""
    category_str = category or "General Alert"

    # Fast heuristic check or fallback
    use_mock = os.getenv("USE_MOCK_AI", "false").lower() == "true"
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")

    if use_mock or not endpoint or not api_key:
        return _classify_severity_heuristically(title, content, category_str)

    try:
        import requests

        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.2")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
        url = f"{endpoint.rstrip('/')}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"

        prompt = f"""You are an enterprise system alert classifier.
Classify the following company announcement into one of three severity levels:
- "critical": For emergency outages, security breaches, active incidents, or major system failures.
- "warning": For scheduled maintenance, planned downtime, patches, or system degradation notices.
- "info": For general announcements, policy updates, company news, and informational bulletins.

Return ONLY a JSON object with:
{{
  "level": "critical" | "warning" | "info",
  "reason": "<one sentence explanation>",
  "confidence": <float between 0.0 and 1.0>
}}

Category: {category_str}
Title: {title}
Content: {content}
"""
        response = requests.post(
            url,
            headers={
                "api-key": api_key,
                "Content-Type": "application/json",
            },
            json={
                "messages": [
                    {"role": "system", "content": "You are a concise enterprise announcement classifier."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.0,
                "response_format": {"type": "json_object"},
            },
            timeout=5,
        )

        if response.status_code == 200:
            result = response.json()
            raw_text = result["choices"][0]["message"]["content"]
            parsed = json.loads(raw_text)
            level = (parsed.get("level") or "info").lower().strip()
            if level not in SEVERITY_METADATA:
                level = "info"
            meta = SEVERITY_METADATA[level]
            return {
                **meta,
                "confidence": float(parsed.get("confidence", 0.9)),
                "reason": str(parsed.get("reason", "")),
            }
    except Exception as exc:
        logger.warning(f"Azure OpenAI announcement classification failed, using fallback: {exc}")

    return _classify_severity_heuristically(title, content, category_str)


def get_latest_announcement_with_severity(db: Optional[Session] = None) -> dict:
    """Retrieve the most recent announcement and its AI-computed severity metadata."""
    announcements = get_announcements(db=db)
    if not announcements:
        return {"announcement": None, "severity": None}

    latest = announcements[0]
    severity = classify_announcement_severity(
        title=latest.get("title", ""),
        content=latest.get("content", ""),
        category=latest.get("category", ""),
    )

    return {
        "announcement": latest,
        "severity": severity,
    }
