# MBP Backend v2.0

MirrorBreak Protocol v2.0 - AI-powered psychological structural analysis API built with FastAPI and LangGraph.

## Overview

MBP v2.0 is a modular multi-agent system that analyzes psychological patterns through structured conversations. It uses LangGraph to orchestrate 22+ specialized agents across 7 processing layers:

1. **Intake** - Safety screening
2. **Extraction** - Signal detection (linguistic, emotional, cognitive, behavioral)
3. **Synthesis** - Pattern merging
4. **Contextualization** - Cultural/temporal framing
5. **Hypothesis** - Parallel generation across 5 domains
6. **Validation** - Evidence evaluation & gap analysis
7. **Assessment** - 12D matrix positioning
8. **Output** - Profile composition

## Prerequisites

- **Python**: 3.10 or higher (tested with 3.12.3)
- **Virtual Environment**: Recommended for dependency isolation
- **API Key**: Moonshot AI API key (for LLM functionality)
- **Memory**: 2GB RAM minimum (4GB recommended)
- **Disk**: 500MB for code + dependencies

## Step-by-Step Setup

### 1. Navigate to Project Directory

```bash
cd /mnt/d/Yoel/Projects/mbp-prototype/backend-v2
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Upgrade pip

```bash
pip install --upgrade pip
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `fastapi>=0.104.0` - Web framework
- `uvicorn[standard]>=0.24.0` - ASGI server
- `pydantic>=2.5.0` - Data validation
- `langgraph>=0.0.40` - Agent orchestration
- `langchain-openai>=0.0.5` - LLM integration
- `python-dotenv>=1.0.0` - Environment management

### 6. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Required
MOONSHOT_API_KEY=your_moonshot_api_key_here

# Optional (defaults shown)
API_HOST=0.0.0.0
API_PORT=8000
```

**Note:** The server can start without an API key, but requests requiring LLM processing will fail.

## How to Run the Server

### Development Mode (with auto-reload)

```bash
python main.py
```

Or using the run script:

```bash
./run.sh
```

### Production Mode (no reload)

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### With Custom Settings

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once running, access interactive docs at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/sessions` | Create new session |
| POST | `/sessions/{id}/respond` | Send user message |
| GET | `/sessions/{id}` | Get session state |
| GET | `/sessions/{id}/profile` | Get final profile |

## Testing the API

### Using curl

#### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "agents_count": 22,
  "mode": "balanced"
}
```

#### 2. Create Session

```bash
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "metadata": {}}'
```

**Expected Response:**
```json
{
  "session_id": "uuid-string",
  "status": "created",
  "created_at": "2024-...",
  "next_question": "Halo! Saya akan membantu Anda memahami pola pikir dan struktur psikologis Anda. Ceritakan sedikit tentang diri Anda dan apa yang ingin Anda pahami?"
}
```

#### 3. Send User Response

```bash
curl -X POST http://localhost:8000/sessions/{session_id}/respond \
  -H "Content-Type: application/json" \
  -d '{"message": "Saya cenderung perfeksionis dan suka menganalisis segala sesuatu sebelum bertindak."}'
```

**Expected Response:**
```json
{
  "session_id": "uuid-string",
  "phase": "probe",
  "next_question": "Ceritakan tentang situasi...",
  "final_profile": null,
  "iteration_count": 1,
  "processing_time_ms": 45000
}
```

#### 4. Get Session State

```bash
curl http://localhost:8000/sessions/{session_id}
```

#### 5. Get Final Profile

```bash
curl http://localhost:8000/sessions/{session_id}/profile
```

### Using Python Test Script

A test script is included for full workflow testing:

```bash
# First, set your API key in the environment
export MOONSHOT_API_KEY=your_key_here

# Run the test
python test_v2.py
```

**Note:** The test script reads from `/mnt/d/Yoel/projects/mbp-prototype/backend/.env` by default. Edit the path in `test_v2.py` if needed.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MOONSHOT_API_KEY` | Yes* | - | Moonshot AI API key |
| `API_HOST` | No | `0.0.0.0` | Server bind address |
| `API_PORT` | No | `8000` | Server port |

*The server can start without the API key, but LLM-dependent endpoints will fail.

## Project Structure

```
backend-v2/
├── api/
│   ├── main.py          # FastAPI application
│   └── models.py        # Pydantic request/response models
├── agents/
│   ├── base.py          # Base agent class
│   ├── intake.py        # Safety screening agent
│   ├── synthesis.py     # Pattern synthesis agent
│   ├── contextualizer.py # Context addition agent
│   ├── validation.py    # Evidence & gap analysis
│   ├── probes.py        # Question generation
│   ├── assessment.py    # 12D matrix positioning
│   ├── output.py        # Profile composition
│   ├── extractors/      # Signal extraction agents
│   │   ├── linguistic.py
│   │   ├── emotional.py
│   │   ├── cognitive.py
│   │   ├── behavioral.py
│   │   └── runner.py
│   └── hypothesis/      # Hypothesis generators
│       ├── generators.py
│       └── runner.py
├── core/
│   ├── config.py        # Global configuration
│   └── llm.py           # LLM setup
├── graph/
│   ├── state.py         # State definitions
│   └── graph.py         # LangGraph orchestration
├── prompts/             # System prompts
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── test_v2.py          # Test script
├── run.sh              # Run script
└── .env                # Environment variables (create this)
```

## Performance Modes

Configure processing mode via `core/config.py` or at runtime:

```python
from core.config import set_fast_mode, set_balanced_mode, set_accuracy_mode

# Fast mode - quicker responses, lower accuracy
set_fast_mode()

# Balanced mode - default
set_balanced_mode()

# Accuracy mode - slower, more thorough
set_accuracy_mode()
```

| Mode | History | Temperature | Best For |
|------|---------|-------------|----------|
| Fast | 5 messages | 0.3 | Development, testing |
| Balanced | 10 messages | 0.2 | Production default |
| Accuracy | 15 messages | 0.1 | Deep analysis |

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError` when running the server

**Solution:** Ensure virtual environment is activated:
```bash
source venv/bin/activate
```

### API Key Not Set

**Problem:** Server starts but requests fail with API key error

**Solution:** Create `.env` file with valid `MOONSHOT_API_KEY`

### Port Already in Use

**Problem:** `Address already in use` error

**Solution:** Kill existing process or use different port:
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or run on different port
python -c "import uvicorn; uvicorn.run('api.main:app', host='0.0.0.0', port=8001)"
```

### Memory Issues

**Problem:** Process killed or very slow responses

**Solution:** Reduce memory usage in `core/config.py`:
```python
MAX_HISTORY_MESSAGES = 5  # Default: 10
MAX_SIGNALS_PER_TYPE = 5  # Default: 10
```

### LLM Timeout

**Problem:** Requests timeout during processing

**Solution:** Adjust timeout in your client or use Fast Mode.

### CORS Errors (Frontend)

**Problem:** Browser blocks requests from different origin

**Solution:** CORS is configured to allow all origins (`["*"]`) in development. For production, update `api/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Replace with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Development Notes

### Adding New Agents

1. Create agent class inheriting from `MBPAgent` in `agents/`
2. Implement `process(self, state)` method
3. Add node function in `graph/graph.py`
4. Connect to graph edges

### State Management

Sessions are stored in-memory (Python dict). For production:
- Replace with Redis or database
- Implement session persistence in `api/main.py`

### Logging

Agent execution times are logged to state:
```python
state["node_execution_times"]["agent_name"] = elapsed_time
```

## License

Proprietary - All rights reserved.

## Support

For issues or questions, refer to:
- `API-DOCUMENTATION.md` - Detailed API reference
- `DEPLOYMENT.md` - Production deployment guide
- Code comments in `agents/` - Agent logic documentation
