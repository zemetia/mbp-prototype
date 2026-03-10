from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session as DBSession
from datetime import datetime
import json

from repositories.session_repo import SessionRepository, AnswerRepository
from models.domain import Session, Answer
from questions import QuestionManager, QuestionType, PHASE_0_QUESTIONS

class QuestionService:
    def __init__(self, db: DBSession):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.answer_repo = AnswerRepository(db)

    def get_phase_number(self, phase: str) -> int:
        phase_map = {
            "safety": 0, "core": 1, "probing": 2, "mining": 3,
            "validation": 4, "synthesis": 5, "closure": 6
        }
        return phase_map.get(phase, 0)

    def check_phase_complete(self, session: Session, current_phase: str) -> bool:
        """Determines if the phase is completed based on answered DB questions vs active questions"""
        questions = self.get_current_questions_for_phase(session, current_phase)
        if not questions:
            return True

        answers = self.answer_repo.get_by_session_id(session.id)
        answered_ids = {a.question_id for a in answers if a.phase == current_phase}

        all_answered = all(q["id"] in answered_ids for q in questions)
        return all_answered

    def get_next_question(self, session: Session, phase: str) -> Optional[Dict]:
        questions = self.get_current_questions_for_phase(session, phase)
        answers = self.answer_repo.get_by_session_id(session.id)
        answered_ids = {a.question_id for a in answers if a.phase == phase}

        for q in questions:
            if q["id"] not in answered_ids:
                return q
        return None

    def get_current_questions_for_phase(self, session: Session, phase: str) -> List[Dict]:
        """Get questions for the current phase, including any flexible questions from session_metadata"""
        fixed = QuestionManager.get_phase_questions(phase)
        questions = []
        for q in fixed:
            q_dict = q.to_dict()
            q_dict["id"] = q_dict.get("question_id", q_dict.get("id"))
            questions.append(q_dict)

        metadata = session.session_metadata or {}
        flexible = metadata.get("flexible_questions", {}).get(phase, [])

        for fq in flexible:
            fq["id"] = fq["question_id"]
            fq["type"] = QuestionType.FLEXIBLE.value
            questions.append(fq)

        return questions

    def submit_answer(self, session_id: str, question_id: str, answer_text: str) -> Dict[str, Any]:
        session = self.session_repo.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        phase = session.current_phase
        questions = self.get_current_questions_for_phase(session, phase)
        question = next((q for q in questions if q["id"] == question_id), None)

        if not question:
            raise ValueError(f"Question {question_id} not found in current phase {phase}")

        # Save the answer
        self.answer_repo.create({
            "client_id": session.client_id,
            "session_id": session.id,
            "question_id": question_id,
            "question_text": question.get("text", ""),
            "answer": answer_text,
            "phase": phase,
            "dimensions": question.get("dimensions", []),
            "question_type": question.get("type", "fixed"),
            "order_index": question.get("order", 0)
        })

        # Update completeness
        phase_complete = self.check_phase_complete(session, phase)
        next_q = self.get_next_question(session, phase)

        # Triggers AI Processing flag implicitly logic
        ai_processing_complete = False
        if not next_q:
            # Generate flex questions if empty
            ai_processing_complete = self.process_phase_completion(session)
            # Re-fetch next q in case flexible ones were just added
            next_q = self.get_next_question(session, phase)

        # Save session updates back
        self.session_repo.update(session, {
            "phase_complete": phase_complete,
            "updated_at": datetime.utcnow()
        })

        analysis_complete = phase == "closure" and phase_complete

        return {
            "next_question": next_q,
            "phase_complete": phase_complete,
            "analysis_complete": analysis_complete,
            "can_advance": phase_complete and ai_processing_complete
        }

    def process_phase_completion(self, session: Session) -> bool:
        """Process completion: Generate flexible questions, return whether AI processing is done."""
        phase = session.current_phase
        metadata = dict(session.session_metadata or {})
        
        if "flexible_questions" not in metadata:
            metadata["flexible_questions"] = {}

        generated = False
        if phase in ["probing", "mining", "validation", "closure"]:
            # Only generate once per phase
            if phase not in metadata["flexible_questions"] or not metadata["flexible_questions"][phase]:
                flexible = self.generate_flexible_questions(phase, metadata)
                if flexible:
                    metadata["flexible_questions"][phase] = flexible
                    generated = True

        if generated:
            self.session_repo.update(session, {"session_metadata": metadata})

        return True # AI processing marked complete

    def advance_phase(self, session_id: str) -> str:
        session = self.session_repo.get(session_id)
        current_phase = session.current_phase

        if not self.check_phase_complete(session, current_phase):
            raise ValueError(f"Phase {current_phase} not complete")

        next_phase = QuestionManager.get_next_phase(current_phase)
        if next_phase:
            self.session_repo.update(session, {
                "current_phase": next_phase,
                "current_phase_number": self.get_phase_number(next_phase),
                "phase_complete": False,
                "updated_at": datetime.utcnow()
            })
            return next_phase
            
        return current_phase

    def generate_flexible_questions(self, phase: str, metadata: Dict) -> List[Dict]:
        from questions import (
            PHASE_2_FLEXIBLE_TEMPLATES, PHASE_3_FLEXIBLE_CATEGORIES,
            PHASE_4_FLEXIBLE_TEMPLATES, PHASE_6_FLEXIBLE_TEMPLATES
        )
        templates = {}
        if phase == "probing": templates = PHASE_2_FLEXIBLE_TEMPLATES
        elif phase == "mining": templates = PHASE_3_FLEXIBLE_CATEGORIES
        elif phase == "validation": templates = PHASE_4_FLEXIBLE_TEMPLATES
        elif phase == "closure": templates = PHASE_6_FLEXIBLE_TEMPLATES
        
        flexible_questions = []
        for i, (key, template) in enumerate(list(templates.items())[:3]):
            text = template
            if "[PATTERN]" in text: text = text.replace("[PATTERN]", "perfeksionis")
            if "[RELATIONSHIP]" in text: text = text.replace("[RELATIONSHIP]", "keluarga")
            if "[EMOTION]" in text: text = text.replace("[EMOTION]", "marah")
            
            flexible_questions.append({
                "question_id": f"{phase}_flex_{i+1}",
                "text": text,
                "dimensions": [key],
                "order": 100 + i,
                "type": QuestionType.FLEXIBLE.value
            })
        return flexible_questions
