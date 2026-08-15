from typing import Literal, Optional

from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10)
    department: Optional[
        Literal[
            "HR Team",
            "Accounting Team",
            "Workplace Operations Team",
            "IT Team",
            "Upper Management",
        ]
    ] = None
    is_anonymous: bool = False
    attachment: Optional[str] = None


class CompletedTicket(TicketCreate):
    """A TicketCreate enriched with the AI classification result.

    This is what actually gets persisted: the raw ticket fields plus the
    department/category/priority/confidence/reason/needs_human_review
    values produced by classify_ticket(). `department` is reused from
    TicketCreate (same allowed values) rather than duplicated under a
    different name, but becomes required here since the AI always fills
    it in.
    """

    department: Literal[
        "HR Team",
        "Accounting Team",
        "Workplace Operations Team",
        "IT Team",
        "Upper Management",
    ]
    category: str
    priority: Literal["Low", "Medium", "High", "Critical"]
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    needs_human_review: bool
