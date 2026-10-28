import pytest
from app.routing.dijkstra import CampusGraph
from app.models.schemas import Location, Edge, Coordinates

@pytest.fixture
def accessibility_graph():
    locations = [
        Location(id="A", name="Building A", category="Academic", description="Test A", coordinates=Coordinates(x=0, y=0), tags=["a"]),
        Location(id="B", name="Building B", category="Dining", description="Test B", coordinates=Coordinates(x=10, y=10), tags=["b"]),
        Location(id="C", name="Building C", category="Library", description="Test C", coordinates=Coordinates(x=20, y=20), tags=["c"]),
        Location(id="D", name="Building D", category="Gym", description="Test D", coordinates=Coordinates(x=30, y=30), tags=["d"]),
        Location(id="E", name="Building E", category="Admin", description="Test E", coordinates=Coordinates(x=40, y=40), tags=["e"]),
        Location(id="STAIRS_ONLY", name="Stairs Tower", category="Tower", description="Only stairs", coordinates=Coordinates(x=50, y=50), tags=["stairs"]),
    ]
    edges = [
        # A -> B is direct, short, but has STAIRS and NO RAMP
        Edge(**{"from": "A", "to": "B", "distance": 10.0, "path_type": "Stepped Walk", "accessible": False, "has_stairs": True, "ramp_available": False, "accessibility_verified": True}),
        # A -> C -> B is longer, NO stairs, verified accessible
        Edge(**{"from": "A", "to": "C", "distance": 15.0, "path_type": "Level Promenade", "accessible": True, "has_stairs": False, "ramp_available": True, "accessibility_verified": True}),
        Edge(**{"from": "C", "to": "B", "distance": 15.0, "path_type": "Level Promenade", "accessible": True, "has_stairs": False, "ramp_available": True, "accessibility_verified": True}),
        # B -> E has stairs WITH an accessible ramp, verified accessible
        Edge(**{"from": "B", "to": "E", "distance": 20.0, "path_type": "Ramped Courtyard", "accessible": True, "has_stairs": True, "ramp_available": True, "accessibility_verified": True}),
        # C -> E has unverified accessibility (unpaved gravel path)
        Edge(**{"from": "C", "to": "E", "distance": 25.0, "path_type": "Gravel Trail", "accessible": False, "has_stairs": False, "ramp_available": False, "accessibility_verified": False}),
        # STAIRS_ONLY is only accessible via unramped stairs from D
        Edge(**{"from": "D", "to": "STAIRS_ONLY", "distance": 10.0, "path_type": "Steep Stairs", "accessible": False, "has_stairs": True, "ramp_available": False, "accessibility_verified": True}),
        # D is connected to A via level path
        Edge(**{"from": "A", "to": "D", "distance": 30.0, "path_type": "Main Avenue", "accessible": True, "has_stairs": False, "ramp_available": True, "accessibility_verified": True}),
    ]
    return CampusGraph(locations=locations, edges=edges, distance_unit="meters")

def test_dijkstra_shortest_path_normal(accessibility_graph):
    # Shortest path A -> B should take direct stairs: distance 10.0
    res = accessibility_graph.find_shortest_path("A", "B", preference="shortest")
    assert res.found is True
    assert res.total_distance == 10.0
    assert res.path_node_ids == ["A", "B"]
    assert res.preference == "shortest"
    assert "Direct shortest" in res.preference_explanation

def test_dijkstra_stair_avoidance(accessibility_graph):
    # In avoid_stairs, A -> B must avoid direct stairs (A->B) and take A -> C -> B (15 + 15 = 30.0)
    res = accessibility_graph.find_shortest_path("A", "B", preference="avoid_stairs")
    assert res.found is True
    assert res.total_distance == 30.0
    assert res.path_node_ids == ["A", "C", "B"]
    assert res.preference == "avoid_stairs"
    assert "avoiding all stairs" in res.preference_explanation.lower()

def test_dijkstra_wheelchair_accessible_with_ramp(accessibility_graph):
    # A -> E in wheelchair mode:
    # A->B is stairs without ramp (excluded).
    # A->C is verified level (15m).
    # From C: C->E is unverified (excluded by conservative rule!).
    # C->B is verified level (15m).
    # B->E has stairs WITH ramp and is verified accessible (20m).
    # Total path: A -> C -> B -> E = 15 + 15 + 20 = 50.0m
    res = accessibility_graph.find_shortest_path("A", "E", preference="wheelchair")
    assert res.found is True
    assert res.total_distance == 50.0
    assert res.path_node_ids == ["A", "C", "B", "E"]
    assert res.is_accessible_verified is True
    assert "Wheelchair-accessible" in res.preference_explanation

def test_dijkstra_conservative_unverified_exclusion(accessibility_graph):
    # Verify that unverified gravel path C -> E is excluded in wheelchair mode
    # even though it has no stairs!
    res_wc = accessibility_graph.find_shortest_path("C", "E", preference="wheelchair")
    assert res_wc.found is True
    # If C->E unverified was allowed, distance would be 25m.
    # Because it is unverified, it must take C -> B -> E (15 + 20 = 35m).
    assert res_wc.total_distance == 35.0
    assert res_wc.path_node_ids == ["C", "B", "E"]

    # In shortest mode, C -> E unverified (25m) is used
    res_short = accessibility_graph.find_shortest_path("C", "E", preference="shortest")
    assert res_short.found is True
    assert res_short.total_distance == 25.0
    assert res_short.path_node_ids == ["C", "E"]

def test_dijkstra_no_suitable_route_stairs(accessibility_graph):
    # Route from D to STAIRS_ONLY: only connected via unramped stairs.
    # Shortest finds it
    res_short = accessibility_graph.find_shortest_path("D", "STAIRS_ONLY", preference="shortest")
    assert res_short.found is True
    assert res_short.total_distance == 10.0

    # Avoid stairs cannot reach it
    res_avoid = accessibility_graph.find_shortest_path("D", "STAIRS_ONLY", preference="avoid_stairs")
    assert res_avoid.found is False
    assert "no suitable route avoiding stairs" in res_avoid.message.lower()

    # Wheelchair cannot reach it
    res_wc = accessibility_graph.find_shortest_path("D", "STAIRS_ONLY", preference="wheelchair")
    assert res_wc.found is False
    assert "no suitable wheelchair-friendly route" in res_wc.message.lower()

def test_dijkstra_same_start_and_dest(accessibility_graph):
    res = accessibility_graph.find_shortest_path("A", "A", preference="wheelchair")
    assert res.found is True
    assert res.total_distance == 0.0
    assert res.path_node_ids == ["A"]
    assert len(res.steps) == 1
    assert res.is_accessible_verified is True

def test_dijkstra_invalid_node(accessibility_graph):
    res = accessibility_graph.find_shortest_path("A", "NON_EXISTENT")
    assert res.found is False
    assert "not found" in res.message
