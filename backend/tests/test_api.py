import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["project"] == "RouteCraft AI — Aurora Campus Navigator"
    assert data["is_demo_data"] is True

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["campus_data_loaded"] is True
    assert data["total_locations"] > 0
    assert data["is_demo_data"] is True

def test_locations_list():
    res = client.get("/api/locations")
    assert res.status_code == 200
    locations = res.json()
    assert isinstance(locations, list)
    assert len(locations) >= 10
    ids = [loc["id"] for loc in locations]
    assert "lib" in ids
    assert "north_gate" in ids

def test_locations_search_query():
    res = client.get("/api/locations?q=library")
    assert res.status_code == 200
    locations = res.json()
    assert len(locations) >= 1
    assert locations[0]["id"] == "lib"

def test_locations_filter_category():
    res = client.get("/api/locations?category=Dining%20%26%20Food")
    assert res.status_code == 200
    locations = res.json()
    assert len(locations) >= 1
    assert any("Dining" in loc["category"] for loc in locations)

def test_location_detail_found():
    res = client.get("/api/locations/eng")
    assert res.status_code == 200
    loc = res.json()
    assert loc["id"] == "eng"
    assert "Robotics" in loc["name"] or "Engineering" in loc["name"]

def test_location_detail_not_found():
    res = client.get("/api/locations/unknown_xyz")
    assert res.status_code == 404

def test_categories_endpoint():
    res = client.get("/api/categories")
    assert res.status_code == 200
    cats = res.json()
    assert isinstance(cats, list)
    assert len(cats) >= 3

def test_graph_endpoint():
    res = client.get("/api/graph")
    assert res.status_code == 200
    data = res.json()
    assert "locations" in data
    assert "edges" in data
    assert len(data["edges"]) >= 15

def test_route_calculation_success():
    # Calculate route from North Gate to South Gate
    payload = {"start_id": "north_gate", "destination_id": "south_gate"}
    res = client.post("/api/route", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["found"] is True
    assert data["total_distance"] > 0
    assert data["distance_unit"] == "meters"
    assert len(data["steps"]) >= 2
    assert data["path_node_ids"][0] == "north_gate"
    assert data["path_node_ids"][-1] == "south_gate"

def test_route_calculation_get_method():
    res = client.get("/api/route?start_id=north_gate&destination_id=lib")
    assert res.status_code == 200
    data = res.json()
    assert data["found"] is True
    assert data["total_distance"] == 170.0
    assert data["path_node_ids"] == ["north_gate", "lib"]

def test_route_calculation_empty_params():
    res = client.post("/api/route", json={"start_id": "", "destination_id": "lib"})
    assert res.status_code == 400

    res2 = client.get("/api/route?start_id=&destination_id=lib")
    assert res2.status_code == 400

def test_route_calculation_invalid_node():
    payload = {"start_id": "invalid_origin", "destination_id": "south_gate"}
    res = client.post("/api/route", json=payload)
    assert res.status_code == 404
    assert "not found" in res.json()["detail"]

def test_chat_endpoint():
    payload = {"message": "Where can I find books and quiet study spaces?"}
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert len(data["reply"]) > 10
    assert data["grounded_in_campus_data"] is True
    assert len(data["suggestions"]) > 0

def test_chat_offline_graceful_fallback(monkeypatch):
    from app.services.ai_service import ai_service
    # Point ai_service to an unreachable port to simulate Ollama being offline
    monkeypatch.setattr(ai_service, "base_url", "http://127.0.0.1:9999")
    payload = {"message": "Where can I find a place to eat lunch?"}
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["ollama_online"] is False
    assert data["model"] == "local-fallback"
    assert "Dining" in data["reply"] or "food" in data["reply"] or "offline" in data["reply"]


