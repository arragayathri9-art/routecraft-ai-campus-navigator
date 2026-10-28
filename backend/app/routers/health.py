from fastapi import APIRouter
from ..models.schemas import HealthResponse
from ..services.campus_service import campus_service
from ..services.ai_service import ai_service
from ..config import OLLAMA_MODEL

router = APIRouter(prefix="/api", tags=["Health & System"])

@router.get("/health", response_model=HealthResponse)
async def get_system_health():
    """
    Returns application health, dataset status, demo data label,
    and Ollama local daemon availability.
    """
    meta = campus_service.get_metadata()
    ollama_info = await ai_service.check_ollama_status()

    return HealthResponse(
        status="healthy" if campus_service.campus_data else "degraded",
        campus_data_loaded=campus_service.campus_data is not None,
        total_locations=meta.get("total_locations", 0),
        total_connections=meta.get("total_connections", 0),
        is_demo_data=meta.get("is_demo_data", True),
        ollama_status=ollama_info.get("status", "unknown"),
        ollama_model=OLLAMA_MODEL
    )
