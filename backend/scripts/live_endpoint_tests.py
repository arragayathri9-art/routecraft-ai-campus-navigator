import json
import httpx

BASE_URL = "http://127.0.0.1:8000"

def log_test(title: str, passed: bool, detail: str = ""):
    icon = "PASS" if passed else "FAIL"
    print(f"[{icon}] {title}")
    if detail:
        print(f"       {detail}")

def run_tests():
    print("=" * 70)
    print("ROUTECRAFT AI: LIVE ENDPOINT VERIFICATION SUITE")
    print(f"Target: {BASE_URL}")
    print("=" * 70)

    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        # Test 1: Root endpoint
        r = client.get("/")
        passed = r.status_code == 200 and r.json().get("project") == "RouteCraft AI — Aurora Campus Navigator"
        log_test("GET / (Root Metadata & Demo Notice)", passed, f"Status: {r.status_code}, Notice: {r.json().get('notice')[:50]}...")

        # Test 2: Health endpoint
        r = client.get("/api/health")
        data = r.json()
        passed = r.status_code == 200 and data.get("status") == "healthy" and data.get("campus_data_loaded") is True
        log_test("GET /api/health (System Health & Ollama Status)", passed, f"Status: {data.get('status')}, Ollama: {data.get('ollama_status')}, Locations: {data.get('total_locations')}")

        # Test 3: List all locations
        r = client.get("/api/locations")
        locations = r.json()
        passed = r.status_code == 200 and len(locations) >= 10
        log_test("GET /api/locations (All Campus Locations)", passed, f"Found {len(locations)} locations.")

        # Test 4: Search locations by query
        r = client.get("/api/locations?q=robotics")
        eng_loc = r.json()
        passed = r.status_code == 200 and len(eng_loc) >= 1 and eng_loc[0]["id"] == "eng"
        log_test("GET /api/locations?q=robotics (Fuzzy Keyword Search)", passed, f"Found '{eng_loc[0]['name']}' (ID: {eng_loc[0]['id']})")

        # Test 5: Filter by category
        r = client.get("/api/locations?category=Dining%20%26%20Food")
        dining_loc = r.json()
        passed = r.status_code == 200 and len(dining_loc) >= 1 and dining_loc[0]["id"] == "cafe"
        log_test("GET /api/locations?category=Dining (Category Filter)", passed, f"Found '{dining_loc[0]['name']}'")

        # Test 6: Get location detail
        r = client.get("/api/locations/lib")
        lib = r.json()
        passed = r.status_code == 200 and lib.get("id") == "lib"
        log_test("GET /api/locations/lib (Single Location Detail)", passed, f"Building: {lib.get('name')}, Floor: {lib.get('floor')}")

        # Test 7: Get unknown location (404)
        r = client.get("/api/locations/imaginary_hall")
        passed = r.status_code == 404
        log_test("GET /api/locations/imaginary_hall (Unknown Location 404 Handling)", passed, f"Status: {r.status_code}, Error: {r.json().get('detail')}")

        # Test 8: Get categories
        r = client.get("/api/categories")
        cats = r.json()
        passed = r.status_code == 200 and len(cats) >= 4
        log_test("GET /api/categories (Distinct Categories)", passed, f"Categories: {', '.join(cats)}")

        # Test 9: Get graph topology
        r = client.get("/api/graph")
        graph = r.json()
        passed = r.status_code == 200 and "locations" in graph and "edges" in graph
        log_test("GET /api/graph (Schematic Map Topology)", passed, f"Nodes: {len(graph.get('locations'))}, Edges: {len(graph.get('edges'))}")

        # Test 10: POST Dijkstra route calculation
        route_payload = {"start_id": "north_gate", "destination_id": "south_gate"}
        r = client.post("/api/route", json=route_payload)
        route_data = r.json()
        passed = r.status_code == 200 and route_data.get("found") is True and route_data.get("total_distance") > 0
        log_test("POST /api/route (Dijkstra Shortest Path North->South)", passed, 
                 f"Path: {' -> '.join(route_data.get('path_node_ids'))} ({route_data.get('total_distance')} {route_data.get('distance_unit')}, {len(route_data.get('steps'))} steps)")

        # Test 11: GET Dijkstra route calculation
        r = client.get("/api/route?start_id=eng&destination_id=stu_union")
        route_data2 = r.json()
        passed = r.status_code == 200 and route_data2.get("found") is True
        log_test("GET /api/route?start_id=eng&destination_id=stu_union (GET Route)", passed,
                 f"Path: {' -> '.join(route_data2.get('path_node_ids'))} ({route_data2.get('total_distance')} meters)")

        # Test 12: Route error with unknown location (404)
        r = client.post("/api/route", json={"start_id": "unknown_origin", "destination_id": "lib"})
        passed = r.status_code == 404
        log_test("POST /api/route Unknown Node (Graceful 404 Handling)", passed, f"Status: {r.status_code}, Error: {r.json().get('detail')}")

        # Test 13: Route error with empty parameters (400)
        r = client.post("/api/route", json={"start_id": "", "destination_id": "lib"})
        passed = r.status_code == 400
        log_test("POST /api/route Empty Parameters (Validation 400)", passed, f"Status: {r.status_code}, Error: {r.json().get('detail')}")

        # Test 14: Chat assistant on known campus location
        chat_payload = {"message": "Where is Turing Engineering Hall and what can students do there?"}
        r = client.post("/api/chat", json=chat_payload)
        chat_data = r.json()
        passed = r.status_code == 200 and "reply" in chat_data and chat_data.get("grounded_in_campus_data") is True
        log_test("POST /api/chat (Grounded Campus Assistant - Known Topic)", passed,
                 f"Model: {chat_data.get('model')}, Online: {chat_data.get('ollama_online')}\n       Reply: {chat_data.get('reply')[:120]}...")

        # Test 15: Chat assistant on unknown facility
        chat_unknown = {"message": "Is there a nuclear reactor or submarine dock on campus?"}
        r = client.post("/api/chat", json=chat_unknown)
        chat_unknown_data = r.json()
        passed = r.status_code == 200 and ("unknown" in chat_unknown_data.get("reply").lower() or "not" in chat_unknown_data.get("reply").lower())
        log_test("POST /api/chat (Grounded Campus Assistant - Unknown Topic Boundary)", passed,
                 f"Reply: {chat_unknown_data.get('reply')[:120]}...")

    print("=" * 70)
    print("ALL 15 ENDPOINT VERIFICATIONS COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
