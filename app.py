"""
RouteCraft AI — Root Entry Point
Allows starting the FastAPI backend directly from repository root via:
    python app.py
"""
import sys
from pathlib import Path
import uvicorn

# Ensure repository root and backend directory are in sys.path
root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / "backend"

for path in [str(root_dir), str(backend_dir)]:
    if path not in sys.path:
        sys.path.insert(0, path)

from backend.app.main import app

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
