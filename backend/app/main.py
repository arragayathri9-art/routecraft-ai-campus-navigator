from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import ALLOWED_ORIGINS
from .routers import locations_router, routes_router, chat_router, health_router
from .services.campus_service import campus_service

app = FastAPI(
    title="RouteCraft AI — Aurora Campus Navigator API",
    description="Intelligent campus navigation, Dijkstra shortest-path calculations, and grounded AI assistant for Aurora University.",
    version="1.0.0",
)

# Configure CORS for Next.js frontend development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(health_router)
app.include_router(locations_router)
app.include_router(routes_router)
app.include_router(chat_router)

@app.get("/")
def read_root():
    meta = campus_service.get_metadata()
    return {
        "project": "RouteCraft AI — Aurora Campus Navigator",
        "campus": meta.get("campus_name", "Aurora University"),
        "is_demo_data": meta.get("is_demo_data", True),
        "notice": meta.get("notice"),
        "docs_url": "/docs",
        "health_url": "/api/health",
        "locations_url": "/api/locations",
    }
