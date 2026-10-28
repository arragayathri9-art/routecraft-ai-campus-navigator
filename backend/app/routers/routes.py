from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from ..models.schemas import RouteRequest, RouteResponse
from ..services.campus_service import campus_service

router = APIRouter(prefix="/api", tags=["Routing"])

def _execute_route_calc(start_id: str, destination_id: str, preference: str = "shortest") -> RouteResponse:
    s_id = (start_id or "").strip()
    d_id = (destination_id or "").strip()
    pref = (preference or "shortest").strip().lower()

    if not s_id or not d_id:
        raise HTTPException(
            status_code=400,
            detail="Both 'start_id' and 'destination_id' parameters must be non-empty strings."
        )

    if pref not in ["shortest", "wheelchair", "avoid_stairs"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid route preference '{pref}'. Supported preferences are 'shortest', 'wheelchair', and 'avoid_stairs'."
        )

    res = campus_service.calculate_route(s_id, d_id, preference=pref)
    if not res.found:
        raise HTTPException(status_code=404, detail=res.message)

    return res

@router.post("/route", response_model=RouteResponse)
async def calculate_campus_route_post(payload: RouteRequest):
    """
    Computes the shortest walking route between start_id and destination_id
    filtered by accessibility preference ('shortest', 'wheelchair', 'avoid_stairs')
    using Dijkstra's algorithm (POST payload).
    """
    return _execute_route_calc(payload.start_id, payload.destination_id, payload.preference or "shortest")

@router.get("/route", response_model=RouteResponse)
async def calculate_campus_route_get(
    start_id: str = Query(..., description="ID of starting location (e.g. north_gate)"),
    destination_id: str = Query(..., description="ID of destination location (e.g. lib)"),
    preference: str = Query("shortest", description="Route preference: 'shortest', 'wheelchair', 'avoid_stairs'")
):
    """
    Computes the shortest walking route between start_id and destination_id
    filtered by accessibility preference ('shortest', 'wheelchair', 'avoid_stairs')
    using Dijkstra's algorithm (GET query parameters).
    """
    return _execute_route_calc(start_id, destination_id, preference)
