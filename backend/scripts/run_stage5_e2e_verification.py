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
    
    # Check that edges include has_stairs, ramp_available, and accessibility_verified
    edges = graph_data["edges"]
    assert len(edges) >= 20
    first_edge = edges[0]
    assert "has_stairs" in first_edge and "ramp_available" in first_edge and "accessibility_verified" in first_edge
    print(f"PASSED: All {len(required_ids)} campus landmarks and 20 accessibility-annotated edges loaded.")
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

def test_4_route_calculation_and_accessibility_preferences():
    print("--- [TEST 4] Dijkstra Route Calculation & Accessibility Preferences ---")
    # 1. Normal Shortest Route (North Gate -> South Gate)
    res_default = campus_service.calculate_route("north_gate", "south_gate", preference="shortest")
    assert res_default.found is True, "Route north_gate -> south_gate must be found"
    assert res_default.total_distance == 720.0, f"Expected 720.0m shortest path, got {res_default.total_distance}"
    assert res_default.path_node_ids == ["north_gate", "lib", "quad", "gym", "south_gate"]
    assert len(res_default.steps) == 4
    
    # 2. Shortest Mode takes stairs when direct: Science (sci) -> Engineering (eng)
    res_short = campus_service.calculate_route("sci", "eng", preference="shortest")
    assert res_short.found is True
    assert res_short.total_distance == 190.0
    assert res_short.path_node_ids == ["sci", "eng"]
    assert res_short.steps[0].has_stairs is True, "Direct sci->eng edge has stairs"

    # 3. Avoid Stairs Mode avoids direct stairs and detours via lib & quad: sci -> lib -> quad -> eng = 650.0m
    res_avoid = campus_service.calculate_route("sci", "eng", preference="avoid_stairs")
    assert res_avoid.found is True
    assert res_avoid.total_distance == 650.0, f"Expected 650.0m detour, got {res_avoid.total_distance}"
    assert res_avoid.path_node_ids == ["sci", "lib", "quad", "eng"]
    assert all(not s.has_stairs or s.ramp_available for s in res_avoid.steps), "Must not have unramped stairs"

    # 4. Wheelchair-Friendly Mode requires verified barrier-free path
    res_wc = campus_service.calculate_route("sci", "eng", preference="wheelchair")
    assert res_wc.found is True
    assert res_wc.total_distance == 650.0
    assert res_wc.is_accessible_verified is True
    assert "Wheelchair-accessible" in res_wc.preference_explanation

    print("PASSED: Accessibility preferences (Shortest, Avoid Stairs, Wheelchair) filter pathways correctly.")
    return True

def test_5_route_highlighting_logic():
    print("--- [TEST 5] Route Map Highlighting & Selection Rationale ---")
    res = campus_service.calculate_route("sci", "eng", preference="wheelchair")
    ids = res.path_node_ids
    active_route_pairs = set()
    for i in range(len(ids) - 1):
        active_route_pairs.add(f"{ids[i]}->{ids[i+1]}")
        active_route_pairs.add(f"{ids[i+1]}->{ids[i]}")
    
    # Verify detour edges are in active route
    assert "sci->lib" in active_route_pairs
    assert "lib->quad" in active_route_pairs
    assert "quad->eng" in active_route_pairs
    assert "sci->eng" not in active_route_pairs
    assert res.preference_explanation is not None
    assert len(res.preference_explanation) > 10
    print("PASSED: Highlighting edge pairs and preference rationale verified.")
    return True

def test_6_invalid_locations_and_no_suitable_route():
    print("--- [TEST 6] Invalid Locations & Inaccessible / No Suitable Route Handling ---")
    # Invalid start
    res_inv = campus_service.calculate_route("invalid_gate", "lib")
    assert res_inv.found is False
    assert "not found" in res_inv.message.lower()

    # Isolated node in graph
    dummy_locations = [
        Location(id="A", name="A", category="Cat", description="A", coordinates=Coordinates(x=0, y=0), tags=[]),
        Location(id="STAIRS_NODE", name="Stairs Tower", category="Cat", description="Stairs only", coordinates=Coordinates(x=10, y=10), tags=[]),
    ]
    # Connected strictly by unramped stairs
    dummy_edges = [
        Edge(**{"from": "A", "to": "STAIRS_NODE", "distance": 20.0, "path_type": "Steep Steps", "accessible": False, "has_stairs": True, "ramp_available": False, "accessibility_verified": True})
    ]
    graph = CampusGraph(dummy_locations, dummy_edges, "meters")

    # Shortest should find it
    res_s = graph.find_shortest_path("A", "STAIRS_NODE", preference="shortest")
    assert res_s.found is True

    # Avoid stairs must return found: False with informative message
    res_avoid = graph.find_shortest_path("A", "STAIRS_NODE", preference="avoid_stairs")
    assert res_avoid.found is False
    assert "no suitable route avoiding stairs" in res_avoid.message.lower()

    # Wheelchair must return found: False with informative message
    res_wc = graph.find_shortest_path("A", "STAIRS_NODE", preference="wheelchair")
    assert res_wc.found is False
    assert "no suitable wheelchair-friendly route" in res_wc.message.lower()

    print("PASSED: Inaccessible paths produce informative failure messages instead of returning unsuitable routes.")
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
    
    res = await offline_service.ask_assistant("Can I get a wheelchair accessible route on campus?")
    assert res.ollama_online is False
    assert res.model == "local-fallback"
    assert "Accessibility-Aware" in res.reply or "Wheelchair" in res.reply or "offline" in res.reply
    print("PASSED: Offline Ollama returns keyword-grounded accessibility navigation instructions without crashing.")
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
    print("ROUTE CRAFT AI — STEP 7 ACCESSIBILITY E2E TESTS")
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
        results["4. Dijkstra Routing & Accessibility Preferences"] = test_4_route_calculation_and_accessibility_preferences()
    except Exception as e:
        print(f"FAILED [TEST 4]: {e}")
        results["4. Dijkstra Routing & Accessibility Preferences"] = False

    try:
        results["5. Route Highlighting & Explanation"] = test_5_route_highlighting_logic()
    except Exception as e:
        print(f"FAILED [TEST 5]: {e}")
        results["5. Route Highlighting & Explanation"] = False

    try:
        results["6. Invalid Locations & Inaccessible Routes"] = test_6_invalid_locations_and_no_suitable_route()
    except Exception as e:
        print(f"FAILED [TEST 6]: {e}")
        results["6. Invalid Locations & Inaccessible Routes"] = False

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
    print("STEP 7 ACCESSIBILITY VERIFICATION SUMMARY")
    print("==================================================")
    all_passed = True
    for name, passed in results.items():
        status_str = "PASSED" if passed else "FAILED"
        print(f"[{status_str}] {name}")
        if not passed:
            all_passed = False
            
    print("==================================================")
    if all_passed:
        print("ALL STEP 7 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    else:
        print("SOME VERIFICATION CHECKS FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
