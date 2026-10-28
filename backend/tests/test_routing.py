import pytest
from app.routing.dijkstra import CampusGraph
from app.models.schemas import Location, Edge, Coordinates

@pytest.fixture
def sample_graph():
    locations = [
        Location(id="A", name="Building A", category="Academic", description="Test A", coordinates=Coordinates(x=0, y=0), tags=["a"]),
        Location(id="B", name="Building B", category="Dining", description="Test B", coordinates=Coordinates(x=10, y=10), tags=["b"]),
        Location(id="C", name="Building C", category="Library", description="Test C", coordinates=Coordinates(x=20, y=20), tags=["c"]),
        Location(id="D", name="Building D", category="Gym", description="Test D", coordinates=Coordinates(x=30, y=30), tags=["d"]),
    ]
    edges = [
        Edge(**{"from": "A", "to": "B", "distance": 10.0, "path_type": "Main Walk"}),
        Edge(**{"from": "B", "to": "C", "distance": 15.0, "path_type": "Courtyard"}),
        Edge(**{"from": "A", "to": "C", "distance": 35.0, "path_type": "Long Way"}),
    ]
    # D is disconnected
    return CampusGraph(locations=locations, edges=edges, distance_unit="meters")

def test_dijkstra_shortest_path_found(sample_graph):
    # Shortest path A -> C should go through B: 10 + 15 = 25 (rather than 35)
    res = sample_graph.find_shortest_path("A", "C")
    assert res.found is True
    assert res.total_distance == 25.0
    assert res.path_node_ids == ["A", "B", "C"]
    assert len(res.steps) == 2
    assert res.steps[0].instruction.startswith("Depart from Building A")
    assert res.steps[1].to_node_name == "Building C"

def test_dijkstra_same_start_and_dest(sample_graph):
    res = sample_graph.find_shortest_path("A", "A")
    assert res.found is True
    assert res.total_distance == 0.0
    assert res.path_node_ids == ["A"]
    assert len(res.steps) == 1

def test_dijkstra_unreachable_node(sample_graph):
    res = sample_graph.find_shortest_path("A", "D")
    assert res.found is False
    assert "No connected pathway" in res.message

def test_dijkstra_invalid_node(sample_graph):
    res = sample_graph.find_shortest_path("A", "NON_EXISTENT")
    assert res.found is False
    assert "not found" in res.message
