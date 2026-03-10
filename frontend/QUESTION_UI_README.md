# MBP Frontend - Question-Based UI

This document describes the new question-based UI flow that replaces the chat-based interface.

## Overview

The MirrorBreak Protocol frontend now uses a **quiz-style question flow** instead of a chat interface. This provides:

- Focus on one question at a time
- No distractions
- Clean, minimal UI
- Calm, therapeutic aesthetic
- Clear progress tracking

## Architecture

### New Components

#### 1. PhaseView.tsx (Main Container)
- Replaces AnalysisFlow as the main analysis container
- Shows current phase name and description
- Displays overall progress
- Handles phase transitions
- Routes: `/analysis/:sessionId` and `/analysis/current`

#### 2. QuestionCard.tsx
- Displays a single question prominently
- Shows which 12D dimensions the question maps to (collapsible)
- Text area for answer input (min 4 rows)
- "Next" button (disabled if empty)
- Shows progress: "Question X of Y"

#### 3. PhaseTransition.tsx
- Shown between phases while AI processes answers
- Displays "AI Processing..." animation
- Progress bar
- Shows from/to phase names
- Text: "Generating next phase questions based on your answers..."

#### 4. ProgressBar.tsx
- Shows overall progress through all 7 phases
- Phase indicators: 0 (Safety) → 6 (Closure)
- Compact mode available for header display
- Visual connection between phases

### Updated Store (mbpStore.ts)

#### State Changes
```typescript
// Replaced chat-based with question-based:
currentPhase: string           // Current phase name
currentPhaseNumber: number     // 0-6
currentQuestion: Question | null  // Current active question
questions: Question[]          // All questions
answers: Answer[]              // User's answers
isProcessing: boolean          // Phase transition state
```

#### New Actions
```typescript
loadCurrentQuestion()          // GET /api/sessions/{id}/questions
submitAnswer(answer: string)   // POST /api/sessions/{id}/answer
nextQuestion()                 // Advance to next question
nextPhase()                    // POST /api/sessions/{id}/next-phase
getPhaseProgress()             // Get current/total for phase
getOverallProgress()           // Get total progress
```

### API Integration

The frontend expects these backend endpoints:

#### GET /api/sessions/{id}/questions
Returns the current question for the session:
```json
{
  "question": {
    "id": "q1.1",
    "text": "Question text here...",
    "phase": "core",
    "phaseNumber": 1,
    "dimensions": ["CFV", "CRF", "ASC"],
    "type": "fixed",
    "order": 1
  },
  "phase": "core",
  "phase_number": 1
}
```

Or indicates phase completion:
```json
{
  "phase_complete": true
}
```

#### POST /api/sessions/{id}/answer
Submit an answer:
```json
{
  "question_id": "q1.1",
  "answer": "User's answer text...",
  "timestamp": "2024-03-08T10:30:00Z"
}
```

Response:
```json
{
  "next_question": { ... },
  "phase_complete": false
}
```

#### POST /api/sessions/{id}/next-phase
Advance to next phase (triggers AI processing):
```json
{
  "next_phase": "adaptive",
  "phase_number": 2
}
```

Or indicates completion:
```json
{
  "analysis_complete": true
}
```

## Flow

1. **User enters analysis** → PhaseView loads
2. **Load current question** → GET /questions
3. **User answers** → Types in textarea, clicks "Next"
4. **Submit answer** → POST /answer
5. **Check response**:
   - If `next_question` → Show next question
   - If `phase_complete` → Show PhaseTransition, then POST /next-phase
   - If `analysis_complete` → Navigate to results
6. **Repeat until Phase 6 (Closure)**

## Types

### Question
```typescript
interface Question {
  id: string
  text: string
  phase: string
  phaseNumber: number
  dimensions: string[]     // 12D dimensions
  type: 'fixed' | 'flexible'
  order: number
}
```

### Answer
```typescript
interface Answer {
  questionId: string
  questionText: string
  answer: string
  phase: string
  timestamp: Date
  dimensions: string[]
}
```

## Phases

| Phase | Name | Questions | Description |
|-------|------|-----------|-------------|
| 0 | Safety | 7 | Safety & Context Screening |
| 1 | Core | 11 | Core Questioning |
| 2 | Adaptive | 5 | Adaptive Probing |
| 3 | Mining | 8 | Adaptation Pattern Mining |
| 4 | Validation | 6 | Cross-Validation |
| 5 | Synthesis | 0 | Structural Synthesis (AI processing only) |
| 6 | Closure | 6 | Debriefing & Closure |

## Design Principles

1. **One Question at a Time**: No scrolling through multiple questions
2. **Clean UI**: Minimal distractions, lots of whitespace
3. **Calm Aesthetic**: Soft colors, gentle animations
4. **Clear Progress**: Users always know where they are
5. **Dimension Visibility**: Users can see which 12D dimensions are being explored

## Backward Compatibility

- Old AnalysisFlow and ChatInterface components are kept as stubs
- Routes have been updated to use PhaseView
- Dashboard and PersonalDataForm remain unchanged
