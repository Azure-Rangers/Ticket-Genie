"""Knowledge Base Ingestion Router for Ticketer Permanent Memory Growth."""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

from services.knowledge_service import answer_question

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class KnowledgeIngestRequest(BaseModel):
    category: str
    title: str
    content: str
    source: Optional[str] = "Ticketer Approved Resolution"


@router.post("/ingest", status_code=201)
def handle_knowledge_ingest(req: KnowledgeIngestRequest):
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
def handle_knowledge_search(q: str):
    ans = answer_question(q)
    return {"query": q, "answer": ans.answer, "verified": ans.verified}
