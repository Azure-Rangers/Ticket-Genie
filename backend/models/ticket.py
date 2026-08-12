from typing import Optional

from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    category: str = Field(default="IT Support")
    priority: str = Field(default="Medium")
    department: Optional[str] = "IT"
    description: str = Field(..., min_length=5)
    preferredDate: Optional[str] = None
    is_anonymous: bool = False
    attachment: Optional[str] = None


class TicketResponse(BaseModel):
    id: str
    title: str
    category: str
    priority: str
    status: str
    department: str
    description: str
    date: str
    createdAt: str
    is_anonymous: bool = False
    attachment: Optional[str] = None


class GenieChatRequest(BaseModel):
    message: str


class GenieChatResponse(BaseModel):
    reply: str
    suggestions: Optional[list[str]] = None
