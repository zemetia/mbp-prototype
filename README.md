# MirrorBreak Protocol Prototype

Prototype implementation of MBP with AI agents (Kimi 2.5) for structural profiling.

## Features

- **Anonymous Sessions**: No login required, UUID-based session tracking
- **6-Phase Workflow**: Safety → Core → Adaptive → Mining → Validation → Synthesis → Debrief
- **5 AI Agents**: Analyzer, HypothesisMaker, QuestionMaker, Assessor, Synthesizer
- **Real-time WebSocket**: Live chat interface with Kimi 2.5
- **SQLite Storage**: Persistent session data, messages, hypotheses, 12D scores
- **Profile Viewer**: Downloadable structural profile with confidence intervals

## Quick Start

### 1. Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variable
export MOONSHOT_API_KEY="your-api-key"

# Run server
python main.py
```

Backend runs on `http://localhost:8000`

### 2. Setup Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

### 3. Access

Open browser to `http://localhost:5173` and start assessment.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions` | Create new session |
| GET | `/api/sessions/{id}` | Get session status |
| GET | `/api/sessions/{id}/history` | Get conversation history |
| GET | `/api/sessions/{id}/profile` | Get final profile |
| WS | `/ws/{id}` | WebSocket for real-time assessment |

## Data Model

### Sessions Table
- `id`: UUID (8 chars)
- `phase`: Current phase (0-6)
- `status`: active/completed
- `safety_cleared`: Boolean
- `final_profile`: JSON
- `confidence_scores`: JSON

### Messages Table
- `session_id`: FK
- `role`: user/assistant/system
- `content`: Text
- `phase`: Phase number
- `metadata`: JSON (context, tension targets)

### Hypotheses Table
- `session_id`: FK
- `field`: Field name
- `hypothesis_text`: Description
- `confidence`: 0.0-1.0
- `evidence`: JSON array
- `status`: active/rejected

### Matrix Scores Table
- `session_id`: FK
- `dimension`: 12D dimension
- `score`: 0-100
- `confidence`: 0-100
- `evidence`: JSON

## Agent Architecture

```
User Input
    ↓
[Analyzer] → Safety check / Pattern detection
    ↓
[HypothesisMaker] → Generate competing hypotheses
    ↓
[QuestionMaker] → Generate adaptive question
    ↓
User Response
    ↓
... (iterate Phase 2-3)
    ↓
[Assessor] → 12D Matrix scoring
    ↓
[Synthesizer] → Final profile
```

## Environment Variables

```bash
# Required
MOONSHOT_API_KEY=your-moonshot-api-key

# Optional
API_HOST=0.0.0.0
API_PORT=8000
DB_PATH=mbp_sessions.db
```

## Docker Deployment

```bash
docker-compose up -d
```

## Safety Considerations

- Phase 0: Hard stop for active suicidality, psychosis
- Phase 3: Focus on patterns, not trauma details
- Phase 6: Debriefing with grounding and resources
- All profiles include disclaimer: not clinical diagnosis

## License

MIT — For research and personal use only.
