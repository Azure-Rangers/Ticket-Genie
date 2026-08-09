from pydantic import BaseModel, Field
from typing import Optional, Literal


class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10)
    department: Literal["HR", "IT"]
    is_anonymous: bool = False
    attachment: Optional[str] = None