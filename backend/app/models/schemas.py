from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class Coordinates(BaseModel):
    x: float
    y: float
    lat: Optional[float] = None
    lng: Optional[float] = None

class Location(BaseModel):
    id: str
    name: str
    category: str
    description: str
    floor: Optional[str] = "Ground"
    coordinates: Coordinates
    tags: List[str] = Field(default_factory=list)

class Edge(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_node: str = Field(..., alias="from")
    to_node: str = Field(..., alias="to")
    distance: float
    path_type: Optional[str] = "Paved walkway"
    accessible: Optional[bool] = True
    has_stairs: Optional[bool] = False
    ramp_available: Optional[bool] = False
    accessibility_verified: Optional[bool] = False

class MapBounds(BaseModel):
    width: float
    height: float

class CampusData(BaseModel):
    campus_name: str
    is_demo_data: bool = True
    notice: str
    distance_unit: str = "meters"
    map_bounds: MapBounds
    locations: List[Location]
    edges: List[Edge]

class RouteRequest(BaseModel):
    start_id: str
    destination_id: str
    preference: Optional[str] = "shortest"

class RouteStep(BaseModel):
    step_number: int
    from_node_id: str
    from_node_name: str
    to_node_id: str
    to_node_name: str
    distance: float
    cumulative_distance: float
    instruction: str
    path_type: str
    has_stairs: Optional[bool] = False
    ramp_available: Optional[bool] = False
    accessibility_verified: Optional[bool] = False

class RouteResponse(BaseModel):
    found: bool
    start_id: str
    destination_id: str
    preference: str = "shortest"
    total_distance: float
    distance_unit: str = "meters"
    path_node_ids: List[str]
    waypoints: List[Location]
    steps: List[RouteStep]
    preference_explanation: Optional[str] = None
    is_accessible_verified: bool = False
    message: Optional[str] = None

class ChatMessage(BaseModel):
    role: str # "user" or "assistant" or "system"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = Field(default_factory=list)
    current_location_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    model: str
    grounded_in_campus_data: bool
    ollama_online: bool
    suggestions: List[str] = Field(default_factory=list)

class HealthResponse(BaseModel):
    status: str
    campus_data_loaded: bool
    total_locations: int
    total_connections: int
    is_demo_data: bool
    ollama_status: str
    ollama_model: str
