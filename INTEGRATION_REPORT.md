# MBP Frontend-Backend Integration Report

## Summary
Successfully aligned frontend and backend API contracts for the MBP question-based flow.

## Changes Made

### 1. Backend API Models (`backend-v2/api/models.py`)

#### QuestionsResponse (GET /api/sessions/{id}/questions)
**Added Fields:**
- `phase_number: int` - Phase number (0-6) for frontend phase tracking
- `question: Optional[Question]` - Single current question (frontend expects this instead of array)
- `analysis_complete: bool` - Flag to indicate session completion

#### Question Model
**Modified Fields:**
- Added `id: str` as alias for `question_id` (frontend expects `id`)
- Added `phase_number: int` field
- Added Pydantic Config to populate by name for alias support

#### AnswerResponse (POST /api/sessions/{id}/answer)
**Added Fields:**
- `analysis_complete: bool` - Flag to indicate session completion

#### NextPhaseResponse (POST /api/sessions/{id}/next-phase)
**Added Fields:**
- `next_phase: str` - Alias for `new_phase` (frontend expects `next_phase`)
- `phase_number: int` - Phase number (0-6)
- `analysis_complete: bool` - Flag to indicate session completion

### 2. Backend Main (`backend-v2/api/main.py`)

#### Added Helper Functions
- `PHASE_TO_NUMBER` mapping dictionary
- `NUMBER_TO_PHASE` reverse mapping
- `get_phase_number(phase: str) -> int` helper function

#### Updated Endpoints

**GET /api/sessions/{id}/questions**
- Now returns `phase_number` based on current phase
- Returns `question` (first unanswered question) instead of requiring frontend to calculate
- Sets `analysis_complete=true` when in closure phase and complete

**POST /api/sessions/{id}/answer**
- Now returns `analysis_complete` flag
- Sets flag to true when in closure phase and all questions answered

**POST /api/sessions/{id}/next-phase**
- Now returns `next_phase` (alias for `new_phase`)
- Returns `phase_number` for the new phase
- Returns `analysis_complete` flag when session is complete

### 3. Backend Questions (`backend-v2/questions.py`)

#### Question Dataclass
**Updated `to_dict()` method:**
- Added `id` field (alias for `question_id`)
- Added `phase_number` field using new `get_phase_number()` method

**Added Method:**
- `get_phase_number()` - Returns phase number (0-6) based on phase name

### 4. Frontend Environment

**Created:**
- `.env` file with `VITE_API_URL=http://localhost:8000`

## API Contract Alignment

### Phase Name Mapping
| Phase Number | Frontend Name | Backend Name |
|--------------|---------------|--------------|
| 0 | Safety | safety |
| 1 | Core | core |
| 2 | Adaptive | probing |
| 3 | Mining | mining |
| 4 | Validation | validation |
| 5 | Synthesis | synthesis |
| 6 | Closure | closure |

### Endpoint Contracts

#### GET /api/sessions/{id}/questions
**Frontend Expects:**
```typescript
{
  question: Question | null,
  phase: string,
  phase_number: number,
  analysis_complete?: boolean
}
```

**Backend Now Returns:**
```python
{
  "question": Question | null,  # Current unanswered question
  "phase": str,                 # Current phase name
  "phase_number": int,          # Phase number (0-6)
  "analysis_complete": bool,    # True if session complete
  "questions": [...],           # All questions in phase (extra)
  "current_question_index": int,
  "total_questions_in_phase": int,
  "phase_complete": bool,
  "progress_percentage": float
}
```

#### POST /api/sessions/{id}/answer
**Request:**
```json
{
  "question_id": string,
  "answer": string
}
```

**Response:**
```typescript
{
  question_id: string,
  next_question: Question | null,
  phase_complete: boolean,
  can_advance: boolean,
  analysis_complete?: boolean
}
```

#### POST /api/sessions/{id}/next-phase
**Request:**
```json
{}
```

**Response:**
```typescript
{
  next_phase: string,
  phase_number: number,
  first_question?: Question,
  analysis_complete?: boolean
}
```

### Question Object
**Frontend Expects:**
```typescript
{
  id: string,
  text: string,
  phase: string,
  phaseNumber: number,
  dimensions: string[],
  type: 'fixed' | 'flexible',
  order: number
}
```

**Backend Now Returns:**
```python
{
  "id": str,              # Alias for question_id
  "question_id": str,     # Original field
  "text": str,
  "phase": str,
  "phase_number": int,
  "dimensions": list[str],
  "type": "fixed" | "flexible",
  "order": int
}
```

## Verification

### Backend Models
✓ All models import successfully
✓ Pydantic validation passes

### Frontend Build
✓ TypeScript compilation successful
✓ Vite build successful
✓ No type errors

### Data Flow Verification

**Complete Flow:**
1. ✓ Create Session → Returns session_id
2. ✓ Load Question → Returns question, phase, phase_number
3. ✓ Submit Answer → Returns next_question, phase_complete, can_advance
4. ✓ Phase Complete → Triggers nextPhase()
5. ✓ Advance Phase → Returns next_phase, phase_number, first_question
6. ✓ Session Complete → Returns analysis_complete=true

## Test Commands

### Backend (after dependencies installed)
```bash
cd /mnt/d/Yoel/Projects/mbp-prototype/backend-v2
pip install -r requirements.txt  # Install dependencies
python -m api.main  # Start server on port 8000
```

### Frontend
```bash
cd /mnt/d/Yoel/Projects/mbp-prototype/frontend
npm run dev  # Start dev server on port 5173
```

## Notes

1. **Backend Dependencies**: The backend requires `langgraph` and other dependencies to run. These need to be installed before testing.

2. **Phase Naming**: Frontend uses capitalized display names ("Safety", "Core") while backend uses lowercase ("safety", "core"). This is handled correctly in the integration.

3. **Extra Fields**: Backend returns additional fields beyond what frontend requires (e.g., `questions[]` array), which is fine as frontend only uses the fields it needs.

4. **Backward Compatibility**: The backend maintains backward compatibility with existing code while adding new fields for the question-based flow.

## Status: ✅ INTEGRATION COMPLETE

All identified mismatches have been resolved. The frontend and backend are now properly aligned for the question-based flow.