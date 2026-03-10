# MBP v2.0 API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required (add JWT/API key for production).

## Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "agents_count": 22,
  "mode": "balanced"
}
```

### Create Session
```http
POST /sessions
Content-Type: application/json
```

**Request:**
```json
{
  "user_id": "optional_user_id",
  "metadata": {}
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "status": "created",
  "created_at": "2024-...",
  "next_question": "Halo! Saya akan membantu..."
}
```

### Send User Response
```http
POST /sessions/{session_id}/respond
Content-Type: application/json
```

**Request:**
```json
{
  "message": "Saya cenderung perfeksionis...",
  "client_timestamp": "optional"
}
```

**Response (In Progress):**
```json
{
  "session_id": "uuid",
  "phase": "probe",
  "next_question": "Tell me more about...",
  "final_profile": null,
  "iteration_count": 2,
  "processing_time_ms": 45000
}
```

**Response (Complete):**
```json
{
  "session_id": "uuid",
  "phase": "complete",
  "next_question": null,
  "final_profile": { /* full profile */ },
  "iteration_count": 5,
  "processing_time_ms": 120000
}
```

### Get Session State
```http
GET /sessions/{session_id}
```

**Response:**
```json
{
  "session_id": "uuid",
  "phase": "hypothesis",
  "iteration_count": 3,
  "safety_cleared": true,
  "overall_confidence": 0.65,
  "extracted_signals_summary": {
    "linguistic": 5,
    "emotional": 3,
    "cognitive": 4,
    "behavioral": 2
  },
  "hypotheses_count": 18,
  "low_confidence_fields": ["defense", "emotional"],
  "created_at": "2024-...",
  "updated_at": "2024-..."
}
```

### Get Profile
```http
GET /sessions/{session_id}/profile
```

**Response:**
```json
{
  "session_id": "uuid",
  "status": "complete",
  "final_profile": {
    "core_structure": {
      "core_fear": { "primary": {...}, "secondary": {...} },
      "core_drive": { "primary": {...}, "secondary": {...} },
      "defense_mechanism": {...}
    },
    "persona_core_gap": {...},
    "adaptation_patterns": [...]
  },
  "matrix_12d": {
    "AB": { "score": 75, "confidence": 80 },
    "CDI": { "score": 60, "confidence": 70 },
    ...
  },
  "executive_summary": "Paragraph in Indonesian...",
  "core_insights": ["insight1", "insight2"],
  "tensions": [...],
  "generated_at": "2024-..."
}
```

## Error Responses

### 404 - Session Not Found
```json
{
  "detail": "Session not found"
}
```

### 400 - Profile Not Ready
```json
{
  "detail": "Profile not yet generated"
}
```

### 500 - Processing Error
```json
{
  "detail": "Processing error: ..."
}
```

## WebSocket (Future)
Real-time updates via WebSocket coming in v2.1.
