from fastapi import APIRouter

from models.chatbot import ChatRequest, ChatResponse
from services.chatbot_service import handle_message

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


@router.post("/message", response_model=ChatResponse)
def chatbot_message(request: ChatRequest):
    return handle_message(request)
