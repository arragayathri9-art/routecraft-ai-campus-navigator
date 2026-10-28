import logging
from typing import Dict, Any, List, Optional
# pyrefly: ignore [missing-import]
import httpx

from ..config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT_SECONDS
from .campus_service import campus_service
from ..models.schemas import ChatResponse, ChatMessage

logger = logging.getLogger("ai_service")

class CampusAIService:
    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model: str = OLLAMA_MODEL,
        timeout: float = OLLAMA_TIMEOUT_SECONDS
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def check_ollama_status(self) -> Dict[str, Any]:
        """Checks if local Ollama daemon is reachable and lists available models."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    model_found = any(self.model in m for m in models)
                    return {
                        "online": True,
                        "status": "ready" if model_found else "model_missing",
                        "available_models": models,
                        "target_model": self.model,
                    }
                return {
                    "online": False,
                    "status": f"http_error_{res.status_code}",
                    "available_models": [],
                    "target_model": self.model,
                }
        except httpx.ConnectError:
            return {
                "online": False,
                "status": "offline_connection_refused",
                "available_models": [],
                "target_model": self.model,
            }
        except Exception as e:
            return {
                "online": False,
                "status": f"error_{str(e)}",
                "available_models": [],
                "target_model": self.model,
            }

    def _build_campus_context(self) -> str:
        """Serializes current campus data into structured text for grounding."""
        if not campus_service.campus_data:
            return "No campus data loaded."

        lines = [
            f"CAMPUS: {campus_service.campus_data.campus_name} (DEMO DATA)",
            "CAMPUS BUILDINGS AND FACILITIES:"
        ]
        for loc in campus_service.campus_data.locations:
            tags_str = ", ".join(loc.tags)
            lines.append(
                f"- {loc.name} (ID: {loc.id}, Category: {loc.category}, Floor: {loc.floor}): "
                f"{loc.description} [Tags: {tags_str}]"
            )

        lines.append("\nCAMPUS PATHWAY CONNECTIONS & ACCESSIBILITY:")
        for edge in campus_service.campus_data.edges:
            stair_info = "stairs present" if edge.has_stairs else "no stairs"
            ramp_info = "ramp available" if edge.ramp_available else "no ramp"
            ver_info = "verified accessible" if edge.accessibility_verified else "accessibility unverified"
            lines.append(
                f"- From {edge.from_node} to {edge.to_node}: ~{edge.distance} meters via {edge.path_type} "
                f"[{stair_info}, {ramp_info}, {ver_info}]."
            )

        return "\n".join(lines)

    def _generate_fallback_answer(self, user_query: str) -> str:
        """
        Keyword-based offline answer generator when Ollama is unreachable,
        ensuring the user still gets helpful campus navigation answers.
        """
        q = user_query.lower()
        matched_locations = campus_service.get_locations(query=user_query)

        if matched_locations:
            loc = matched_locations[0]
            return (
                f"*(Ollama service offline — fallback campus lookup)*\n\n"
                f"**{loc.name}** ({loc.category})\n"
                f"- **Description:** {loc.description}\n"
                f"- **Floor:** {loc.floor}\n"
                f"- **Tags:** {', '.join(loc.tags)}\n\n"
                f"You can select this location on the map or use the Route Finder to calculate walking directions."
            )

        if "wheelchair" in q or "accessible" in q or "disability" in q or "ramp" in q or "stairs" in q:
            return (
                "*(Ollama service offline — fallback campus lookup)*\n\n"
                "**Accessibility-Aware Navigation on Aurora Campus:**\n"
                "RouteCraft AI supports 3 routing preferences:\n"
                "- **Shortest Route**: Direct shortest path across all walkways.\n"
                "- **Wheelchair-Friendly Route**: Routes through verified barrier-free paths and ramps (avoids unramped stairs and unverified trails).\n"
                "- **Avoid Stairs**: Bypasses physical staircases and stepped corridors.\n\n"
                "Select your preferred mode in the Route Finder on the sidebar to compute customized navigation."
            )

        if "dining" in q or "food" in q or "eat" in q or "lunch" in q or "coffee" in q:
            return (
                "*(Ollama service offline — fallback campus lookup)*\n\n"
                "For dining and refreshments on Aurora campus:\n"
                "- **Aurora Dining Hall & Cafe**: All-day dining, salad bar, vegan options, espresso bar (Ground floor).\n"
                "- **Spartan Student Union**: Snack hubs and coffee counters."
            )

        if "library" in q or "study" in q or "books" in q or "quiet" in q:
            return (
                "*(Ollama service offline — fallback campus lookup)*\n\n"
                "For studying and research:\n"
                "- **Phillips Central Library**: 4 stories of quiet study areas, collaborative pods, and 24/7 IT helpdesk."
            )

        if "gym" in q or "sports" in q or "fitness" in q or "pool" in q:
            return (
                "*(Ollama service offline — fallback campus lookup)*\n\n"
                "For recreation and workouts:\n"
                "- **Spartan Athletic & Wellness Center**: Indoor track, Olympic pool, fitness gym, and courts."
            )

        return (
            "*(Ollama service offline)*\n\n"
            "I could not reach the local Ollama instance (llama3.2). "
            "Please check that Ollama is running (`ollama serve`). "
            "In the meantime, you can search buildings using the campus search bar or select endpoints to calculate walking routes."
        )

    async def ask_assistant(
        self,
        message: str,
        history: Optional[List[ChatMessage]] = None,
        current_location_id: Optional[str] = None
    ) -> ChatResponse:
        """
        Sends grounded query to Ollama or falls back to local knowledge retrieval.
        """
        status_info = await self.check_ollama_status()
        campus_context = self._build_campus_context()

        # Context about current user location if known
        user_loc_context = ""
        if current_location_id:
            curr_loc = campus_service.get_location_by_id(current_location_id)
            if curr_loc:
                user_loc_context = f"\nThe user is currently at or viewing: {curr_loc.name} ({curr_loc.id})."

        system_instruction = (
            "You are RouteCraft AI, the intelligent campus assistant for Aurora University.\n"
            "STRICT GROUNDING & ACCURACY RULES:\n"
            "1. Answer using ONLY the official campus dataset provided below.\n"
            "2. NEVER INVENT OR HALLUCINATE building locations, walkway distances, room numbers, accessibility ramps, elevators, or official university policies.\n"
            "3. If the user asks about a building, service, facility, room, or external place NOT in this dataset, explicitly reply: "
            "'This facility/location is not recorded in the Aurora University campus dataset. Please consult campus administration or student services for verified details.'\n"
            "4. If asked about wheelchair accessibility, note that while pathways are labelled as accessible walkways in the demo prototype, detailed elevator and ramp survey data is not yet verified.\n"
            "5. Remind the user that building coordinates and distances are based on a synthetic demonstration prototype for Aurora University.\n"
            "6. Keep answers structured, friendly, and concise with bullet points where appropriate.\n\n"
            f"--- CAMPUS DATA ---\n{campus_context}\n{user_loc_context}\n--- END CAMPUS DATA ---"
        )

        suggestions = [
            "Where can I find a quiet place to study?",
            "What dining options are available on campus?",
            "Where is Turing Engineering & Robotics Hall?",
            "How far is the walk from North Gate to the Library?"
        ]

        if not status_info["online"]:
            fallback = self._generate_fallback_answer(message)
            return ChatResponse(
                reply=fallback,
                model="local-fallback",
                grounded_in_campus_data=True,
                ollama_online=False,
                suggestions=suggestions
            )

        # Prepare messages payload for Ollama chat API
        messages_payload = [{"role": "system", "content": system_instruction}]

        if history:
            for h in history[-6:]: # Include last few conversation turns
                messages_payload.append({"role": h.role, "content": h.content})

        messages_payload.append({"role": "user", "content": message})

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages_payload,
                        "stream": False,
                        "options": {
                            "temperature": 0.2,
                            "top_p": 0.85,
                        }
                    }
                )

                if res.status_code == 200:
                    data = res.json()
                    bot_message = data.get("message", {}).get("content", "").strip()
                    return ChatResponse(
                        reply=bot_message,
                        model=self.model,
                        grounded_in_campus_data=True,
                        ollama_online=True,
                        suggestions=suggestions
                    )
                else:
                    logger.warning(f"Ollama returned HTTP {res.status_code}: {res.text}")
                    fallback = self._generate_fallback_answer(message)
                    return ChatResponse(
                        reply=fallback,
                        model=f"fallback-(http-{res.status_code})",
                        grounded_in_campus_data=True,
                        ollama_online=False,
                        suggestions=suggestions
                    )

        except Exception as e:
            logger.error(f"Error communicating with Ollama: {e}", exc_info=True)
            fallback = self._generate_fallback_answer(message)
            return ChatResponse(
                reply=fallback,
                model="fallback-exception",
                grounded_in_campus_data=True,
                ollama_online=False,
                suggestions=suggestions
            )

ai_service = CampusAIService()
