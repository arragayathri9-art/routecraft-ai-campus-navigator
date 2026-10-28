# RouteCraft AI — Aurora Campus Navigator

RouteCraft AI is an intelligent smart campus navigation web application built for Aurora University. It calculates optimal walking routes across campus landmarks using Dijkstra's shortest-path algorithm and provides a grounded campus assistant powered by a locally hosted Ollama large language model (`llama3.2:latest`).

---

## 📌 Features

- **Dijkstra Shortest Path Routing**: Calculates optimal point-to-point walking paths, distances (in meters), and turn-by-turn navigation instructions.
- **Campus Data Validation**: Fictional demo dataset for Aurora University with buildings, categories, coordinates, and accessible walkway edges.
- **Local AI Assistant (Ollama)**: Answers student and visitor campus inquiries grounded strictly in dataset knowledge, clearly acknowledging unknown locations.
- **Resilient Fallback**: Offline detection when the Ollama service is disconnected or unreachable.
- **Visible Demo Notice**: Distinct label ensuring prototype synthetic data is not confused with official campus surveys.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.14 / FastAPI, Uvicorn, Pydantic V2, HTTPX, Pytest
- **Routing Engine**: Dijkstra's algorithm with priority queues (`heapq`)
- **Campus AI**: Ollama Local API (`llama3.2:latest`)
- **Frontend** *(Stage 3)*: Next.js, TypeScript, Tailwind CSS, Leaflet 2D schematic map

---

## 📂 Repository Structure

```text
rootcraft_niat/
├── backend/
│   ├── app/
│   │   ├── data/
│   │   │   └── campus_data.json       # Aurora University demo dataset
│   │   ├── models/
│   │   │   └── schemas.py             # Pydantic data schemas
│   │   ├── routing/
│   │   │   └── dijkstra.py            # Shortest-path graph algorithm
│   │   ├── services/
│   │   │   ├── campus_service.py      # Campus lookup & filtering
│   │   │   └── ai_service.py          # Grounded Ollama integration
│   │   ├── routers/
│   │   │   ├── health.py              # /api/health
│   │   │   ├── locations.py           # /api/locations, /api/categories, /api/graph
│   │   │   ├── routes.py              # /api/route (POST & GET)
│   │   │   └── chat.py                # /api/chat
│   │   ├── config.py                  # Environment settings & model config
│   │   └── main.py                    # FastAPI application & CORS
│   ├── tests/
│   │   ├── test_routing.py            # Dijkstra unit tests
│   │   └── test_api.py                # Endpoints integration tests
│   ├── pytest.ini
│   └── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🚀 Quick Start (Windows PowerShell)

### 1. Prerequisites
- **Python**: 3.10+ (Verified on Python 3.14.0)
- **Ollama**: Installed with `llama3.2:latest` model pulled (`ollama pull llama3.2`)

### 2. Backend Setup
Open a Windows PowerShell terminal in the repository root:

```powershell
# Navigate to the backend directory
cd backend

# Create virtual environment (if not already created)
py -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run automated tests
pytest -v

# Start the FastAPI Development Server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Frontend Setup
Open a second Windows PowerShell terminal in the repository root:

```powershell
# Navigate to the frontend directory
cd frontend

# Install Node dependencies
npm install

# Start the Next.js development server
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser to view the application.
The API will be accessible at:
- **Root Info & Demo Notice**: `http://127.0.0.1:8000/`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **ReDoc Documentation**: `http://127.0.0.1:8000/redoc`

---

## 📡 API Endpoints

### 1. Health & Status
- **`GET /api/health`**
  Returns service status, loaded location count, demo data flag, and Ollama connection status.

### 2. Locations & Topology
- **`GET /api/locations`**: List all locations.
  - Query parameters: `?q=library` (search), `?category=Academic` (filter).
- **`GET /api/locations/{location_id}`**: Get single building by ID (e.g. `/api/locations/lib`).
- **`GET /api/categories`**: List distinct categories.
- **`GET /api/graph`**: Full graph containing nodes, coordinates, and pathway edges for map rendering.

### 3. Routing (Dijkstra)
- **`POST /api/route`**
  ```json
  {
    "start_id": "north_gate",
    "destination_id": "lib"
  }
  ```
- **`GET /api/route?start_id=north_gate&destination_id=lib`**
  Returns optimal path, distance in meters, ordered waypoints, and step-by-step walking instructions.

### 4. Grounded Campus AI Assistant
- **`POST /api/chat`**
  ```json
  {
    "message": "Where is the library and how do I study there?",
    "current_location_id": "north_gate"
  }
  ```
  Returns answers grounded in Aurora University's dataset or clarifies when information is unknown.

---

## 🤖 Local Ollama Setup (No Paid API Keys Required)

RouteCraft AI runs **100% locally** using Ollama. It requires **no paid cloud API keys** (no OpenAI, Anthropic, or Google Cloud accounts required).

### 1. Install & Verify Ollama
1. Download Ollama from [ollama.com](https://ollama.com) and install it on your machine.
2. In PowerShell, pull the lightweight LLaMA 3.2 model:
   ```powershell
   ollama pull llama3.2
   ```
3. Verify that the model is installed:
   ```powershell
   ollama list
   ```

### 2. Environment Variables Configuration
The application reads configuration from environment variables with sensible local defaults:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | URL of the local Ollama daemon service |
| `OLLAMA_MODEL` | `llama3.2:latest` | Target model name used for campus assistant chat |
| `OLLAMA_TIMEOUT_SECONDS` | `90.0` | Timeout threshold for asynchronous HTTP requests |
| `CAMPUS_DATA_PATH` | `app/data/campus_data.json` | Path to the verified or demo campus dataset |
| `NEXT_PUBLIC_API_URL`| `http://127.0.0.1:8000/api` | Base API URL used by the Next.js frontend |

To override any configuration in PowerShell before launching the backend:
```powershell
$env:OLLAMA_MODEL = "llama3.2:latest"
$env:OLLAMA_TIMEOUT_SECONDS = "90.0"
```

---

## 🔒 Security & Privacy Considerations

1. **Local-Only Inference**: All campus assistant queries, navigation requests, and conversation history are processed entirely on your local machine by Ollama. No user prompt data or coordinates are transmitted over the public internet.
2. **Hallucination & Grounding Guardrails**: The system prompt strictly limits assistant answers to the official campus dataset provided. The assistant is instructed never to invent building coordinates, room numbers, accessibility ramps, or administrative policies. If a facility is not in the dataset, it explicitly states this fact.
3. **CORS Boundary Enforcement**: FastAPI CORS middleware restricts API requests to local frontend origins (`http://localhost:3000`, `http://127.0.0.1:3000`).
4. **Data Integrity Notice**: Because official surveyed coordinates for Aurora University require field validation, all prototype layouts are explicitly flagged with a visible demo disclaimer to prevent user confusion with real-world navigation.

---

## 📄 License
MIT License. See [LICENSE](LICENSE) for details.
