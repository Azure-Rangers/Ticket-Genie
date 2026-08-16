from fastapi import APIRouter, Depends

from models.chatbot import ChatRequest, ChatResponse
from services.chatbot_service import handle_message
from services.jwt_verifier import verify_azure_user

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


@router.post("/message", response_model=ChatResponse)
def chatbot_message(
    request: ChatRequest,
    current_user: dict = Depends(verify_azure_user),
):
    return handle_message(request)
