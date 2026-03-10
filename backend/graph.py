"""
MBP LangGraph Implementation
MirrorBreak Protocol 6-Phase Agent Flow - Main Graph Builder
"""
from typing import Dict, List, Any, Optional
from datetime import datetime

from langgraph.graph import StateGraph, END
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
except ImportError:
    # For langgraph >= 1.0
    from langgraph.checkpoint.memory import MemorySaver as SqliteSaver

from state import MBPState, Phase
from nodes import (
    safety_check_node,
    analyzer_node,
    hypothesis_maker_node,
    adaptation_mining_node,
    cross_validation_node,
    assessor_node,
    synthesizer_node,
    question_maker_node,
)
from utils import get_current_timestamp


# ============================================================================
# CONDITIONAL EDGE ROUTING FUNCTIONS
# ============================================================================

def route_after_safety(state: MBPState) -> str:
    """Route after safety check"""
    if state.get("current_phase") == Phase.ABORTED:
        return "aborted"
    return "analyzer"


def route_after_analyzer(state: MBPState) -> str:
    """Route after analysis"""
    return "hypothesis_maker"


def route_after_hypothesis(state: MBPState) -> str:
    """Route after hypothesis generation"""
    phase = state.get("current_phase")
    if phase == Phase.ADAPTATION_MINING:
        return "adaptation_mining"
    return "question_maker"


def route_after_mining(state: MBPState) -> str:
    """Route after adaptation mining"""
    phase = state.get("current_phase")
    if phase == Phase.CROSS_VALIDATION:
        return "cross_validation"
    return "question_maker"


def route_after_validation(state: MBPState) -> str:
    """Route after cross-validation"""
    phase = state.get("current_phase")
    if phase == Phase.SYNTHESIS:
        return "assessor"
    return "question_maker"


def route_after_question(state: MBPState) -> str:
    """Route after question generation"""
    phase = state.get("current_phase")
    if phase == Phase.CORE_QUESTIONING:
        return "analyzer"
    elif phase == Phase.ADAPTIVE_PROBING:
        return "hypothesis_maker"
    elif phase == Phase.ADAPTATION_MINING:
        return "adaptation_mining"
    elif phase == Phase.CROSS_VALIDATION:
        return "cross_validation"
    return END


def route_after_assessor(state: MBPState) -> str:
    """Route after 12D assessment"""
    if state.get("should_generate_profile"):
        return "synthesizer"
    return END


# ============================================================================
# GRAPH BUILDER
# ============================================================================

def create_mbp_graph(checkpointer=None):
    """Create the MBP LangGraph"""
    
    # Initialize graph
    workflow = StateGraph(MBPState)
    
    # Add nodes
    workflow.add_node("safety_check", safety_check_node)
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_node("hypothesis_maker", hypothesis_maker_node)
    workflow.add_node("adaptation_mining", adaptation_mining_node)
    workflow.add_node("cross_validation", cross_validation_node)
    workflow.add_node("assessor", assessor_node)
    workflow.add_node("synthesizer", synthesizer_node)
    workflow.add_node("question_maker", question_maker_node)
    
    # Set entry point
    workflow.set_entry_point("safety_check")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "safety_check", route_after_safety,
        {"aborted": END, "analyzer": "analyzer"}
    )
    
    workflow.add_conditional_edges(
        "analyzer", route_after_analyzer,
        {"hypothesis_maker": "hypothesis_maker"}
    )
    
    workflow.add_conditional_edges(
        "hypothesis_maker", route_after_hypothesis,
        {"adaptation_mining": "adaptation_mining", "question_maker": "question_maker"}
    )
    
    workflow.add_conditional_edges(
        "adaptation_mining", route_after_mining,
        {"cross_validation": "cross_validation", "question_maker": "question_maker"}
    )
    
    workflow.add_conditional_edges(
        "cross_validation", route_after_validation,
        {"assessor": "assessor", "question_maker": "question_maker"}
    )
    
    workflow.add_conditional_edges(
        "question_maker", route_after_question,
        {
            "analyzer": "analyzer",
            "hypothesis_maker": "hypothesis_maker",
            "adaptation_mining": "adaptation_mining",
            "cross_validation": "cross_validation",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "assessor", route_after_assessor,
        {"synthesizer": "synthesizer", END: END}
    )
    
    workflow.add_edge("synthesizer", END)
    
    # Compile with checkpointer
    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    return workflow.compile()


# ============================================================================
# RUN FUNCTION
# ============================================================================

async def run_mbp_graph(
    session_id: str,
    user_response: str,
    messages: List[Dict],
    previous_state: Optional[Dict] = None
) -> Dict[str, Any]:
    """Run the MBP graph with user input"""
    
    # Initialize or resume state
    if previous_state:
        state = MBPState(**previous_state)
    else:
        state = MBPState(
            session_id=session_id,
            current_phase=Phase.SAFETY_CHECK,
            messages=messages,
            current_response=user_response,
            response_timestamp=get_current_timestamp(),
            phase_start_time=get_current_timestamp(),
            safety_cleared=False,
            safety_data={},
            signals=[],
            hypotheses=[],
            adaptation_patterns=[],
            tensions_detected=[],
            matrix_12d={},
            overall_confidence=0.0,
            final_profile=None,
            next_question=None,
            should_ask_question=False,
            should_generate_profile=False,
            iteration_count=0,
            error=None,
            node_execution_times={}
        )
    
    # Update with new response and timestamp
    state["current_response"] = user_response
    state["messages"] = messages
    state["response_timestamp"] = get_current_timestamp()
    
    # Create checkpointer
    try:
        checkpointer = SqliteSaver.from_conn_string("mbp_graph.db")
    except AttributeError:
        # For MemorySaver (fallback)
        checkpointer = SqliteSaver()
    
    # Create and run graph
    graph = create_mbp_graph(checkpointer)
    
    config = {
        "configurable": {"thread_id": session_id},
        "recursion_limit": 50
    }
    
    result = await graph.ainvoke(state, config)
    
    return result
