from fastapi import APIRouter
from ..models.schemas import ChatRequest, ChatResponse
from ..services.ai_service import ai_service

router = APIRouter(prefix="/api", tags=["Campus AI Assistant"])

@router.post("/chat", response_model=ChatResponse)
async def campus_ai_chat(request: ChatRequest):
    """
    Campus AI assistant chat endpoint grounded in Aurora University dataset.
    Routes queries to local Ollama (llama3.2:latest) with offline fallback.
    """
    return await ai_service.ask_assistant(
        message=request.message,
        history=request.history,
        current_location_id=request.current_location_id
    )
