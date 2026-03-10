# MBP v2.0 - Question-Based Flow Implementation

## Overview

The backend has been modified to support a **quiz-style, question-based flow** instead of a free-form chat interface. Each phase of the MirrorBreak Protocol now has specific fixed and flexible questions.

## Phase Structure

| Phase | Name | Fixed | Flexible | Description |
|-------|------|-------|----------|-------------|
| 0 | Safety & Context Screening | 100% | 0% | Readiness check, consent, context gathering |
| 1 | Core Questioning | 70% | 30% | Baseline & hypothesis generation |
| 2 | Adaptive Probing | 20% | 80% | Hypothesis pursuit |
| 3 | Adaptation Pattern Mining | 0% | 100% | AI-generated deep probes |
| 4 | Cross-Validation | 50% | 50% | Contradiction exposure |
| 5 | Structural Synthesis | 0% | 0% | Internal analysis (no questions) |
| 6 | Debriefing & Closure | 60% | 40% | Safe landing & resources |

## API Changes

### New Endpoints

#### 1. Get Current Phase Questions
```http
GET /api/sessions/{session_id}/questions
```

**Response:**
```json
{
  "session_id": "uuid",
  "phase": "safety",
  "questions": [
    {
      "question_id": "q0.1",
      "phase": "safety",
      "type": "fixed",
      "text": "Sebelum kita mulai...",
      "dimensions": ["Safety"],
      "order": 1
    }
  ],
  "current_question_index": 0,
  "total_questions_in_phase": 7,
  "phase_complete": false,
  "progress_percentage": 0.0
}
```

#### 2. Submit Answer
```http
POST /api/sessions/{session_id}/answer
Content-Type: application/json

{
  "question_id": "q0.1",
  "answer": "Saya merasa cukup stabil saat ini..."
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "phase": "safety",
  "question_id": "q0.1",
  "next_question": {
    "question_id": "q0.2",
    "text": "Kalau nanti dalam percakapan...",
    ...
  },
  "phase_complete": false,
  "can_advance": false,
  "message": "Answer recorded."
}
```

#### 3. Advance to Next Phase
```http
POST /api/sessions/{session_id}/next-phase
Content-Type: application/json

{
  "confirm": true
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "previous_phase": "safety",
  "new_phase": "core",
  "first_question": {
    "question_id": "q1.1",
    "text": "Kalau disuruh deskripsikan dirimu...",
    ...
  },
  "ai_processing_complete": true,
  "message": "Advanced from safety to core."
}
```

#### 4. Get Question State
```http
GET /api/sessions/{session_id}/question-state
```

**Response:**
```json
{
  "session_id": "uuid",
  "current_phase": "core",
  "current_question_index": 3,
  "phase_complete": false,
  "answers_count": 10,
  "phase_progress": [
    {
      "phase": "safety",
      "fixed_questions_total": 7,
      "fixed_questions_answered": 7,
      "flexible_questions_total": 0,
      "flexible_questions_answered": 0,
      "phase_complete": true
    }
  ],
  "can_advance": false
}
```

### Modified Endpoints

#### Create Session
Now includes question state initialization and first question:

```http
POST /api/sessions
```

**Response:**
```json
{
  "session_id": "uuid",
  "status": "created",
  "created_at": "2026-03-08T10:30:00",
  "current_phase": "safety",
  "first_question": {
    "question_id": "q0.1",
    ...
  },
  "message": "Session created. Phase 0: Safety & Context Screening begins."
}
```

## Client Flow

### 1. Create Session
```javascript
const resp = await fetch('/api/sessions', {
  method: 'POST',
  body: JSON.stringify({ metadata: {} })
});
const data = await resp.json();
const sessionId = data.session_id;
const firstQuestion = data.first_question;
```

### 2. Display Current Question
Show `first_question.text` to the user.

### 3. Submit Answer
```javascript
await fetch(`/api/sessions/${sessionId}/answer`, {
  method: 'POST',
  body: JSON.stringify({
    question_id: currentQuestion.question_id,
    answer: userAnswer
  })
});
```

### 4. Check for Next Question
If `next_question` is returned, display it. If `phase_complete` is true:

### 5. Advance Phase
```javascript
await fetch(`/api/sessions/${sessionId}/next-phase`, {
  method: 'POST',
  body: JSON.stringify({ confirm: true })
});
```

Then get new phase questions:
```javascript
const resp = await fetch(`/api/sessions/${sessionId}/questions`);
const data = await resp.json();
// Display data.questions[0]
```

## Backward Compatibility

The following endpoints remain unchanged:

- `GET /api/health`
- `POST /api/personal-data`
- `GET /api/personal-data/{id}`
- `POST /api/sessions/with-personal-data`
- `POST /api/analyses`
- `GET /api/analyses`
- `GET /api/analyses/{id}`

Legacy endpoints still work but use new flow internally:
- `POST /api/sessions/{id}/respond` - Now maps to question-based flow
- `GET /api/sessions/{id}` - Returns extended state

## File Changes

### New Files
- `questions.py` - All question templates and QuestionManager class
- `test_question_flow.py` - Test script for the question-based flow

### Modified Files
- `api/models.py` - Added question-based flow models
- `api/main.py` - Added new endpoints and question flow logic
- `graph/state.py` - Added question tracking fields to MBPState

## Testing

Run the test script:
```bash
cd /mnt/d/Yoel/Projects/mbp-prototype/backend-v2
./run.sh  # In one terminal
python test_question_flow.py  # In another terminal
```

Test specific features:
```bash
# Test personal data endpoints (backward compatibility)
python test_question_flow.py --personal-data

# Full flow test through all phases
python test_question_flow.py --full
```

## Question Templates

All questions are defined in `questions.py`:

- `PHASE_0_QUESTIONS` - 7 fixed safety questions
- `PHASE_1_QUESTIONS` - 11 fixed core questions
- `PHASE_2_QUESTIONS` - 3 fixed + flexible probing templates
- `PHASE_3_FLEXIBLE_CATEGORIES` - AI-generated mining questions
- `PHASE_4_QUESTIONS` - 5 fixed + flexible validation templates
- `PHASE_6_QUESTIONS` - 6 fixed + flexible closure templates

## Flexible Question Generation

For phases with flexible questions (2, 3, 4, 6), the system:

1. Collects all fixed question answers
2. Sends them to AI for analysis
3. Generates context-specific follow-up questions
4. Stores them in `flexible_questions` session state
5. Presents them after fixed questions

## Session State

The session now tracks:

```python
{
  "question_state": {
    "current_phase": "safety",
    "current_question_index": 0,
    "answers": [
      {
        "question_id": "q0.1",
        "phase": "safety",
        "answer": "...",
        "timestamp": "..."
      }
    ],
    "phase_complete": false,
    "phase_progress": {},
    "flexible_questions": {},
    "ai_processing_complete": false
  }
}
```

## Error Handling

Common errors:

- `404 Session not found` - Invalid session ID
- `400 Question X not found in current phase Y` - Wrong question ID for phase
- `400 Current phase X is not complete` - Tried to advance before answering all questions

## Future Enhancements

1. **Real AI Integration**: Replace `generate_flexible_questions()` with actual LLM calls
2. **Persistence**: Store sessions in Redis/PostgreSQL
3. **Resume**: Allow users to resume interrupted sessions
4. **Analytics**: Track completion rates per question
5. **Dynamic Skip**: Skip questions based on previous answers