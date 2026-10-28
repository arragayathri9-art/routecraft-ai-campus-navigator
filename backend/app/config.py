import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE_PATH = os.environ.get(
    "CAMPUS_DATA_PATH",
    str(BASE_DIR / "data" / "campus_data.json")
)

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:latest")
OLLAMA_TIMEOUT_SECONDS = float(os.environ.get("OLLAMA_TIMEOUT_SECONDS", "90.0"))

ALLOWED_ORIGINS = [
    "https://routecraft-ai-campus-navigator-2.onrender.com",
    "https://routecraft-ai-campus-navigator-1.onrender.com",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "*"
]

# Allow additional origins via environment variables (comma-separated or single)
extra_origins = os.environ.get("ALLOWED_ORIGINS") or os.environ.get("FRONTEND_URL")
if extra_origins:
    for origin in extra_origins.split(","):
        cleaned = origin.strip().rstrip("/")
        if cleaned and cleaned not in ALLOWED_ORIGINS:
            ALLOWED_ORIGINS.append(cleaned)
