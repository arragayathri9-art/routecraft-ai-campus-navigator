import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from ..config import DATA_FILE_PATH
from ..models.schemas import CampusData, Location, Edge, RouteResponse
from ..routing.dijkstra import CampusGraph

logger = logging.getLogger("campus_service")

class CampusService:
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = Path(data_path or DATA_FILE_PATH)
        self.campus_data: Optional[CampusData] = None
        self.graph: Optional[CampusGraph] = None
        self.load_data()

    def load_data(self) -> None:
        """Loads and parses the campus data JSON into validated models."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Campus dataset file not found at: {self.data_path}")

        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                raw_json = json.load(f)

            self.campus_data = CampusData(**raw_json)
            self.graph = CampusGraph(
                locations=self.campus_data.locations,
                edges=self.campus_data.edges,
                distance_unit=self.campus_data.distance_unit
            )
            logger.info(
                f"Loaded campus '{self.campus_data.campus_name}' with "
                f"{len(self.campus_data.locations)} locations and {len(self.campus_data.edges)} edges."
            )
        except Exception as e:
            logger.error(f"Failed to parse campus data: {e}", exc_info=True)
            raise

    def get_metadata(self) -> Dict[str, Any]:
        if not self.campus_data:
            return {}
        return {
            "campus_name": self.campus_data.campus_name,
            "is_demo_data": self.campus_data.is_demo_data,
            "notice": self.campus_data.notice,
            "distance_unit": self.campus_data.distance_unit,
            "map_bounds": self.campus_data.map_bounds.model_dump(),
            "total_locations": len(self.campus_data.locations),
            "total_connections": len(self.campus_data.edges),
        }

    def get_locations(self, query: Optional[str] = None, category: Optional[str] = None) -> List[Location]:
        if not self.campus_data:
            return []

        results = self.campus_data.locations

        if category:
            cat_lower = category.strip().lower()
            results = [loc for loc in results if loc.category.lower() == cat_lower]

        if query:
            q = query.strip().lower()
            results = [
                loc for loc in results
                if q in loc.name.lower()
                or q in loc.description.lower()
                or any(q in tag.lower() for tag in loc.tags)
                or q in loc.category.lower()
            ]

        return results

    def get_location_by_id(self, location_id: str) -> Optional[Location]:
        if not self.campus_data:
            return None
        for loc in self.campus_data.locations:
            if loc.id == location_id:
                return loc
        return None

    def get_categories(self) -> List[str]:
        if not self.campus_data:
            return []
        cats = sorted(list(set(loc.category for loc in self.campus_data.locations)))
        return cats

    def get_graph_data(self) -> Dict[str, Any]:
        if not self.campus_data:
            return {"locations": [], "edges": [], "map_bounds": {"width": 800, "height": 800}}
        return {
            "campus_name": self.campus_data.campus_name,
            "is_demo_data": self.campus_data.is_demo_data,
            "notice": self.campus_data.notice,
            "distance_unit": self.campus_data.distance_unit,
            "map_bounds": self.campus_data.map_bounds.model_dump(),
            "locations": [loc.model_dump() for loc in self.campus_data.locations],
            "edges": [
                {
                    "from": edge.from_node,
                    "to": edge.to_node,
                    "distance": edge.distance,
                    "path_type": edge.path_type,
                    "accessible": edge.accessible,
                    "has_stairs": edge.has_stairs,
                    "ramp_available": edge.ramp_available,
                    "accessibility_verified": edge.accessibility_verified,
                }
                for edge in self.campus_data.edges
            ]
        }

    def calculate_route(self, start_id: str, destination_id: str, preference: str = "shortest") -> RouteResponse:
        if not self.graph:
            raise RuntimeError("Campus routing graph is not initialized.")
        return self.graph.find_shortest_path(start_id, destination_id, preference=preference)

campus_service = CampusService()
