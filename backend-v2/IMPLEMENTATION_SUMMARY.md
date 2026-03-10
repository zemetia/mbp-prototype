# MBP Backend v2.0 - Question-Based Flow Implementation Summary

## Summary of Changes

This implementation adds a **quiz-style question-based flow** to the MBP Backend, replacing the free-form chat approach with structured phases containing fixed and flexible questions.

## Files Created

### 1. `/questions.py` (20.5 KB)
Contains all question templates for every phase:
- **Phase 0 (Safety)**: 7 fixed questions
- **Phase 1 (Core)**: 11 fixed questions  
- **Phase 2 (Probing)**: 3 fixed + flexible templates
- **Phase 3 (Mining)**: 100% flexible categories
- **Phase 4 (Validation)**: 5 fixed + flexible templates
- **Phase 5 (Synthesis)**: 0 questions (internal analysis)
- **Phase 6 (Closure)**: 6 fixed + flexible templates

Includes `QuestionManager` class for managing questions.

### 2. `/test_question_flow.py` (9.9 KB)
Comprehensive test script that:
- Tests health endpoint
- Creates sessions with question flow
- Gets questions for current phase
- Submits answers
- Tracks progress
- Advances through phases
- Tests backward compatibility

### 3. `/QUESTION_FLOW.md` (7.2 KB)
Complete documentation including:
- Phase structure table
- API endpoint descriptions
- Client flow examples
- Error handling
- Session state details

## Files Modified

### 1. `/api/models.py`
**Added:**
- New phases: `SAFETY`, `CORE`, `PROBING`, `MINING`, `CROSS_VALIDATION`, `STRUCTURAL_SYNTHESIS`, `CLOSURE`
- `QuestionType` enum (FIXED/FLEXIBLE)
- `Question` model
- `Answer` model
- `QuestionsResponse` model
- `AnswerRequest`/`AnswerResponse` models
- `NextPhaseRequest`/`NextPhaseResponse` models
- `PhaseProgress` model
- `SessionQuestionsStateResponse` model
- Updated `CreateSessionResponse` with first_question

### 2. `/api/main.py`
**Added:**
- Question flow helper functions:
  - `get_session_question_state()`
  - `get_current_questions_for_phase()`
  - `check_phase_complete()`
  - `get_next_question()`
  - `advance_to_next_phase()`
  - `generate_flexible_questions()`
  - `process_phase_completion()`

- New endpoints:
  - `GET /api/sessions/{id}/questions` - Get current phase questions
  - `POST /api/sessions/{id}/answer` - Submit answer
  - `POST /api/sessions/{id}/next-phase` - Advance phase
  - `GET /api/sessions/{id}/question-state` - Get detailed state

**Modified:**
- `POST /api/sessions` - Now initializes question state
- `POST /api/sessions/with-personal-data` - Now initializes question state

### 3. `/graph/state.py`
**Added to MBPState:**
- `current_question_index: int`
- `current_question_id: Optional[str]`
- `answers: List[Answer]`
- `phase_complete: bool`
- `phase_question_count: int`
- `flexible_questions: List[QuestionState]`
- `phase_progress: Dict[str, Any]`

**Updated:**
- `Phase` enum with new phases
- `create_initial_state()` to initialize question fields

## New API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sessions/{id}/questions` | Get current phase questions |
| POST | `/api/sessions/{id}/answer` | Submit answer for current question |
| POST | `/api/sessions/{id}/next-phase` | Advance to next phase |
| GET | `/api/sessions/{id}/question-state` | Get detailed question progress |

## Backward Compatibility

✅ **Preserved endpoints:**
- `GET /api/health`
- `POST /api/personal-data`
- `GET /api/personal-data/{id}`
- `POST /api/sessions/with-personal-data`
- `POST /api/analyses`
- `GET /api/analyses`
- `GET /api/analyses/{id}`
- `POST /api/sessions/{id}/respond` (legacy)
- `GET /api/sessions/{id}` (legacy)

## Phase Question Counts

| Phase | Fixed | Flexible | Total |
|-------|-------|----------|-------|
| 0 - Safety | 7 | 0 | 7 |
| 1 - Core | 11 | 0-3 | 11-14 |
| 2 - Probing | 3 | 2-3 | 5-6 |
| 3 - Mining | 0 | 5-8 | 5-8 |
| 4 - Validation | 5 | 2-4 | 7-9 |
| 5 - Synthesis | 0 | 0 | 0 |
| 6 - Closure | 6 | 0-2 | 6-8 |

## Usage Flow

```
1. POST /api/sessions
   → Returns session_id + first_question

2. Display first_question to user

3. POST /api/sessions/{id}/answer
   → Submit answer, get next_question

4. Repeat until phase_complete=true

5. POST /api/sessions/{id}/next-phase
   → Advance to next phase

6. GET /api/sessions/{id}/questions
   → Get questions for new phase

7. Repeat steps 2-6 until closure
```

## Testing

Run the test script:
```bash
# Start server
./run.sh

# Run tests (in another terminal)
python test_question_flow.py

# Test specific features
python test_question_flow.py --personal-data
python test_question_flow.py --full
```

## Key Features

1. **Fixed Questions**: Template-based questions asked to all users
2. **Flexible Questions**: AI-generated based on user responses
3. **Progress Tracking**: Track answered/total per phase
4. **Phase Gating**: Must complete all questions before advancing
5. **AI Processing**: Automatic generation of flexible questions
6. **Backward Compatibility**: Existing endpoints still work

## Implementation Notes

- In-memory storage (replace with Redis/DB for production)
- Flexible question generation is template-based (replace with LLM for production)
- Session state tracks answers with timestamps
- Each answer is also recorded in messages for compatibility
- Phase 5 (Synthesis) has no questions - internal analysis only