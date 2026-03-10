"""
MBP State Definition
MirrorBreak Protocol State Types
"""
from typing import Dict, List, Any, Optional, TypedDict
from enum import Enum


class Phase(str, Enum):
    """MBP 6 Phases"""
    SAFETY_CHECK = "safety_check"           # Phase 0
    CORE_QUESTIONING = "core_questioning"   # Phase 1
    ADAPTIVE_PROBING = "adaptive_probing"   # Phase 2
    ADAPTATION_MINING = "adaptation_mining" # Phase 3
    CROSS_VALIDATION = "cross_validation"   # Phase 4
    SYNTHESIS = "synthesis"                 # Phase 5
    CLOSURE = "closure"                     # Phase 6
    ABORTED = "aborted"


class MBPState(TypedDict):
    """State for MBP LangGraph"""
    # Session Info
    session_id: str
    current_phase: Phase
    
    # Conversation
    messages: List[Dict[str, Any]]  # [{role, content, timestamp, phase}]
    current_response: str
    response_timestamp: str  # ISO format timestamp
    
    # Phase 0: Safety
    safety_cleared: bool
    safety_data: Dict[str, Any]
    
    # Phase 1-2: Analysis & Hypotheses
    signals: List[Dict[str, Any]]
    hypotheses: List[Dict[str, Any]]
    
    # Phase 3: Patterns
    adaptation_patterns: List[Dict[str, Any]]
    
    # Phase 4: Validation
    tensions_detected: List[Dict[str, Any]]
    
    # Phase 5: 12D Matrix
    matrix_12d: Dict[str, Any]
    overall_confidence: float
    
    # Phase 6: Profile
    final_profile: Optional[Dict[str, Any]]
    
    # Control
    next_question: Optional[str]
    should_ask_question: bool
    should_generate_profile: bool
    iteration_count: int
    error: Optional[str]
    
    # Timing metadata
    phase_start_time: str  # ISO format timestamp when phase started
    node_execution_times: Dict[str, float]  # execution time per node
