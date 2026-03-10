"""
MBP v2.0 - FastAPI Application
"""
import os
import sys
import time
import uuid
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.models import (
    CreateSessionRequest, CreateSessionResponse,
    UserResponseRequest, UserResponseResponse,
    SessionStateResponse, ProfileResponse, HealthResponse,
    Phase,
    PersonalDataRequest, PersonalDataResponse, PersonalData,
    CreateSessionWithPersonalDataRequest, CreateSessionWithPersonalDataResponse,
    AnalysisRequest, AnalysisResponse, AnalysesListResponse, AnalysisDetail,
    # Question-based flow models
    Question, Answer, QuestionsResponse, AnswerRequest, AnswerResponse,
    NextPhaseRequest, NextPhaseResponse, PhaseProgress, SessionQuestionsStateResponse,
    QuestionType
)
from questions import QuestionManager, get_all_questions, PHASE_0_QUESTIONS
from graph.graph import run_mbp_v2
from core.config import MBPConfig

# Import database module
try:
    from db import (
        init_database,
        create_client, get_client, update_client_phase, list_clients,
        create_session, get_session, update_session_phase, complete_session,
        save_answer, get_session_answers, get_phase_answers,
        get_client_progress, can_resume_analysis
    )
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print("⚠️  Database module not available, using in-memory storage")

# Load env
load_dotenv()

# Initialize database on startup
if DB_AVAILABLE:
    init_database()

# In-memory stores (fallback if DB not available)
sessions = {}
personal_data_store = {}
analyses_store = {}


# ============ QUESTION-BASED FLOW HELPERS ============

# Phase name to number mapping
PHASE_TO_NUMBER = {
    "safety": 0,
    "core": 1,
    "probing": 2,
    "mining": 3,
    "validation": 4,
    "synthesis": 5,
    "closure": 6,
}

# Reverse mapping
NUMBER_TO_PHASE = {v: k for k, v in PHASE_TO_NUMBER.items()}


def get_phase_number(phase: str) -> int:
    """Get phase number from phase name"""
    return PHASE_TO_NUMBER.get(phase, 0)


def get_session_question_state(session_id: str) -> Dict[str, Any]:
    """Get question state for a session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    if "question_state" not in session:
        # Initialize question state
        session["question_state"] = {
            "current_phase": "safety",
            "current_question_index": 0,
            "answers": [],
            "phase_complete": False,
            "phase_progress": {},
            "flexible_questions": {},  # phase -> list of flexible questions
            "ai_processing_complete": False,
        }
    return session["question_state"]


def get_current_questions_for_phase(phase: str, session: Dict) -> List[Question]:
    """Get questions for the current phase, including any flexible questions"""
    # Get fixed questions
    fixed = QuestionManager.get_phase_questions(phase)
    questions = [Question(**q.to_dict()) for q in fixed]
    
    # Get flexible questions if generated
    q_state = session.get("question_state", {})
    flexible = q_state.get("flexible_questions", {}).get(phase, [])
    
    # Add flexible questions
    for fq in flexible:
        qid = fq["question_id"]
        questions.append(Question(
            question_id=qid,
            id=qid,  # Alias field for frontend compatibility
            phase=phase,
            phase_number=get_phase_number(phase),
            type=QuestionType.FLEXIBLE,
            text=fq["text"],
            dimensions=fq.get("dimensions", []),
            order=fq.get("order", len(questions) + 1)
        ))
    
    return questions


def check_phase_complete(session: Dict) -> bool:
    """Check if current phase is complete (all questions answered)"""
    q_state = get_session_question_state(session["session_id"])
    phase = q_state["current_phase"]
    
    # Get all questions for this phase
    questions = get_current_questions_for_phase(phase, session)
    
    if not questions:
        # No questions in this phase (e.g., synthesis)
        return True
    
    # Get answered question IDs
    answered_ids = {a["question_id"] for a in q_state["answers"] if a.get("phase") == phase}
    
    # Check if all questions are answered
    all_answered = all(q.question_id in answered_ids for q in questions)
    
    return all_answered


def get_next_question(session: Dict) -> Optional[Question]:
    """Get the next question for the current phase"""
    q_state = get_session_question_state(session["session_id"])
    phase = q_state["current_phase"]
    
    questions = get_current_questions_for_phase(phase, session)
    
    # Get answered question IDs for this phase
    answered_ids = {a["question_id"] for a in q_state["answers"] if a.get("phase") == phase}
    
    # Find first unanswered question
    for q in questions:
        if q.question_id not in answered_ids:
            return q
    
    return None


def advance_to_next_phase(session_id: str) -> str:
    """Advance session to next phase, return new phase"""
    q_state = get_session_question_state(session_id)
    current_phase = q_state["current_phase"]
    
    next_phase = QuestionManager.get_next_phase(current_phase)
    
    if next_phase:
        q_state["current_phase"] = next_phase
        q_state["current_question_index"] = 0
        q_state["phase_complete"] = False
        q_state["ai_processing_complete"] = False
        
        # Mark previous phase as complete in progress
        if current_phase not in q_state["phase_progress"]:
            q_state["phase_progress"][current_phase] = {}
        q_state["phase_progress"][current_phase]["completed"] = True
    
    sessions[session_id]["updated_at"] = datetime.now().isoformat()
    return next_phase or current_phase


def generate_flexible_questions(phase: str, session: Dict) -> List[Dict]:
    """Generate flexible questions for a phase based on previous answers"""
    # This is a simplified version - in production, this would use LLM
    from questions import (
        PHASE_2_FLEXIBLE_TEMPLATES, PHASE_3_FLEXIBLE_CATEGORIES,
        PHASE_4_FLEXIBLE_TEMPLATES, PHASE_6_FLEXIBLE_TEMPLATES
    )
    
    templates = {}
    if phase == "probing":
        templates = PHASE_2_FLEXIBLE_TEMPLATES
    elif phase == "mining":
        templates = PHASE_3_FLEXIBLE_CATEGORIES
    elif phase == "validation":
        templates = PHASE_4_FLEXIBLE_TEMPLATES
    elif phase == "closure":
        templates = PHASE_6_FLEXIBLE_TEMPLATES
    
    flexible_questions = []
    q_state = session.get("question_state", {})
    
    # Get previous answers for context
    previous_answers = q_state.get("answers", [])
    
    # Generate 2-3 flexible questions per phase (simplified)
    for i, (key, template) in enumerate(list(templates.items())[:3]):
        # Simple template filling (in production, use LLM)
        text = template
        if "[PATTERN]" in text:
            text = text.replace("[PATTERN]", "perfeksionis")
        if "[RELATIONSHIP]" in text:
            text = text.replace("[RELATIONSHIP]", "keluarga")
        if "[EMOTION]" in text:
            text = text.replace("[EMOTION]", "marah")
        
        flexible_questions.append({
            "question_id": f"{phase}_flex_{i+1}",
            "text": text,
            "dimensions": [key],
            "order": 100 + i
        })
    
    return flexible_questions


def process_phase_completion(session_id: str) -> Dict[str, Any]:
    """Process phase completion and generate next questions"""
    q_state = get_session_question_state(session_id)
    phase = q_state["current_phase"]
    
    result = {
        "ai_processing_complete": True,
        "generated_flexible_questions": 0,
        "next_phase_ready": False
    }
    
    # Generate flexible questions for phases that need them
    if phase in ["probing", "mining", "validation", "closure"]:
        flexible = generate_flexible_questions(phase, sessions[session_id])
        if flexible:
            if phase not in q_state["flexible_questions"]:
                q_state["flexible_questions"][phase] = []
            q_state["flexible_questions"][phase].extend(flexible)
            result["generated_flexible_questions"] = len(flexible)
    
    # Check if we can advance (all questions answered including flexible)
    questions = get_current_questions_for_phase(phase, sessions[session_id])
    answered_ids = {a["question_id"] for a in q_state["answers"] if a.get("phase") == phase}
    
    if all(q.question_id in answered_ids for q in questions):
        q_state["phase_complete"] = True
        result["next_phase_ready"] = True
    
    q_state["ai_processing_complete"] = True
    return result


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print("🚀 MBP v2.0 API Starting...")
    yield
    print("🛑 MBP v2.0 API Shutting down...")


# Create main app
app = FastAPI(
    title="MirrorBreak Protocol v2.0 API",
    description="AI-powered psychological structural analysis",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create API router with /api prefix
api_router = APIRouter()


@api_router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        agents_count=22,
        mode=MBPConfig.MODE.value
    )


@api_router.post("/sessions", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """Create new MBP session with question-based flow"""
    session_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    sessions[session_id] = {
        "session_id": session_id,
        "user_id": request.user_id,
        "status": "active",
        "created_at": now,
        "updated_at": now,
        "messages": [],
        "metadata": request.metadata,
        "question_state": {
            "current_phase": "safety",
            "current_question_index": 0,
            "answers": [],
            "phase_complete": False,
            "phase_progress": {},
            "flexible_questions": {},
            "ai_processing_complete": False,
        }
    }
    
    # Get first question from Phase 0
    first_q = PHASE_0_QUESTIONS[0] if PHASE_0_QUESTIONS else None
    first_question = None
    if first_q:
        first_question = Question(**first_q.to_dict())
    
    return CreateSessionResponse(
        session_id=session_id,
        status="created",
        created_at=now,
        current_phase="safety",
        first_question=first_question,
        message="Session created. Phase 0: Safety & Context Screening begins."
    )


@api_router.post("/sessions/{session_id}/respond", response_model=UserResponseResponse)
async def respond(session_id: str, request: UserResponseRequest):
    """Send user response and get next question or profile"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    start_time = time.time()
    
    # Add user message
    session["messages"].append({
        "role": "user",
        "content": request.message,
        "timestamp": request.client_timestamp or datetime.now().isoformat()
    })
    
    try:
        # Run MBP v2.0
        result = await run_mbp_v2(
            session_id=session_id,
            user_response=request.message,
            messages=session["messages"]
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        # Update session
        session["updated_at"] = datetime.now().isoformat()
        session["last_result"] = result
        
        # Add AI response if there's a next question
        if result.get("next_question"):
            session["messages"].append({
                "role": "assistant",
                "content": result["next_question"],
                "timestamp": datetime.now().isoformat()
            })
        
        # Handle phase - convert graph.state.Phase to api.models.Phase
        current_phase = result.get("current_phase", "intake")
        if hasattr(current_phase, 'value'):
            # It's an enum (from graph.state), convert via string value
            phase_value = Phase(current_phase.value)
        else:
            # It's already a string
            phase_value = Phase(current_phase)
        
        return UserResponseResponse(
            session_id=session_id,
            phase=phase_value,
            next_question=result.get("next_question"),
            final_profile=result.get("final_profile"),
            iteration_count=result.get("iteration_count", 0),
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@api_router.get("/sessions/{session_id}", response_model=SessionStateResponse)
async def get_session(session_id: str):
    """Get current session state"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    result = session.get("last_result", {})
    
    # Extract signals summary
    signals = result.get("extracted_signals", {})
    signals_summary = {k: len(v.get("patterns", [])) for k, v in signals.items()}
    
    # Count hypotheses
    hyps = result.get("hypotheses", {})
    hyps_count = sum(len(h) for h in hyps.values())
    
    # Handle phase - convert graph.state.Phase to api.models.Phase
    current_phase = result.get("current_phase", "intake")
    if hasattr(current_phase, 'value'):
        # It's an enum (from graph.state), convert via string value
        phase_value = Phase(current_phase.value)
    else:
        # It's already a string
        phase_value = Phase(current_phase)
    
    return SessionStateResponse(
        session_id=session_id,
        phase=phase_value,
        iteration_count=result.get("iteration_count", 0),
        safety_cleared=result.get("safety_cleared", False),
        overall_confidence=result.get("overall_confidence", 0.0),
        extracted_signals_summary=signals_summary,
        hypotheses_count=hyps_count,
        low_confidence_fields=[f["field"] for f in result.get("low_confidence_fields", [])],
        created_at=session["created_at"],
        updated_at=session["updated_at"]
    )


@api_router.get("/sessions/{session_id}/profile", response_model=ProfileResponse)
async def get_profile(session_id: str):
    """Get final profile for completed session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    result = session.get("last_result", {})
    
    if not result.get("final_profile"):
        raise HTTPException(status_code=400, detail="Profile not yet generated")
    
    return ProfileResponse(
        session_id=session_id,
        status="complete",
        final_profile=result.get("final_profile"),
        matrix_12d=result.get("matrix_12d"),
        executive_summary=result.get("executive_summary"),
        core_insights=result.get("core_insights", []),
        tensions=result.get("tensions", []),
        generated_at=session["updated_at"]
    )


# ============ QUESTION-BASED FLOW ENDPOINTS ============

@api_router.get("/sessions/{session_id}/questions", response_model=QuestionsResponse)
async def get_questions(session_id: str):
    """Get current questions for the session's current phase"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    q_state = get_session_question_state(session_id)
    phase = q_state["current_phase"]
    phase_number = get_phase_number(phase)
    
    # Get questions for current phase
    questions = get_current_questions_for_phase(phase, session)
    
    # Calculate progress
    answered_count = len([a for a in q_state["answers"] if a.get("phase") == phase])
    total = len(questions)
    progress = (answered_count / total * 100) if total > 0 else 100
    
    # Check if phase is complete
    phase_complete = check_phase_complete(session)
    
    # Get current question (first unanswered)
    answered_ids = {a["question_id"] for a in q_state["answers"] if a.get("phase") == phase}
    current_question = None
    for q in questions:
        if q.question_id not in answered_ids:
            current_question = q
            break
    
    # Check if analysis is complete (closure phase is complete)
    analysis_complete = phase == "closure" and phase_complete
    
    return QuestionsResponse(
        session_id=session_id,
        phase=phase,
        phase_number=phase_number,
        question=current_question,
        questions=questions,
        current_question_index=q_state["current_question_index"],
        total_questions_in_phase=total,
        phase_complete=phase_complete,
        progress_percentage=round(progress, 1),
        analysis_complete=analysis_complete
    )


@api_router.post("/sessions/{session_id}/answer", response_model=AnswerResponse)
async def submit_answer(session_id: str, request: AnswerRequest):
    """Submit an answer for the current question"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    q_state = get_session_question_state(session_id)
    phase = q_state["current_phase"]
    
    # Verify the question exists in current phase
    questions = get_current_questions_for_phase(phase, session)
    question = next((q for q in questions if q.question_id == request.question_id), None)
    
    if not question:
        raise HTTPException(
            status_code=400, 
            detail=f"Question {request.question_id} not found in current phase {phase}"
        )
    
    # Record the answer
    now = datetime.now().isoformat()
    answer_record = {
        "question_id": request.question_id,
        "phase": phase,
        "answer": request.answer,
        "timestamp": now
    }
    q_state["answers"].append(answer_record)
    
    # Also add to messages for backward compatibility
    session["messages"].append({
        "role": "user",
        "content": f"Q: {question.text}\nA: {request.answer}",
        "timestamp": now
    })
    
    # Save to database if available
    if DB_AVAILABLE:
        try:
            client_id = session.get("_client_id")
            db_session_id = session.get("_db_session_id")
            
            if client_id and db_session_id:
                save_answer(
                    client_id=client_id,
                    session_id=db_session_id,
                    question_id=request.question_id,
                    question_text=question.text,
                    answer=request.answer,
                    phase=phase,
                    dimensions=question.dimensions,
                    question_type=question.type.value,
                    order_index=question.order
                )
        except Exception as e:
            print(f"⚠️  Failed to save answer to database: {e}")
    
    # Update question index
    q_state["current_question_index"] += 1
    session["updated_at"] = now
    
    # Check if phase is complete
    phase_complete = check_phase_complete(session)
    q_state["phase_complete"] = phase_complete
    
    # Get next question
    next_q = get_next_question(session)
    
    # If no more questions in phase, trigger AI processing
    ai_processing = False
    if not next_q and not q_state.get("ai_processing_complete", False):
        # Generate flexible questions if needed
        result = process_phase_completion(session_id)
        ai_processing = result["ai_processing_complete"]
        # Refresh next question after processing
        next_q = get_next_question(session)
    
    # Check if can advance to next phase
    can_advance = q_state["phase_complete"] and q_state.get("ai_processing_complete", False)
    
    # Check if analysis is complete (closure phase is complete)
    analysis_complete = phase == "closure" and phase_complete
    
    message = "Answer recorded."
    if analysis_complete:
        message = "Session complete. Analysis finished."
    elif phase_complete:
        message = "All questions in this phase answered. AI is processing..."
    elif next_q:
        message = f"Proceed to question: {next_q.question_id}"
    
    return AnswerResponse(
        session_id=session_id,
        phase=phase,
        question_id=request.question_id,
        next_question=next_q,
        phase_complete=phase_complete,
        can_advance=can_advance,
        analysis_complete=analysis_complete,
        message=message
    )


@api_router.post("/sessions/{session_id}/next-phase", response_model=NextPhaseResponse)
async def advance_phase(session_id: str, request: NextPhaseRequest):
    """Advance to the next phase (after completing current phase)"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    q_state = get_session_question_state(session_id)
    current_phase = q_state["current_phase"]
    
    # Verify phase is complete
    if not q_state.get("phase_complete", False):
        raise HTTPException(
            status_code=400,
            detail=f"Current phase {current_phase} is not complete. Answer all questions first."
        )
    
    if not q_state.get("ai_processing_complete", False):
        # Process completion first
        process_phase_completion(session_id)
    
    # Advance to next phase
    previous_phase = current_phase
    new_phase = advance_to_next_phase(session_id)
    new_phase_number = get_phase_number(new_phase)
    
    # Update database if available
    if DB_AVAILABLE:
        try:
            db_session_id = session.get("_db_session_id")
            if db_session_id:
                update_session_phase(
                    session_id=db_session_id,
                    phase=new_phase,
                    phase_number=new_phase_number,
                    phase_complete=False  # Reset for new phase
                )
        except Exception as e:
            print(f"⚠️  Failed to update session phase in database: {e}")
    
    # Get first question of new phase
    first_question = None
    questions = get_current_questions_for_phase(new_phase, session)
    if questions:
        first_question = questions[0]
    
    # Check if analysis is complete (closure phase is complete)
    analysis_complete = new_phase == "closure" and q_state.get("phase_complete", False)
    
    message = f"Advanced from {previous_phase} to {new_phase}."
    if new_phase == "closure":
        message = "Final phase reached. Preparing for session closure."
    elif new_phase == previous_phase:
        message = "No next phase available. Session may be complete."
        analysis_complete = True  # Session complete
    
    return NextPhaseResponse(
        session_id=session_id,
        previous_phase=previous_phase,
        new_phase=new_phase,
        next_phase=new_phase,  # Alias for frontend compatibility
        phase_number=new_phase_number,
        first_question=first_question,
        ai_processing_complete=True,
        analysis_complete=analysis_complete,
        message=message
    )


@api_router.get("/sessions/{session_id}/question-state", response_model=SessionQuestionsStateResponse)
async def get_question_state(session_id: str):
    """Get detailed question state for a session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    q_state = get_session_question_state(session_id)
    
    # Build phase progress list
    phase_progress_list = []
    for phase_name in QuestionManager.PHASE_ORDER:
        questions = get_current_questions_for_phase(phase_name, session)
        fixed_count = len([q for q in questions if q.type == QuestionType.FIXED])
        flexible_count = len([q for q in questions if q.type == QuestionType.FLEXIBLE])
        
        answered = [a for a in q_state["answers"] if a.get("phase") == phase_name]
        fixed_answered = len([a for a in answered if not a.get("question_id", "").endswith("_flex")])
        flexible_answered = len([a for a in answered if a.get("question_id", "").endswith("_flex")])
        
        phase_complete = q_state.get("phase_progress", {}).get(phase_name, {}).get("completed", False)
        
        phase_progress_list.append(PhaseProgress(
            phase=phase_name,
            fixed_questions_total=fixed_count,
            fixed_questions_answered=fixed_answered,
            flexible_questions_total=flexible_count,
            flexible_questions_answered=flexible_answered,
            phase_complete=phase_complete
        ))
    
    can_advance = q_state.get("phase_complete", False) and q_state.get("ai_processing_complete", False)
    
    return SessionQuestionsStateResponse(
        session_id=session_id,
        current_phase=q_state["current_phase"],
        current_question_index=q_state["current_question_index"],
        phase_complete=q_state.get("phase_complete", False),
        answers_count=len(q_state["answers"]),
        phase_progress=phase_progress_list,
        can_advance=can_advance
    )


# ============ PERSONAL DATA ENDPOINTS ============

@api_router.post("/personal-data", response_model=PersonalDataResponse)
async def create_personal_data(request: PersonalDataRequest):
    """Create new personal data record - also creates a client in the database"""
    personal_data_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    # Store in memory (backward compatibility)
    personal_data_store[personal_data_id] = {
        "id": personal_data_id,
        "nama": request.nama,
        "tanggal_lahir": request.tanggal_lahir,
        "tempat_lahir": request.tempat_lahir,
        "agama": request.agama,
        "created_at": now
    }
    
    # Also create in database if available
    if DB_AVAILABLE:
        try:
            client = create_client(
                nama=request.nama,
                tanggal_lahir=request.tanggal_lahir,
                tempat_lahir=request.tempat_lahir,
                agama=request.agama
            )
            # Store mapping from personal_data_id to client_id
            personal_data_store[personal_data_id]["_client_id"] = client["id"]
        except Exception as e:
            print(f"⚠️  Failed to create client in database: {e}")
    
    return PersonalDataResponse(
        personal_data_id=personal_data_id,
        status="created",
        created_at=now
    )


@api_router.get("/personal-data/{personal_data_id}", response_model=PersonalData)
async def get_personal_data(personal_data_id: str):
    """Get personal data by ID"""
    # Try in-memory first
    if personal_data_id in personal_data_store:
        data = personal_data_store[personal_data_id]
        return PersonalData(**data)
    
    # Try database if available
    if DB_AVAILABLE:
        try:
            # Check if this is actually a client_id
            client = get_client(personal_data_id)
            if client:
                return PersonalData(
                    id=client["id"],
                    nama=client["nama"],
                    tanggal_lahir=client["tanggal_lahir"],
                    tempat_lahir=client["tempat_lahir"],
                    agama=client["agama"],
                    created_at=client["created_at"].isoformat() if hasattr(client["created_at"], 'isoformat') else str(client["created_at"])
                )
        except Exception as e:
            print(f"⚠️  Database error: {e}")
    
    raise HTTPException(status_code=404, detail="Personal data not found")


@api_router.post("/sessions/with-personal-data", response_model=CreateSessionWithPersonalDataResponse)
async def create_session_with_personal_data(request: CreateSessionWithPersonalDataRequest):
    """Create new MBP session linked to personal data with question-based flow"""
    # Verify personal data exists
    if request.personal_data_id not in personal_data_store:
        raise HTTPException(status_code=404, detail="Personal data not found")
    
    session_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    sessions[session_id] = {
        "session_id": session_id,
        "personal_data_id": request.personal_data_id,
        "status": "active",
        "created_at": now,
        "updated_at": now,
        "messages": [],
        "metadata": request.metadata,
        "question_state": {
            "current_phase": "safety",
            "current_question_index": 0,
            "answers": [],
            "phase_complete": False,
            "phase_progress": {},
            "flexible_questions": {},
            "ai_processing_complete": False,
        }
    }
    
    # Also create in database if available
    client_id = None
    if DB_AVAILABLE:
        try:
            # Get client_id from personal data store
            pd_data = personal_data_store[request.personal_data_id]
            client_id = pd_data.get("_client_id")
            
            if client_id:
                db_session = create_session(client_id=client_id, metadata=request.metadata)
                # Store mapping
                sessions[session_id]["_db_session_id"] = db_session["id"]
                sessions[session_id]["_client_id"] = client_id
        except Exception as e:
            print(f"⚠️  Failed to create session in database: {e}")
    
    # Get first question from Phase 0
    first_q = PHASE_0_QUESTIONS[0] if PHASE_0_QUESTIONS else None
    first_question = None
    if first_q:
        first_question = Question(**first_q.to_dict())
    
    return CreateSessionWithPersonalDataResponse(
        session_id=session_id,
        status="created",
        created_at=now,
        current_phase="safety",
        first_question=first_question,
        message="Session created. Phase 0: Safety & Context Screening begins."
    )


# ============ ANALYSES ENDPOINTS ============

@api_router.post("/analyses", response_model=AnalysisResponse)
async def create_analysis(request: AnalysisRequest):
    """Save completed analysis results"""
    # Verify personal data exists
    if request.personal_data_id not in personal_data_store:
        raise HTTPException(status_code=404, detail="Personal data not found")
    
    # Verify session exists
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    analysis_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    # Get personal data for reference
    pd = personal_data_store[request.personal_data_id]
    
    analyses_store[analysis_id] = {
        "analysis_id": analysis_id,
        "personal_data_id": request.personal_data_id,
        "session_id": request.session_id,
        "nama": pd["nama"],
        "tanggal_lahir": pd["tanggal_lahir"],
        "tempat_lahir": pd["tempat_lahir"],
        "agama": pd["agama"],
        "final_profile": request.final_profile,
        "matrix_12d": request.matrix_12d,
        "executive_summary": request.executive_summary,
        "core_insights": request.core_insights,
        "tensions": request.tensions,
        "created_at": now
    }
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="created",
        created_at=now
    )


@api_router.get("/analyses", response_model=AnalysesListResponse)
async def list_analyses(personal_data_id: Optional[str] = None):
    """List all analyses, optionally filtered by personal_data_id"""
    analyses_list = []
    
    for analysis in analyses_store.values():
        if personal_data_id and analysis["personal_data_id"] != personal_data_id:
            continue
        
        analyses_list.append({
            "analysis_id": analysis["analysis_id"],
            "personal_data_id": analysis["personal_data_id"],
            "nama": analysis["nama"],
            "created_at": analysis["created_at"],
            "executive_summary": analysis.get("executive_summary")
        })
    
    # Sort by created_at descending (newest first)
    analyses_list.sort(key=lambda x: x["created_at"], reverse=True)
    
    return AnalysesListResponse(
        analyses=analyses_list,
        total=len(analyses_list)
    )


@api_router.get("/analyses/{analysis_id}", response_model=AnalysisDetail)
async def get_analysis(analysis_id: str):
    """Get full analysis by ID"""
    if analysis_id not in analyses_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis = analyses_store[analysis_id]
    return AnalysisDetail(**analysis)


# ============ CLIENT/RESUME ENDPOINTS ============

@api_router.get("/clients", response_model=Dict[str, Any])
async def list_all_clients():
    """List all clients (for resuming analysis)"""
    clients = []
    
    if DB_AVAILABLE:
        try:
            db_clients = list_clients()
            for client in db_clients:
                clients.append({
                    "id": client["id"],
                    "nama": client["nama"],
                    "tanggal_lahir": client["tanggal_lahir"],
                    "tempat_lahir": client["tempat_lahir"],
                    "agama": client["agama"],
                    "last_phase": client.get("last_phase", 0),
                    "created_at": client["created_at"],
                    "updated_at": client["updated_at"]
                })
        except Exception as e:
            print(f"⚠️  Database error: {e}")
    
    # Fallback to in-memory if no DB clients
    if not clients:
        for pd_id, pd in personal_data_store.items():
            clients.append({
                "id": pd_id,
                "nama": pd["nama"],
                "tanggal_lahir": pd["tanggal_lahir"],
                "tempat_lahir": pd["tempat_lahir"],
                "agama": pd["agama"],
                "last_phase": 0,
                "created_at": pd["created_at"],
                "updated_at": pd["created_at"]
            })
    
    return {
        "clients": clients,
        "total": len(clients)
    }


@api_router.get("/clients/{client_id}/progress", response_model=Dict[str, Any])
async def get_client_progress_endpoint(client_id: str):
    """Get client progress for resuming analysis"""
    if DB_AVAILABLE:
        try:
            progress = get_client_progress(client_id)
            if progress:
                return {
                    "can_resume": progress["can_resume"],
                    "client": progress["client"],
                    "session": progress.get("session"),
                    "current_phase": progress.get("current_phase"),
                    "current_phase_number": progress.get("current_phase_number"),
                    "total_answers": progress.get("total_answers", 0),
                    "answered_question_ids": progress.get("answered_question_ids", []),
                    "last_answer": progress.get("last_answer")
                }
        except Exception as e:
            print(f"⚠️  Database error: {e}")
    
    raise HTTPException(status_code=404, detail="Client not found or no progress available")


@api_router.post("/clients/{client_id}/resume", response_model=CreateSessionWithPersonalDataResponse)
async def resume_client_analysis(client_id: str):
    """Resume analysis for a client"""
    # Check if client exists
    client = None
    if DB_AVAILABLE:
        try:
            client = get_client(client_id)
        except Exception as e:
            print(f"⚠️  Database error: {e}")
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get progress
    progress = None
    if DB_AVAILABLE:
        try:
            progress = get_client_progress(client_id)
        except Exception as e:
            print(f"⚠️  Database error: {e}")
    
    if not progress or not progress.get("can_resume"):
        raise HTTPException(status_code=400, detail="No active session to resume. Please start a new analysis.")
    
    session_id = progress["session"]["id"]
    current_phase = progress.get("current_phase", "safety")
    current_phase_number = progress.get("current_phase_number", 0)
    
    # Create in-memory session linked to DB session
    now = datetime.now().isoformat()
    sessions[session_id] = {
        "session_id": session_id,
        "personal_data_id": client_id,  # Use client_id as personal_data_id
        "_client_id": client_id,
        "_db_session_id": session_id,
        "status": "active",
        "created_at": progress["session"]["created_at"],
        "updated_at": now,
        "messages": [],
        "metadata": {},
        "question_state": {
            "current_phase": current_phase,
            "current_question_index": progress.get("total_answers", 0),
            "answers": [],
            "phase_complete": False,
            "phase_progress": {},
            "flexible_questions": {},
            "ai_processing_complete": False,
        }
    }
    
    # Load existing answers into session
    db_answers = get_session_answers(session_id)
    for ans in db_answers:
        sessions[session_id]["question_state"]["answers"].append({
            "question_id": ans["question_id"],
            "phase": ans["phase"],
            "answer": ans["answer"],
            "timestamp": ans["created_at"]
        })
    
    # Get current question for the phase
    first_question = None
    questions = get_current_questions_for_phase(current_phase, sessions[session_id])
    answered_ids = set(a["question_id"] for a in sessions[session_id]["question_state"]["answers"] if a.get("phase") == current_phase)
    for q in questions:
        if q.question_id not in answered_ids:
            first_question = q
            break
    
    return CreateSessionWithPersonalDataResponse(
        session_id=session_id,
        status="resumed",
        created_at=now,
        current_phase=current_phase,
        first_question=first_question,
        message=f"Session resumed from Phase {current_phase_number}: {current_phase.capitalize()}."
    )


# Include API router with /api prefix
app.include_router(api_router, prefix="/api")

# Root health check (also available at /api/health)
@app.get("/health")
async def root_health_check():
    """Root health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        agents_count=22,
        mode=MBPConfig.MODE.value
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
