import sys
import json
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.campus_service import campus_service
from app.services.ai_service import ai_service, CampusAIService
from app.routing.dijkstra import CampusGraph
from app.models.schemas import Location, Edge, Coordinates

def test_1_health_endpoint():
    print("--- [TEST 1] Backend Health Endpoint ---")
    meta = campus_service.get_metadata()
    assert campus_service.campus_data is not None, "Campus data must be loaded"
    assert meta["total_locations"] == 11, f"Expected 11 locations, found {meta['total_locations']}"
    assert meta["total_connections"] == 20, f"Expected 20 edges, found {meta['total_connections']}"
    assert meta["is_demo_data"] is True, "Must be flagged as demo data"
    assert "DEMO DATA" in meta["notice"], "Demo notice must be present"
    print("PASSED: Health data is consistent, 11 locations & 20 connections loaded.")
    return True

def test_2_campus_locations_load():
    print("--- [TEST 2] Campus Locations Load ---")
    graph_data = campus_service.get_graph_data()
    locs = graph_data["locations"]
    assert len(locs) >= 10, f"Expected at least 10 locations, got {len(locs)}"
    required_ids = ["north_gate", "lib", "sci", "eng", "quad", "stu_union", "adm", "arts", "cafe", "gym", "south_gate"]
    for rid in required_ids:
        loc = next((l for l in locs if l["id"] == rid), None)
        assert loc is not None, f"Required building '{rid}' missing from graph data"
        assert "x" in loc["coordinates"] and "y" in loc["coordinates"], f"Coordinates missing in {rid}"
        assert len(loc["tags"]) > 0, f"Tags missing in {rid}"
    print(f"PASSED: All {len(required_ids)} campus landmarks loaded with coordinates and tags.")
    return True

def test_3_search_filtering():
    print("--- [TEST 3] Location Search Filtering ---")
    # Search by name
    res_lib = campus_service.get_locations(query="library")
    assert any(l.id == "lib" for l in res_lib), "Search 'library' should find Phillips Central Library"
    
    # Search by category
    res_dining = campus_service.get_locations(category="Dining & Food")
    assert len(res_dining) >= 1, "Category 'Dining & Food' should return at least 1 location"
    assert res_dining[0].id == "cafe", "Dining search should find cafe"
    
    # Search by tag
    res_tag = campus_service.get_locations(query="robotics")
    assert any(l.id == "eng" for l in res_tag), "Tag search 'robotics' should return engineering hall"
    
    # Search non-matching
    res_none = campus_service.get_locations(query="nonexistent_landmark_xyz")
    assert len(res_none) == 0, "Nonexistent search query should yield empty list safely"
    print("PASSED: Search filters correctly across name, category, description, and tags.")
    return True

def test_4_route_calculation():
    print("--- [TEST 4] Dijkstra Route Calculation (Shortest Path) ---")
    # Test North Gate to South Gate
    res = campus_service.calculate_route("north_gate", "south_gate")
    assert res.found is True, "Route north_gate -> south_gate must be found"
    assert res.total_distance == 720.0, f"Expected 720.0m shortest path, got {res.total_distance}"
    assert res.path_node_ids == ["north_gate", "lib", "quad", "gym", "south_gate"], f"Unexpected path: {res.path_node_ids}"
    assert len(res.steps) == 4, f"Expected 4 navigation steps, got {len(res.steps)}"
    
    # Check cumulative distance progression
    for step in res.steps:
        assert step.distance > 0, "Each step must have positive distance"
    assert res.steps[-1].cumulative_distance == 720.0, "Final cumulative distance must equal total distance"
    
    # Test Science to Cafe
    res2 = campus_service.calculate_route("sci", "cafe")
    assert res2.found is True
    # sci -> lib (230) -> quad (170) -> cafe (290) = 690, or sci -> eng (190) -> quad (250) -> cafe (290) = 730, or sci -> lib (230) -> stu_union (250) -> adm (180) -> cafe (160) = 820
    assert res2.total_distance == 690.0, f"Expected 690.0m for sci -> cafe, got {res2.total_distance}"
    assert res2.path_node_ids == ["sci", "lib", "quad", "cafe"]
    print("PASSED: Dijkstra shortest path algorithm computes mathematically optimal routes and step instructions.")
    return True

def test_5_route_highlighting_logic():
    print("--- [TEST 5] Route Map Highlighting Logic ---")
    res = campus_service.calculate_route("north_gate", "south_gate")
    ids = res.path_node_ids
    # Emulate frontend activeRoutePairs calculation
    active_route_pairs = set()
    for i in range(len(ids) - 1):
        active_route_pairs.add(f"{ids[i]}->{ids[i+1]}")
        active_route_pairs.add(f"{ids[i+1]}->{ids[i]}")
    
    # Verify expected edges are captured
    assert "north_gate->lib" in active_route_pairs
    assert "lib->quad" in active_route_pairs
    assert "quad->gym" in active_route_pairs
    assert "gym->south_gate" in active_route_pairs
    assert "north_gate->sci" not in active_route_pairs
    print("PASSED: Active route edge pairs generated symmetrically for directional map highlighting.")
    return True

def test_6_invalid_locations_and_disconnected_routes():
    print("--- [TEST 6] Error Handling: Invalid Locations & Disconnected Routes ---")
    # Invalid start
    res_inv_start = campus_service.calculate_route("invalid_gate", "lib")
    assert res_inv_start.found is False
    assert "not found" in res_inv_start.message.lower()
    
    # Invalid dest
    res_inv_dest = campus_service.calculate_route("lib", "invalid_hall")
    assert res_inv_dest.found is False
    assert "not found" in res_inv_dest.message.lower()
    
    # Disconnected graph handling
    dummy_locations = [
        Location(id="A", name="A", category="Cat", description="A", coordinates=Coordinates(x=0, y=0), tags=[]),
        Location(id="B", name="B", category="Cat", description="B", coordinates=Coordinates(x=10, y=10), tags=[]),
        Location(id="ISOLATED", name="Iso", category="Cat", description="Iso", coordinates=Coordinates(x=20, y=20), tags=[])
    ]
    dummy_edges = [
        Edge(**{"from": "A", "to": "B", "distance": 15.0, "path_type": "Walkway"})
    ]
    graph = CampusGraph(dummy_locations, dummy_edges, "meters")
    res_disc = graph.find_shortest_path("A", "ISOLATED")
    assert res_disc.found is False
    assert "no connected pathway" in res_disc.message.lower()
    print("PASSED: Invalid IDs and disconnected nodes are safely caught and return structured error messages.")
    return True

async def test_7_ollama_assistant_grounding():
    print("--- [TEST 7] Ollama Assistant Grounded Responses ---")
    status = await ai_service.check_ollama_status()
    print(f"Ollama status: {status}")
    
    # Known building query
    res = await ai_service.ask_assistant("Where is the Phillips Central Library and what study facilities does it have?")
    print(f"Response (model: {res.model}):\n{res.reply}\n")
    assert res.grounded_in_campus_data is True
    assert "lib" in res.reply.lower() or "library" in res.reply.lower()
    
    # Unknown building hallucination test
    res_hallucination = await ai_service.ask_assistant("Where is the Hogwarts Astronomy Tower on campus?")
    print(f"Hallucination test response:\n{res_hallucination.reply}\n")
    assert "not recorded" in res_hallucination.reply.lower() or "administration" in res_hallucination.reply.lower()
    print("PASSED: AI assistant utilizes campus dataset and rejects unrecorded facilities.")
    return True

async def test_8_ollama_offline_fallback():
    print("--- [TEST 8] Ollama Offline Graceful Degradation ---")
    offline_service = CampusAIService(base_url="http://127.0.0.1:9999")
    status = await offline_service.check_ollama_status()
    assert status["online"] is False
    
    res = await offline_service.ask_assistant("Where can I find lunch and dining?")
    assert res.ollama_online is False
    assert res.model == "local-fallback"
    assert "Dining" in res.reply or "Cafe" in res.reply or "offline" in res.reply
    print("PASSED: Offline Ollama returns keyword-grounded fallback response without crashing.")
    return True

def test_9_demo_notice_presence():
    print("--- [TEST 9] Demo Data Notice Verification ---")
    meta = campus_service.get_metadata()
    assert meta["is_demo_data"] is True
    assert "DEMO DATA" in meta["notice"]
    assert "synthetic" in meta["notice"].lower() or "prototyping" in meta["notice"].lower()
    
    # Check that frontend files contain the demo notice bar
    header_path = Path(__file__).resolve().parent.parent.parent / "frontend" / "components" / "Header.tsx"
    header_content = header_path.read_text(encoding="utf-8")
    assert "Demo Notice:" in header_content, "Header must display demo notice"
    assert "Synthetic Demo" in header_content, "Header must have Synthetic Demo badge"
    print("PASSED: Synthetic demo notices are clearly prominent in both backend metadata and frontend Header.")
    return True

def test_10_production_build_artifact_check():
    print("--- [TEST 10] Frontend Production Build Output ---")
    build_dir = Path(__file__).resolve().parent.parent.parent / "frontend" / ".next"
    assert build_dir.exists(), "Frontend .next directory must exist from production build"
    pages_manifest = build_dir / "server" / "pages-manifest.json"
    app_paths_manifest = build_dir / "server" / "app-paths-manifest.json"
    assert app_paths_manifest.exists() or pages_manifest.exists(), "Next.js build manifests must exist"
    print("PASSED: Frontend production build output verified (.next manifests present).")
    return True

async def main():
    print("==================================================")
    print("ROUTE CRAFT AI — STAGE 5 END-TO-END VERIFICATION")
    print("==================================================\n")
    
    results = {}
    
    try:
        results["1. Backend Health Endpoint"] = test_1_health_endpoint()
    except Exception as e:
        print(f"FAILED [TEST 1]: {e}")
        results["1. Backend Health Endpoint"] = False

    try:
        results["2. Campus Locations Loading"] = test_2_campus_locations_load()
    except Exception as e:
        print(f"FAILED [TEST 2]: {e}")
        results["2. Campus Locations Loading"] = False

    try:
        results["3. Location Search Filtering"] = test_3_search_filtering()
    except Exception as e:
        print(f"FAILED [TEST 3]: {e}")
        results["3. Location Search Filtering"] = False

    try:
        results["4. Shortest Path Routing"] = test_4_route_calculation()
    except Exception as e:
        print(f"FAILED [TEST 4]: {e}")
        results["4. Shortest Path Routing"] = False

    try:
        results["5. Route Highlighting on Map"] = test_5_route_highlighting_logic()
    except Exception as e:
        print(f"FAILED [TEST 5]: {e}")
        results["5. Route Highlighting on Map"] = False

    try:
        results["6. Invalid Locations & Disconnected Routes"] = test_6_invalid_locations_and_disconnected_routes()
    except Exception as e:
        print(f"FAILED [TEST 6]: {e}")
        results["6. Invalid Locations & Disconnected Routes"] = False

    try:
        results["7. Ollama Assistant with Campus Data"] = await test_7_ollama_assistant_grounding()
    except Exception as e:
        print(f"FAILED [TEST 7]: {e}")
        results["7. Ollama Assistant with Campus Data"] = False

    try:
        results["8. Ollama Offline Graceful Degradation"] = await test_8_ollama_offline_fallback()
    except Exception as e:
        print(f"FAILED [TEST 8]: {e}")
        results["8. Ollama Offline Graceful Degradation"] = False

    try:
        results["9. Demo Data Notice Visibility"] = test_9_demo_notice_presence()
    except Exception as e:
        print(f"FAILED [TEST 9]: {e}")
        results["9. Demo Data Notice Visibility"] = False

    try:
        results["10. Frontend Production Build"] = test_10_production_build_artifact_check()
    except Exception as e:
        print(f"FAILED [TEST 10]: {e}")
        results["10. Frontend Production Build"] = False

    print("\n==================================================")
    print("STAGE 5 TEST SUMMARY")
    print("==================================================")
    all_passed = True
    for name, passed in results.items():
        status_str = "PASSED" if passed else "FAILED"
        print(f"[{status_str}] {name}")
        if not passed:
            all_passed = False
            
    print("==================================================")
    if all_passed:
        print("ALL 10 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    else:
        print("SOME VERIFICATION CHECKS FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
