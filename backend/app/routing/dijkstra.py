import heapq
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from ..models.schemas import Location, Edge, RouteResponse, RouteStep

@dataclass
class EdgeMeta:
    to_node: str
    distance: float
    path_type: str
    accessible: bool
    has_stairs: bool
    ramp_available: bool
    accessibility_verified: bool

class CampusGraph:
    """
    Undirected graph data structure supporting Dijkstra's shortest-path algorithm
    for campus navigation with accessibility-aware preferences (Shortest,
    Wheelchair-Friendly, Avoid Stairs) and turn-by-turn routing directions.
    """

    PREFERENCE_EXPLANATIONS = {
        "shortest": "Direct shortest route calculated without accessibility constraints.",
        "wheelchair": "Wheelchair-accessible route utilizing only surveyed barrier-free pathways and verified ramps (avoids unramped stairs and unverified trails).",
        "avoid_stairs": "Route calculated avoiding all stairs and stepped terraces (uses level walkways or ramp-equipped pathways)."
    }

    def __init__(self, locations: List[Location], edges: List[Edge], distance_unit: str = "meters"):
        self.distance_unit = distance_unit
        self.locations: Dict[str, Location] = {loc.id: loc for loc in locations}
        # Adjacency list: node_id -> list of EdgeMeta
        self.adj: Dict[str, List[EdgeMeta]] = {loc.id: [] for loc in locations}

        for edge in edges:
            u = edge.from_node
            v = edge.to_node
            dist = float(edge.distance)
            path_type = edge.path_type or "Paved walkway"
            accessible = True if edge.accessible is None else bool(edge.accessible)
            has_stairs = bool(edge.has_stairs)
            ramp_available = bool(edge.ramp_available)
            accessibility_verified = bool(edge.accessibility_verified)

            if u in self.adj and v in self.adj:
                self.adj[u].append(
                    EdgeMeta(
                        to_node=v,
                        distance=dist,
                        path_type=path_type,
                        accessible=accessible,
                        has_stairs=has_stairs,
                        ramp_available=ramp_available,
                        accessibility_verified=accessibility_verified
                    )
                )
                self.adj[v].append(
                    EdgeMeta(
                        to_node=u,
                        distance=dist,
                        path_type=path_type,
                        accessible=accessible,
                        has_stairs=has_stairs,
                        ramp_available=ramp_available,
                        accessibility_verified=accessibility_verified
                    )
                )

    def _is_edge_allowed(self, edge: EdgeMeta, preference: str) -> bool:
        """
        Determines whether an edge satisfies the routing accessibility constraints.
        Treats unverified or unknown accessibility data conservatively.
        """
        if preference == "shortest":
            return True

        if preference == "avoid_stairs":
            # Must not contain stairs unless an accessible ramp is provided
            if edge.has_stairs and not edge.ramp_available:
                return False
            return True

        if preference == "wheelchair":
            # Conservative rule: Never claim a route is wheelchair accessible
            # unless relevant survey data has been verified.
            if not edge.accessibility_verified:
                return False
            if not edge.accessible:
                return False
            if edge.has_stairs and not edge.ramp_available:
                return False
            return True

        return True

    def find_shortest_path(
        self,
        start_id: str,
        destination_id: str,
        preference: str = "shortest"
    ) -> RouteResponse:
        """
        Executes Dijkstra's algorithm to compute the shortest path
        between start_id and destination_id filtered by accessibility preferences.
        """
        pref = (preference or "shortest").strip().lower()
        if pref not in self.PREFERENCE_EXPLANATIONS:
            pref = "shortest"

        explanation = self.PREFERENCE_EXPLANATIONS.get(pref)

        if start_id not in self.locations:
            return RouteResponse(
                found=False,
                start_id=start_id,
                destination_id=destination_id,
                preference=pref,
                total_distance=0.0,
                distance_unit=self.distance_unit,
                path_node_ids=[],
                waypoints=[],
                steps=[],
                preference_explanation=explanation,
                is_accessible_verified=False,
                message=f"Starting location '{start_id}' was not found in campus records."
            )

        if destination_id not in self.locations:
            return RouteResponse(
                found=False,
                start_id=start_id,
                destination_id=destination_id,
                preference=pref,
                total_distance=0.0,
                distance_unit=self.distance_unit,
                path_node_ids=[],
                waypoints=[],
                steps=[],
                preference_explanation=explanation,
                is_accessible_verified=False,
                message=f"Destination '{destination_id}' was not found in campus records."
            )

        # Handle trivial case: start == destination
        if start_id == destination_id:
            loc = self.locations[start_id]
            return RouteResponse(
                found=True,
                start_id=start_id,
                destination_id=destination_id,
                preference=pref,
                total_distance=0.0,
                distance_unit=self.distance_unit,
                path_node_ids=[start_id],
                waypoints=[loc],
                steps=[
                    RouteStep(
                        step_number=1,
                        from_node_id=start_id,
                        from_node_name=loc.name,
                        to_node_id=destination_id,
                        to_node_name=loc.name,
                        distance=0.0,
                        cumulative_distance=0.0,
                        instruction=f"You are already at {loc.name}.",
                        path_type="Direct",
                        has_stairs=False,
                        ramp_available=True,
                        accessibility_verified=True
                    )
                ],
                preference_explanation=explanation,
                is_accessible_verified=True,
                message="Starting point and destination are identical."
            )

        # Priority queue stores tuples of (current_shortest_distance, node_id)
        pq: List[Tuple[float, str]] = [(0.0, start_id)]
        distances: Dict[str, float] = {node_id: float("inf") for node_id in self.locations}
        distances[start_id] = 0.0

        # Predecessor mapping: child_node -> (parent_node, EdgeMeta)
        predecessors: Dict[str, Tuple[Optional[str], Optional[EdgeMeta]]] = {
            node_id: (None, None) for node_id in self.locations
        }

        visited = set()

        while pq:
            curr_dist, u = heapq.heappop(pq)

            if u in visited:
                continue
            visited.add(u)

            if u == destination_id:
                break

            for edge_meta in self.adj.get(u, []):
                # Filter paths according to selected preference before relaxing
                if not self._is_edge_allowed(edge_meta, pref):
                    continue

                v = edge_meta.to_node
                weight = edge_meta.distance
                new_dist = curr_dist + weight

                if new_dist < distances[v]:
                    distances[v] = new_dist
                    predecessors[v] = (u, edge_meta)
                    heapq.heappush(pq, (new_dist, v))

        # Check if destination is reachable with the given constraints
        if distances[destination_id] == float("inf"):
            start_name = self.locations[start_id].name
            dest_name = self.locations[destination_id].name

            if pref == "wheelchair":
                no_route_msg = (
                    f"No suitable wheelchair-friendly route could be found between {start_name} and {dest_name}. "
                    "Connecting pathways include unramped stairs or lack verified accessibility surveys."
                )
            elif pref == "avoid_stairs":
                no_route_msg = (
                    f"No suitable route avoiding stairs could be found between {start_name} and {dest_name}. "
                    "Available connecting pathways require navigating stairs without ramps."
                )
            else:
                no_route_msg = f"No connected pathway found between {start_name} and {dest_name}."

            return RouteResponse(
                found=False,
                start_id=start_id,
                destination_id=destination_id,
                preference=pref,
                total_distance=0.0,
                distance_unit=self.distance_unit,
                path_node_ids=[],
                waypoints=[],
                steps=[],
                preference_explanation=explanation,
                is_accessible_verified=False,
                message=no_route_msg
            )

        # Backtrack path from destination to start
        path_segments: List[Tuple[str, str, EdgeMeta]] = []
        curr = destination_id
        while curr != start_id:
            parent, edge_meta = predecessors[curr]
            if parent is None or edge_meta is None:
                break
            path_segments.append((parent, curr, edge_meta))
            curr = parent

        path_segments.reverse()

        path_node_ids = [start_id] + [seg[1] for seg in path_segments]
        waypoints = [self.locations[nid] for nid in path_node_ids]

        # Generate human-readable navigation steps with accessibility callouts
        steps: List[RouteStep] = []
        cumulative = 0.0
        total_steps = len(path_segments)

        is_accessible_verified = all(
            em.accessibility_verified and em.accessible and (not em.has_stairs or em.ramp_available)
            for _, _, em in path_segments
        )

        for idx, (from_id, to_id, em) in enumerate(path_segments, start=1):
            dist = em.distance
            cumulative += dist
            from_name = self.locations[from_id].name
            to_name = self.locations[to_id].name
            path_type = em.path_type

            # Add accessibility detail to instructions
            ramp_note = ""
            if em.has_stairs and em.ramp_available:
                ramp_note = " via accessible ramp"

            if idx == 1:
                instruction = f"Depart from {from_name} along the {path_type}{ramp_note} towards {to_name} ({round(dist)} {self.distance_unit})."
            elif idx == total_steps:
                instruction = f"Continue on the {path_type}{ramp_note} to arrive at {to_name} ({round(dist)} {self.distance_unit})."
            else:
                instruction = f"Follow the {path_type}{ramp_note} toward {to_name} ({round(dist)} {self.distance_unit})."

            steps.append(
                RouteStep(
                    step_number=idx,
                    from_node_id=from_id,
                    from_node_name=from_name,
                    to_node_id=to_id,
                    to_node_name=to_name,
                    distance=round(dist, 1),
                    cumulative_distance=round(cumulative, 1),
                    instruction=instruction,
                    path_type=path_type,
                    has_stairs=em.has_stairs,
                    ramp_available=em.ramp_available,
                    accessibility_verified=em.accessibility_verified
                )
            )

        return RouteResponse(
            found=True,
            start_id=start_id,
            destination_id=destination_id,
            preference=pref,
            total_distance=round(distances[destination_id], 1),
            distance_unit=self.distance_unit,
            path_node_ids=path_node_ids,
            waypoints=waypoints,
            steps=steps,
            preference_explanation=explanation,
            is_accessible_verified=is_accessible_verified,
            message=f"Optimal {pref} route found: {len(steps)} segments covering {round(distances[destination_id])} {self.distance_unit}."
        )
