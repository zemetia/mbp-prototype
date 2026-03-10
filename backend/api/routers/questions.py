from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Any

from core.database import get_db
from models.domain import Session as SessionModel
from services.question_service import QuestionService
from api.models import Question, QuestionsResponse, AnswerRequest, AnswerResponse, NextPhaseRequest, NextPhaseResponse, SessionQuestionsStateResponse, PhaseProgress

router = APIRouter(prefix="/sessions/{session_id}", tags=["questions"])

def get_question_service(db: Session = Depends(get_db)) -> QuestionService:
    return QuestionService(db=db)

@router.get("/questions", response_model=QuestionsResponse)
async def get_questions(session_id: str, service: QuestionService = Depends(get_question_service)):
    """Get current questions for the session's current phase"""
    try:
        session = service.session_repo.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        phase = session.current_phase
        phase_number = session.current_phase_number

        questions_dicts = service.get_current_questions_for_phase(session, phase)
        questions = [Question(**q) for q in questions_dicts]
        
        answers = service.answer_repo.get_by_session_id(session_id)
        answered_count = len([a for a in answers if a.phase == phase])
        total = len(questions)
        progress = (answered_count / total * 100) if total > 0 else 100
        
        phase_complete = service.check_phase_complete(session, phase)
        
        current_question_dict = service.get_next_question(session, phase)
        current_question = Question(**current_question_dict) if current_question_dict else None
        
        analysis_complete = phase == "closure" and phase_complete

        return QuestionsResponse(
            session_id=session_id,
            phase=phase,
            phase_number=phase_number,
            question=current_question,
            questions=questions,
            current_question_index=answered_count,
            total_questions_in_phase=total,
            phase_complete=phase_complete,
            progress_percentage=round(progress, 1),
            analysis_complete=analysis_complete
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/answer", response_model=AnswerResponse)
async def submit_answer(session_id: str, request: AnswerRequest, service: QuestionService = Depends(get_question_service)):
    """Submit an answer for the current question"""
    try:
        session = service.session_repo.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        phase = session.current_phase
        
        result = service.submit_answer(session_id, request.question_id, request.answer)
        
        next_obj = result.get("next_question")
        next_question = Question(**next_obj) if next_obj else None
        
        message = "Answer recorded."
        if result["analysis_complete"]:
            message = "Session complete. Analysis finished."
        elif result["phase_complete"]:
            message = "All questions in this phase answered. AI is processing..."
        elif next_question:
            message = f"Proceed to question: {next_question.question_id}"
            
        return AnswerResponse(
            session_id=session_id,
            phase=phase,
            question_id=request.question_id,
            next_question=next_question,
            phase_complete=result["phase_complete"],
            can_advance=result["can_advance"],
            analysis_complete=result["analysis_complete"],
            message=message
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/next-phase", response_model=NextPhaseResponse)
async def advance_phase(session_id: str, request: NextPhaseRequest, service: QuestionService = Depends(get_question_service)):
    """Advance to the next phase"""
    try:
        session = service.session_repo.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        previous_phase = session.current_phase
        new_phase = service.advance_phase(session_id)
        new_phase_number = service.get_phase_number(new_phase)
        
        # Get first question of new phase
        questions = service.get_current_questions_for_phase(session, new_phase)
        first_q = Question(**questions[0]) if questions else None
        
        analysis_complete = new_phase == "closure" and service.check_phase_complete(session, new_phase)
        
        message = f"Advanced from {previous_phase} to {new_phase}."
        if new_phase == "closure":
            message = "Final phase reached. Preparing for session closure."
        elif new_phase == previous_phase:
            message = "No next phase available. Session may be complete."
            analysis_complete = True
            
        return NextPhaseResponse(
            session_id=session_id,
            previous_phase=previous_phase,
            new_phase=new_phase,
            next_phase=new_phase,
            phase_number=new_phase_number,
            first_question=first_q,
            ai_processing_complete=True,
            analysis_complete=analysis_complete,
            message=message
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
