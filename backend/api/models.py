"""
MBP v2.0 - API Request/Response Models
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class Phase(str, Enum):
    # Legacy phases
    INTAKE = "intake"
    EXTRACTION = "extraction"
    SYNTHESIS = "synthesis"
    CONTEXTUALIZATION = "contextualization"
    HYPOTHESIS = "hypothesis"
    VALIDATION = "validation"
    PROBE = "probe"
    ASSESSMENT = "assessment"
    OUTPUT = "output"
    COMPLETE = "complete"
    
    # New question-based flow phases
    SAFETY = "safety"           # Phase 0
    CORE = "core"               # Phase 1
    PROBING = "probing"         # Phase 2
    MINING = "mining"           # Phase 3
    CROSS_VALIDATION = "cross_validation"  # Phase 4
    STRUCTURAL_SYNTHESIS = "structural_synthesis"  # Phase 5
    CLOSURE = "closure"         # Phase 6


class Message(BaseModel):
    role: str = Field(..., description="user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: Optional[str] = None


class CreateSessionRequest(BaseModel):
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UserResponseRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    client_timestamp: Optional[str] = None


class UserResponseResponse(BaseModel):
    session_id: str
    phase: Phase
    next_question: Optional[str] = None
    final_profile: Optional[Dict[str, Any]] = None
    iteration_count: int
    processing_time_ms: int


class SessionStateResponse(BaseModel):
    session_id: str
    phase: Phase
    iteration_count: int
    safety_cleared: bool
    overall_confidence: float
    extracted_signals_summary: Dict[str, int]
    hypotheses_count: int
    low_confidence_fields: List[str]
    created_at: str
    updated_at: str


class ProfileResponse(BaseModel):
    session_id: str
    status: str
    final_profile: Optional[Dict[str, Any]]
    matrix_12d: Optional[Dict[str, Any]]
    executive_summary: Optional[str]
    core_insights: List[str]
    tensions: List[Dict[str, Any]]
    generated_at: str


class HealthResponse(BaseModel):
    status: str
    version: str
    agents_count: int
    mode: str


# ============ QUESTION-BASED FLOW MODELS ============
# Define Question and related types BEFORE they are referenced

class QuestionType(str, Enum):
    FIXED = "fixed"
    FLEXIBLE = "flexible"


class Question(BaseModel):
    """Question template"""
    question_id: str = Field(..., alias="id")
    id: str = Field(..., description="Alias for question_id")
    phase: str
    phase_number: int = Field(default=0, description="Phase number (0-6)")
    type: QuestionType
    text: str
    dimensions: List[str] = Field(default_factory=list)
    order: int = 0
    sub_questions: List[str] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "q_001",
                "question_id": "q_001",
                "phase": "safety",
                "phase_number": 0,
                "type": "fixed",
                "text": "Sample question",
                "dimensions": ["emosi"],
                "order": 1
            }
        }


# Forward reference safe models
class Answer(BaseModel):
    """User answer to a question"""
    question_id: str
    answer: str
    timestamp: str


class QuestionsResponse(BaseModel):
    """Response for getting current phase questions"""
    session_id: str
    phase: str
    phase_number: int = Field(..., description="Phase number (0-6)")
    question: Optional[Question] = Field(None, description="Current question to answer")
    questions: List[Question] = Field(default_factory=list, description="All questions in current phase")
    current_question_index: int
    total_questions_in_phase: int
    phase_complete: bool
    progress_percentage: float
    analysis_complete: bool = Field(default=False, description="Whether entire analysis is complete")


class AnswerRequest(BaseModel):
    """Request to submit an answer"""
    question_id: str
    answer: str = Field(..., min_length=1, max_length=5000)


class AnswerResponse(BaseModel):
    """Response after submitting an answer"""
    session_id: str
    phase: str
    question_id: str
    next_question: Optional[Question] = None
    phase_complete: bool
    can_advance: bool  # Whether user can advance to next phase
    analysis_complete: bool = Field(default=False, description="Whether entire analysis is complete")
    message: str


class NextPhaseRequest(BaseModel):
    """Request to advance to next phase"""
    confirm: bool = True  # User confirmation to proceed


class NextPhaseResponse(BaseModel):
    """Response after advancing to next phase"""
    session_id: str
    previous_phase: str
    new_phase: str
    next_phase: str = Field(..., description="Alias for new_phase for frontend compatibility")
    phase_number: int = Field(..., description="Phase number (0-6)")
    first_question: Optional[Question] = None
    ai_processing_complete: bool
    analysis_complete: bool = Field(default=False, description="Whether entire analysis is complete")
    message: str


class PhaseProgress(BaseModel):
    """Progress information for a phase"""
    phase: str
    fixed_questions_total: int
    fixed_questions_answered: int
    flexible_questions_total: int
    flexible_questions_answered: int
    phase_complete: bool


class SessionQuestionsStateResponse(BaseModel):
    """Extended session state with question progress"""
    session_id: str
    current_phase: str
    current_question_index: int
    phase_complete: bool
    answers_count: int
    phase_progress: List[PhaseProgress]
    can_advance: bool


# Now define CreateSessionResponse (after Question class is defined)
class CreateSessionResponse(BaseModel):
    session_id: str
    status: str
    created_at: str
    current_phase: str = "safety"
    first_question: Optional[Question] = None
    message: str = "Session created successfully. Please answer the first question to begin."


# ============ PERSONAL DATA MODELS ============

class PersonalDataRequest(BaseModel):
    nama: str = Field(..., min_length=1, max_length=100, description="Nama lengkap")
    tanggal_lahir: str = Field(..., min_length=1, max_length=20, description="Format: DD/MM/YYYY")
    tempat_lahir: str = Field(..., min_length=1, max_length=100, description="Tempat lahir")
    agama: str = Field(..., min_length=1, max_length=50, description="Agama")


class PersonalDataResponse(BaseModel):
    personal_data_id: str
    status: str
    created_at: str


class PersonalData(BaseModel):
    id: str
    nama: str
    tanggal_lahir: str
    tempat_lahir: str
    agama: str
    created_at: str


class CreateSessionWithPersonalDataRequest(BaseModel):
    personal_data_id: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CreateSessionWithPersonalDataResponse(BaseModel):
    session_id: str
    status: str
    created_at: str
    current_phase: str = "safety"
    first_question: Optional[Question] = None
    message: str = "Session created. Phase 0: Safety & Context Screening begins."


# ============ ANALYSIS MODELS ============

class AnalysisRequest(BaseModel):
    personal_data_id: str
    session_id: str
    final_profile: Dict[str, Any]
    matrix_12d: Optional[Dict[str, Any]] = None
    executive_summary: Optional[str] = None
    core_insights: List[str] = Field(default_factory=list)
    tensions: List[Dict[str, Any]] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    created_at: str


class AnalysisSummary(BaseModel):
    analysis_id: str
    personal_data_id: str
    nama: str
    created_at: str
    executive_summary: Optional[str] = None


class AnalysesListResponse(BaseModel):
    analyses: List[AnalysisSummary]
    total: int


class AnalysisDetail(BaseModel):
    analysis_id: str
    personal_data_id: str
    session_id: str
    nama: str
    tanggal_lahir: str
    tempat_lahir: str
    agama: str
    final_profile: Dict[str, Any]
    matrix_12d: Optional[Dict[str, Any]] = None
    executive_summary: Optional[str] = None
    core_insights: List[str]
    tensions: List[Dict[str, Any]]
    created_at: str
