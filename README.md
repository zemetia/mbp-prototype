# MirrorBreak Protocol (MBP) Prototype

FastAPI-based implementation of the MirrorBreak Protocol — a qualitative structural analysis framework for understanding human behavioral patterns.

## Quick Start

```bash
# 1. Start infrastructure
docker-compose up -d db redis

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
alembic upgrade head

# 4. Start server
uvicorn app.main:app --reload
```

## API Endpoints

- `POST /sessions` — Create new assessment session
- `POST /sessions/{id}/responses` — Submit user response
- `GET /sessions/{id}/next-question` — Get next probe question
- `GET /sessions/{id}/profile` — Get final structural profile
- `GET /health` — Health check

## Architecture

```
Client → API → Session Manager → Agent Pipeline → Database
                    ↓
            ┌───────┴───────┐
            ▼               ▼
      Analyzer      HypothesisMaker
            ↓               ↓
      HypothesisRefiner ←──┘
            ↓
      QuestionMaker (loop until confidence ≥ 0.7)
            ↓
      Assessor (12D Matrix)
            ↓
      Synthesizer (Final Profile)
```

## Environment Variables

```bash
DATABASE_URL=postgresql+asyncpg://mbp:mbp@localhost:5432/mbp
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

## Project Structure

```
app/
├── __init__.py
├── main.py              # FastAPI app entry
├── config.py            # Settings
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── agents/              # 6 MBP agents
├── services/            # Business logic
└── core/                # Utilities
```

## Status

Prototype phase — Foundation scaffolded. Agents implemented incrementally.
