"""
RouteCraft AI — Root Entry Point
Allows starting the FastAPI backend directly from repository root via:
    python app.py
"""
import sys
from pathlib import Path
import uvicorn

# Ensure backend directory is in sys.path
backend_path = Path(__file__).resolve().parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.main import app

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
