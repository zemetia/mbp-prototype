"""
MBP v2.0 - State Definitions
"""
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class Phase(Enum):
    # Legacy phases (for backward compatibility)
    INTAKE = "intake"
    EXTRACTION = "extraction"
    SYNTHESIS = "synthesis"
    HYPOTHESIS = "hypothesis"
    VALIDATION = "validation"
    PROBE = "probe"
    ASSESSMENT = "assessment"
    OUTPUT = "output"
    COMPLETE = "complete"
    
    # New question-based flow phases
    SAFETY = "safety"           # Phase 0: Safety & Context Screening
    CORE = "core"               # Phase 1: Core Questioning
    PROBING = "probing"         # Phase 2: Adaptive Probing
    MINING = "mining"           # Phase 3: Adaptation Pattern Mining
    CROSS_VALIDATION = "cross_validation"  # Phase 4: Cross-Validation
    STRUCTURAL_SYNTHESIS = "structural_synthesis"  # Phase 5: Structural Synthesis
    CLOSURE = "closure"         # Phase 6: Debriefing & Closure


class ExtractedSignals(TypedDict):
    linguistic: List[Dict[str, Any]]
    emotional: List[Dict[str, Any]]
    cognitive: List[Dict[str, Any]]
    behavioral: List[Dict[str, Any]]


class Hypothesis(TypedDict):
    id: str
    field: str
    description: str
    confidence: float
    evidence: List[str]
    testable_prediction: str
    status: str  # leading, competing, rejected


class Contradiction(TypedDict):
    id: str
    description: str
    evidence_a: str
    evidence_b: str
    severity: str  # strong, moderate, subtle


class Matrix12D(TypedDict):
    AB: Dict[str, Any]  # Abstraction Bandwidth
    CDI: Dict[str, Any]  # Causal Depth
    CRF: Dict[str, Any]  # Cognitive Rigidity
    Processing_Style: Dict[str, Any]
    EG: Dict[str, Any]  # Emotional Granularity
    RSI: Dict[str, Any]  # Regulation Strategy
    VB: Dict[str, Any]  # Vulnerability Bandwidth
    Stress_Response: Dict[str, Any]
    ARP: Dict[str, Any]  # Authority Response
    RS: Dict[str, Any]  # Recognition Sensitivity
    COI: Dict[str, Any]  # Control Orientation
    ASC: Dict[str, Any]  # Adaptive Strength


class Answer(TypedDict):
    """User answer to a question"""
    question_id: str
    answer: str
    timestamp: str


class QuestionState(TypedDict):
    """Current question state in session"""
    question_id: str
    text: str
    type: str  # fixed or flexible
    dimensions: List[str]
    order: int


class MBPState(TypedDict):
    # Session Info
    session_id: str
    current_phase: Phase
    iteration_count: int
    
    # Input
    messages: List[Dict[str, str]]
    current_response: str
    response_timestamp: str
    
    # Safety
    safety_cleared: bool
    crisis_detected: bool
    crisis_type: Optional[str]
    
    # Layer 1: Extraction
    extracted_signals: ExtractedSignals
    
    # Layer 2: Synthesis
    unified_patterns: List[Dict[str, Any]]
    contextualized_patterns: List[Dict[str, Any]]
    cultural_frame: Optional[Dict[str, Any]]
    
    # Layer 3: Hypotheses
    hypotheses: Dict[str, List[Hypothesis]]  # by field
    
    # Layer 4: Validation
    contradictions: List[Contradiction]
    low_confidence_fields: List[str]
    
    # Layer 5: Probes
    next_question: Optional[str]
    probe_rationale: Optional[str]
    
    # Layer 6: Assessment
    matrix_12d: Optional[Matrix12D]
    tensions: List[Dict[str, Any]]
    
    # Layer 7: Output
    final_profile: Optional[Dict[str, Any]]
    user_report: Optional[Dict[str, Any]]
    
    # Question-based Flow State
    current_question_index: int
    current_question_id: Optional[str]
    answers: List[Answer]
    phase_complete: bool
    phase_question_count: int
    flexible_questions: List[QuestionState]  # AI-generated questions for flexible phases
    phase_progress: Dict[str, Any]  # Track progress per phase
    
    # Metadata
    error: Optional[str]
    node_execution_times: Dict[str, float]
    created_at: str


def create_initial_state(session_id: str, user_response: str, messages: List[Dict[str, str]]) -> MBPState:
    """Create initial state for new session"""
    return MBPState(
        session_id=session_id,
        current_phase=Phase.SAFETY,  # Start with Phase 0: Safety
        iteration_count=0,
        messages=messages,
        current_response=user_response,
        response_timestamp=datetime.now().isoformat(),
        safety_cleared=False,
        crisis_detected=False,
        crisis_type=None,
        extracted_signals={
            "linguistic": [],
            "emotional": [],
            "cognitive": [],
            "behavioral": []
        },
        unified_patterns=[],
        contextualized_patterns=[],
        cultural_frame=None,
        hypotheses={},
        contradictions=[],
        low_confidence_fields=[],
        next_question=None,
        probe_rationale=None,
        matrix_12d=None,
        tensions=[],
        final_profile=None,
        user_report=None,
        # Question-based Flow State - Initialize
        current_question_index=0,
        current_question_id=None,
        answers=[],
        phase_complete=False,
        phase_question_count=0,
        flexible_questions=[],
        phase_progress={},
        error=None,
        node_execution_times={},
        created_at=datetime.now().isoformat()
    )
