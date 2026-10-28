from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query

from ..models.schemas import Location
from ..services.campus_service import campus_service

router = APIRouter(prefix="/api", tags=["Locations"])

@router.get("/locations", response_model=List[Location])
async def list_locations(
    q: Optional[str] = Query(None, description="Search term matching name, description, tags, or category"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """Retrieve all campus locations, with optional search and category filters."""
    return campus_service.get_locations(query=q, category=category)

@router.get("/locations/{location_id}", response_model=Location)
async def get_location_detail(location_id: str):
    """Retrieve details for a specific campus location by ID."""
    loc = campus_service.get_location_by_id(location_id)
    if not loc:
        raise HTTPException(
            status_code=404,
            detail=f"Location with ID '{location_id}' not found in campus database."
        )
    return loc

@router.get("/categories", response_model=List[str])
async def list_categories():
    """Retrieve all distinct location categories available in the campus dataset."""
    return campus_service.get_categories()

@router.get("/graph", response_model=Dict[str, Any])
async def get_campus_graph():
    """Retrieve the entire campus graph topology including nodes, edges, and map dimensions."""
    return campus_service.get_graph_data()
