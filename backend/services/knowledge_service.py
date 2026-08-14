"""
Knowledge / RAG retrieval boundary.

No real document store, vector index, or Azure AI Search is connected in
this repo yet. Rather than inventing that infrastructure, this module
defines the retrieval interface (KnowledgeRetriever) that a real retrieval
backend can implement later, plus a deterministic local mock
implementation so the Knowledge Agent has something safe and testable to
run against for V1.

Filtering by allowed_scopes happens INSIDE search(), before any content is
returned to a caller - callers (chatbot_service) never see documents
outside the scopes role_service.get_allowed_scopes() granted them, and the
LLM is never shown unfiltered content.

MOCK DATA NOTE: the "General" documents below summarize the same policies
already listed in frontend/knowledge-base.html (Code of Conduct, Remote
Work, Expense & Travel, Information Security, PTO). The department-scoped
documents (HR/IT/Accounting/UpperManagement) are synthetic placeholders
that exist only to exercise the authorization boundary in tests - they are
not real company policy and must be replaced by the approved knowledge
source before this ships.
"""

from dataclasses import dataclass
from typing import List, Protocol

from models.chatbot import ChatAction


@dataclass(frozen=True)
class KnowledgeDocument:
    id: str
    title: str
    content: str
    scope: str
    keywords: tuple


class KnowledgeRetriever(Protocol):
    def search(
        self, query: str, allowed_scopes: List[str]
    ) -> List[KnowledgeDocument]: ...


_MOCK_DOCUMENTS: List[KnowledgeDocument] = [
    KnowledgeDocument(
        id="kb-pto-policy",
        title="Paid Time Off (PTO) & Leave Accrual Policy",
        content=(
            "Full-time employees accrue PTO each pay period and can view their "
            "current balance in the HR Portal. PTO, medical leave, parental "
            "leave, and other time-off requests are submitted from the Leave "
            "Management tab on the New Request page and require manager "
            "approval before HR processes them."
        ),
        scope="General",
        keywords=("pto", "vacation", "time off", "leave", "accrual"),
    ),
    KnowledgeDocument(
        id="kb-remote-work",
        title="Hybrid & Remote Work Policy",
        content=(
            "Employees may work remotely in line with their team's hybrid "
            "schedule. Home office equipment requests and connectivity issues "
            "should be submitted as an IT & Technology request."
        ),
        scope="General",
        keywords=("remote", "hybrid", "work from home", "wfh"),
    ),
    KnowledgeDocument(
        id="kb-expense-travel",
        title="Corporate Travel & Expense Guidelines",
        content=(
            "Reimbursable expenses and travel bookings are submitted as an "
            "Account Management request on the New Request page, including "
            "receipts and the relevant cost center."
        ),
        scope="General",
        keywords=("expense", "reimbursement", "travel", "per diem"),
    ),
    KnowledgeDocument(
        id="kb-code-of-conduct",
        title="Global Employee Handbook & Code of Conduct",
        content=(
            "The Code of Conduct covers workplace ethics, anti-harassment, and "
            "equal opportunity standards. Concerns can be raised confidentially "
            "through an Anonymous Request."
        ),
        scope="General",
        keywords=("conduct", "harassment", "ethics", "handbook"),
    ),
    KnowledgeDocument(
        id="kb-infosec",
        title="Data Privacy & Confidentiality Agreement",
        content=(
            "Company data must be handled per the Information Security policy: "
            "no sharing credentials, and suspected security incidents should be "
            "reported as an IT & Technology request."
        ),
        scope="General",
        keywords=("security", "privacy", "confidentiality", "data"),
    ),
    KnowledgeDocument(
        id="kb-hr-internal-escalation",
        title="[Internal] HR Escalation Procedure",
        content=(
            "MOCK/INTERNAL: HR-only escalation steps for disciplinary cases "
            "and formal employee-relations investigations."
        ),
        scope="HR",
        keywords=("disciplinary", "escalation", "investigation", "employee relations"),
    ),
    KnowledgeDocument(
        id="kb-accounting-internal-thresholds",
        title="[Internal] Vendor Payment Approval Thresholds",
        content=(
            "MOCK/INTERNAL: Accounting-only vendor payment and invoice "
            "approval thresholds by amount."
        ),
        scope="Accounting",
        keywords=("vendor payment", "approval threshold", "invoice approval"),
    ),
    KnowledgeDocument(
        id="kb-it-internal-privileged-access",
        title="[Internal] Privileged Access Request Procedure",
        content=(
            "MOCK/INTERNAL: IT-only procedure for granting elevated/admin "
            "system access."
        ),
        scope="IT",
        keywords=("privileged access", "admin access", "elevated permissions"),
    ),
    KnowledgeDocument(
        id="kb-exec-budget-review",
        title="[Internal] Executive Budget Variance Review",
        content=(
            "MOCK/INTERNAL: Upper-management-only procedure for quarterly "
            "budget variance review."
        ),
        scope="UpperManagement",
        keywords=("budget variance", "executive review", "quarterly budget"),
    ),
]


class LocalMockKnowledgeRetriever:
    """Deterministic keyword-matching retriever over the local mock KB."""

    def __init__(self, documents: List[KnowledgeDocument] = None):
        self._documents = documents if documents is not None else _MOCK_DOCUMENTS

    def search(self, query: str, allowed_scopes: List[str]) -> List[KnowledgeDocument]:
        allowed = set(allowed_scopes)
        normalized_query = query.lower()

        candidates = [doc for doc in self._documents if doc.scope in allowed]

        matches = [
            doc
            for doc in candidates
            if any(keyword in normalized_query for keyword in doc.keywords)
            or doc.title.lower() in normalized_query
        ]
        return matches


default_knowledge_retriever = LocalMockKnowledgeRetriever()


class KnowledgeAnswer:
    def __init__(
        self,
        answer: str,
        verified: bool,
        sources: List[str],
        action: ChatAction = None,
    ):
        self.answer = answer
        self.verified = verified
        self.sources = sources
        self.action = action


def answer_question(
    query: str,
    *,
    allowed_scopes: List[str],
    retriever: KnowledgeRetriever = default_knowledge_retriever,
) -> KnowledgeAnswer:
    """
    Retrieve ONLY documents already within allowed_scopes, then compose an
    answer strictly from that content. Never falls back to unfiltered
    content, and never fabricates an answer when nothing authorized matches.
    """

    matches = retriever.search(query, allowed_scopes)

    if not matches:
        return KnowledgeAnswer(
            answer=(
                "I couldn't verify an answer to that from the knowledge sources "
                "you're authorized to access. You can browse the Knowledge Base "
                "for related articles, or I can help you open a support request "
                "so a person can confirm the details."
            ),
            verified=False,
            sources=[],
            action=ChatAction(
                type="navigate",
                target="knowledge-base.html",
                label="Browse Knowledge Base",
            ),
        )

    parts = [f"{doc.title}: {doc.content}" for doc in matches[:3]]
    answer = " ".join(parts)
    return KnowledgeAnswer(
        answer=answer,
        verified=True,
        sources=[doc.id for doc in matches[:3]],
    )
