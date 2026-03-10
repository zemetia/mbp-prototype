"""
MBP Agent Node Functions
All agent node implementations for MirrorBreak Protocol
"""
import json
from datetime import datetime
from typing import Any

from langchain_core.messages import SystemMessage, HumanMessage

from state import MBPState, Phase
from llm import get_llm
from prompts import (
    SAFETY_CHECK_PROMPT,
    ANALYZER_PROMPT,
    HYPOTHESIS_MAKER_PROMPT,
    HYPOTHESIS_REFINE_PROMPT,
    ADAPTATION_MINING_PROMPT,
    CROSS_VALIDATION_PROMPT,
    ASSESSOR_PROMPT,
    SYNTHESIZER_PROMPT,
    QUESTION_MAKER_PROMPT,
    QUESTION_MAKER_PHASE_3,
    QUESTION_MAKER_PHASE_4,
)
from utils import (
    safe_json_parse,
    format_timing_context,
    log_phase_transition,
    NodeExecutionTimer,
    get_current_timestamp,
)


# ============================================================================
# SAFETY CHECK NODE
# ============================================================================

async def safety_check_node(state: MBPState, config: dict = None) -> MBPState:
    """Phase 0: Safety screening"""
    session_id = state.get("session_id", "unknown")
    current_phase = state.get("current_phase", Phase.SAFETY_CHECK)
    
    with NodeExecutionTimer(session_id, "safety_check_node", current_phase, state):
        # Update phase start time
        state["phase_start_time"] = get_current_timestamp()
        
        content = state.get("current_response", "")
        timing = format_timing_context(state)
        
        try:
            prompt = SAFETY_CHECK_PROMPT.format(**timing)
            response = await get_llm().ainvoke([
                SystemMessage(content=prompt),
                HumanMessage(content=f"Response to analyze: {content}")
            ])
            
            result = safe_json_parse(response.content, {
                "crisis_detected": False,
                "safety_cleared": True,
                "recommendation": "proceed",
                "reasoning": "Fallback: proceeding with caution"
            })
            
            state["safety_data"] = result
            state["safety_cleared"] = result.get("safety_cleared", False)
            
            if result.get("crisis_detected"):
                old_phase = state["current_phase"]
                state["current_phase"] = Phase.ABORTED
                state["error"] = f"Crisis detected: {result.get('crisis_type')}"
                log_phase_transition(session_id, old_phase, Phase.ABORTED, 
                                    state.get("iteration_count", 0))
            else:
                old_phase = state["current_phase"]
                state["current_phase"] = Phase.CORE_QUESTIONING
                state["should_ask_question"] = True
                log_phase_transition(session_id, old_phase, Phase.CORE_QUESTIONING, 
                                    state.get("iteration_count", 0))
                
        except Exception as e:
            print(f"[Safety Error] {e}")
            state["safety_cleared"] = True  # Fail open with caution
            old_phase = state["current_phase"]
            state["current_phase"] = Phase.CORE_QUESTIONING
            state["should_ask_question"] = True
            log_phase_transition(session_id, old_phase, Phase.CORE_QUESTIONING, 
                                state.get("iteration_count", 0))
        
        state["iteration_count"] = state.get("iteration_count", 0) + 1
    
    return state


# ============================================================================
# ANALYZER NODE
# ============================================================================

async def analyzer_node(state: MBPState, config: dict = None) -> MBPState:
    """Phase 1: Analyze response for signals"""
    session_id = state.get("session_id", "unknown")
    current_phase = state.get("current_phase", Phase.CORE_QUESTIONING)
    
    with NodeExecutionTimer(session_id, "analyzer_node", current_phase, state):
        content = state.get("current_response", "")
        messages = state.get("messages", [])
        timing = format_timing_context(state)
        
        try:
            prompt = ANALYZER_PROMPT.format(**timing)
            response = await get_llm().ainvoke([
                SystemMessage(content=prompt),
                HumanMessage(content=f"History: {json.dumps(messages[-3:])}\n\nAnalyze: {content}")
            ])
            
            result = safe_json_parse(response.content, {
                "signals": [],
                "linguistic_patterns": {},
                "emotional_indicators": {},
                "cognitive_markers": {}
            })
            
            new_signals = result.get("signals", [])
            state["signals"] = state.get("signals", []) + new_signals
            
            # Move to hypothesis generation
            old_phase = state["current_phase"]
            state["current_phase"] = Phase.ADAPTIVE_PROBING
            log_phase_transition(session_id, old_phase, Phase.ADAPTIVE_PROBING, 
                                state.get("iteration_count", 0))
            
        except Exception as e:
            print(f"[Analyzer Error] {e}")
            state["error"] = str(e)
    
    return state


# ============================================================================
# HYPOTHESIS MAKER NODE
# ============================================================================

async def hypothesis_maker_node(state: MBPState, config: dict = None) -> MBPState:
    """Phase 2: Generate/refine hypotheses"""
    session_id = state.get("session_id", "unknown")
    current_phase = state.get("current_phase", Phase.ADAPTIVE_PROBING)
    
    with NodeExecutionTimer(session_id, "hypothesis_maker_node", current_phase, state):
        signals = state.get("signals", [])
        messages = state.get("messages", [])
        current_hypotheses = state.get("hypotheses", [])
        timing = format_timing_context(state)
        
        # If we have hypotheses, refine them. Otherwise generate new.
        if current_hypotheses and len(messages) > 3:
            action = "refine"
        else:
            action = "generate"
        
        try:
            if action == "generate":
                prompt = HYPOTHESIS_MAKER_PROMPT.format(**timing)
                response = await get_llm().ainvoke([
                    SystemMessage(content=prompt),
                    HumanMessage(content=f"Signals: {json.dumps(signals[-10:])}\n\nGenerate hypotheses.")
                ])
            else:
                # Refine existing
                prompt = HYPOTHESIS_REFINE_PROMPT.format(**timing)
                response = await get_llm().ainvoke([
                    SystemMessage(content=prompt),
                    HumanMessage(content=f"Current hypotheses: {json.dumps(current_hypotheses)}\n\nNew signals: {json.dumps(signals[-3:])}")
                ])
            
            result = safe_json_parse(response.content, {
                "hypotheses": [],
                "confidence_overall": 0.5
            })
            
            new_hypotheses = result.get("hypotheses", [])
            state["hypotheses"] = new_hypotheses
            state["overall_confidence"] = result.get("confidence_overall", 0.5)
            
            # Check if ready for mining or need more probing
            if result.get("confidence_overall", 0) >= 0.7 and len(messages) >= 8:
                old_phase = state["current_phase"]
                state["current_phase"] = Phase.ADAPTATION_MINING
                log_phase_transition(session_id, old_phase, Phase.ADAPTATION_MINING, 
                                    state.get("iteration_count", 0))
            else:
                state["should_ask_question"] = True
                
        except Exception as e:
            print(f"[Hypothesis Error] {e}")
            state["error"] = str(e)
            state["should_ask_question"] = True
    
    return state


# ============================================================================
# ADAPTATION MINING NODE
# ============================================================================

async def adaptation_mining_node(state: MBPState, config: dict = None) -> MBPState:
    """Phase 3: Mine adaptation patterns"""
    session_id = state.get("session_id", "unknown")
    current_phase = state.get("current_phase", Phase.ADAPTATION_MINING)
    
    with NodeExecutionTimer(session_id, "adaptation_mining_node", current_phase, state):
        messages = state.get("messages", [])
        timing = format_timing_context(state)
        
        try:
            prompt = ADAPTATION_MINING_PROMPT.format(**timing)
            response = await get_llm().ainvoke([
                SystemMessage(content=prompt),
                HumanMessage(content=f"Responses: {json.dumps([m for m in messages if m.get('role') == 'user'][-5:])}")
            ])
            
            result = safe_json_parse(response.content, {
                "patterns": [],
                "ready_for_validation": False
            })
            
            patterns = result.get("patterns", [])
            state["adaptation_patterns"] = state.get("adaptation_patterns", []) + patterns
            
            if result.get("ready_for_validation") and len(patterns) >= 2:
                old_phase = state["current_phase"]
                state["current_phase"] = Phase.CROSS_VALIDATION
                log_phase_transition(session_id, old_phase, Phase.CROSS_VALIDATION, 
                                    state.get("iteration_count", 0))
            else:
                state["should_ask_question"] = True
                
        except Exception as e:
            print(f"[Mining Error] {e}")
            state["error"] = str(e)
            state["should_ask_question"] = True
    
    return state


# ============================================================================
# CROSS VALIDATION NODE
# ============================================================================

async def cross_validation_node(state: MBPState, config: dict = None) -> MBPState:
    """Phase 4: Cross-validate with 12D tension network"""
    session_id = state.get("session_id", "unknown")
    current_phase = state.get("current_phase", Phase.CROSS_VALIDATION)
    
    with NodeExecutionTimer(session_id, "cross_validation_node", current_phase, state):
        hypotheses = state.get("hypotheses", [])
        patterns = state.get("adaptation_patterns", [])
        timing = format_timing_context(state)
        
        try:
            prompt = CROSS_VALIDATION_PROMPT.format(**timing)
            response = await get_llm().ainvoke([
                SystemMessage(content=prompt),
                HumanMessage(content=f"Hypotheses: {json.dumps(hypotheses)}\n\nPatterns: {json.dumps(patterns)}")
            ])
            
            result = safe_json_parse(response.content, {
                "tensions_detected": [],
                "persona_coherence": "mixed",
                "ready_for_synthesis": True
            })
            
            state["tensions_detected"] = result.get("tensions_detected", [])
            
            if result.get("ready_for_synthesis"):
                old_phase = state["current_phase"]
                state["current_phase"] = Phase.SYNTHESIS
                log_phase_transition(session_id, old_phase, Phase.SYNTHESIS, 
                                    state.get("iteration_count", 0))
            else:
                state["should_ask_question"] = True
                
        except Exception as e:
            print(f"[Validation Error] {e}")
            # Proceed to synthesis on error
            old_phase = state["current_phase"]
            state["current_phase"] = Phase.SYNTHESIS
            log_phase_transition(session_id, old_phase, Phase.SYNTHESIS, 
                                state.get("iteration_count", 0))
    
    return state


# ============================================================================
# ASSESSOR NODE
# ============================================================================

async def assessor_node(state: MBPState, config: dict = None) -> MBPState:
    """Phase 5: Assess 12D Matrix"""
    session_id = state.get("session_id", "unknown")
    current_phase = state.get("current_phase", Phase.SYNTHESIS)
    
    with NodeExecutionTimer(session_id, "assessor_node", current_phase, state):
        messages = state.get("messages", [])
        user_responses = [m for m in messages if m.get("role") == "user"]
        timing = format_timing_context(state)
        
        try:
            prompt = ASSESSOR_PROMPT.format(**timing)
            response = await get_llm().ainvoke([
                SystemMessage(content=prompt),
                HumanMessage(content=f"All user responses: {json.dumps(user_responses[-15:])}")
            ])
            
            result = safe_json_parse(response.content, {
                "scores": {},
                "tensions": [],
                "overall_confidence": 50
            })
            
            state["matrix_12d"] = result.get("scores", {})
            state["tensions_detected"] = result.get("tensions", [])
            state["overall_confidence"] = result.get("overall_confidence", 50)
            
            old_phase = state["current_phase"]
            state["current_phase"] = Phase.CLOSURE
            state["should_generate_profile"] = True
            log_phase_transition(session_id, old_phase, Phase.CLOSURE, 
                                state.get("iteration_count", 0))
            
        except Exception as e:
            print(f"[Assessor Error] {e}")
            state["error"] = str(e)
            old_phase = state["current_phase"]
            state["current_phase"] = Phase.CLOSURE
            log_phase_transition(session_id, old_phase, Phase.CLOSURE, 
                                state.get("iteration_count", 0))
    
    return state


# ============================================================================
# SYNTHESIZER NODE
# ============================================================================

async def synthesizer_node(state: MBPState, config: dict = None) -> MBPState:
    """Phase 6: Generate final structural profile"""
    session_id = state.get("session_id", "unknown")
    current_phase = state.get("current_phase", Phase.CLOSURE)
    
    with NodeExecutionTimer(session_id, "synthesizer_node", current_phase, state):
        messages = state.get("messages", [])
        hypotheses = state.get("hypotheses", [])
        matrix = state.get("matrix_12d", {})
        patterns = state.get("adaptation_patterns", [])
        timing = format_timing_context(state)
        
        try:
            prompt = SYNTHESIZER_PROMPT.format(**timing)
            response = await get_llm().ainvoke([
                SystemMessage(content=prompt),
                HumanMessage(content=f"""
Messages: {json.dumps([m for m in messages if m.get('role') == 'user'][-15:])}
Hypotheses: {json.dumps(hypotheses)}
12D Matrix: {json.dumps(matrix)}
Patterns: {json.dumps(patterns)}
""")
            ])
            
            result = safe_json_parse(response.content, {
                "core_summary": "Terjadi error dalam generate profile. Silakan coba lagi.",
                "overall_confidence": 0
            })
            
            state["final_profile"] = result
            state["should_generate_profile"] = False
            
        except Exception as e:
            print(f"[Synthesizer Error] {e}")
            state["final_profile"] = {
                "error": str(e),
                "core_summary": "Terjadi error dalam generate profile. Silakan coba lagi."
            }
    
    return state


# ============================================================================
# QUESTION MAKER NODE
# ============================================================================

async def question_maker_node(state: MBPState, config: dict = None) -> MBPState:
    """Generate next question based on state"""
    session_id = state.get("session_id", "unknown")
    current_phase = state.get("current_phase", Phase.CORE_QUESTIONING)
    
    with NodeExecutionTimer(session_id, "question_maker_node", current_phase, state):
        hypotheses = state.get("hypotheses", [])
        messages = state.get("messages", [])
        phase = state.get("current_phase")
        timing = format_timing_context(state)
        
        # Select prompt based on phase
        if phase == Phase.ADAPTATION_MINING:
            prompt = QUESTION_MAKER_PHASE_3.format(**timing)
        elif phase == Phase.CROSS_VALIDATION:
            prompt = QUESTION_MAKER_PHASE_4.format(**timing)
        else:
            prompt = QUESTION_MAKER_PROMPT.format(**timing)
        
        try:
            response = await get_llm().ainvoke([
                SystemMessage(content=prompt),
                HumanMessage(content=f"Hypotheses: {json.dumps(hypotheses[:3])}\n\nLast messages: {json.dumps(messages[-2:])}")
            ])
            
            result = safe_json_parse(response.content, {
                "question": "Ceritain lebih banyak tentang itu.",
                "target_hypothesis": "unknown",
                "tension_target": "none",
                "question_type": "general"
            })
            
            state["next_question"] = result.get("question", "Ceritain lebih banyak tentang itu.")
            state["should_ask_question"] = False
            
        except Exception as e:
            print(f"[Question Error] {e}")
            state["next_question"] = "Bisa elaborate lebih dalam?"
            state["should_ask_question"] = False
    
    return state
