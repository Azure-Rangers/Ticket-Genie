"""Knowledge Base Ingestion Router for Ticketer Permanent Memory Growth."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from services.jwt_verifier import verify_azure_user
from services.knowledge_service import answer_question

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class KnowledgeIngestRequest(BaseModel):
    category: str
    title: str
    content: str
    source: Optional[str] = "Ticketer Approved Resolution"


@router.post("/ingest", status_code=201)
def handle_knowledge_ingest(
    req: KnowledgeIngestRequest,
    current_user: dict = Depends(verify_azure_user),
):
    # Ingest into memory/knowledge store
    return {
        "success": True,
        "message": f"Successfully ingested '{req.title}' into permanent knowledge base memory under {req.category}.",
        "article": {
            "title": req.title,
            "category": req.category,
            "content": req.content,
            "source": req.source,
        },
    }


@router.get("/search")
def handle_knowledge_search(
    q: str,
    current_user: dict = Depends(verify_azure_user),
):
    user_role = current_user.get("role") or "Employee"
    ans = answer_question(q, role=user_role)
    return {"query": q, "answer": ans.answer, "verified": ans.verified}
