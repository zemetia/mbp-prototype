"""
MBP Optimized Graph Implementation
Parallel execution and performance optimizations
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from state import MBPState, Phase
from nodes_optimized import (
    parallel_analyzer_hypothesis,
    optimized_analyzer_node,
    optimized_hypothesis_maker_node,
    adaptation_mining_node,
    cross_validation_node,
    optimized_assessor_node,
    optimized_synthesizer_node,
    streaming_question_maker,
    cached_llm_invoke,
    LLMCache,
)


# ============================================================================
# PARALLEL FAN-OUT NODES
# ============================================================================

async def parallel_initial_analysis_node(state: MBPState, config: dict = None) -> MBPState:
    """
    Parallel node that runs analyzer and hypothesis maker together.
    
    This replaces the sequential analyzer -> hypothesis flow for initial passes,
    reducing 2 LLM calls from sequential (~40-60s) to parallel (~20-30s).
    """
    session_id = state.get("session_id", "unknown")
    
    # Only use parallel mode for initial analysis (no existing hypotheses)
    if state.get("hypotheses"):
        # Fall back to sequential for refinement
        state = await optimized_analyzer_node(state, config)
        return await optimized_hypothesis_maker_node(state, config)
    
    print(f"[{session_id}] Running parallel analyzer + hypothesis...")
    start_time = datetime.now()
    
    # Execute both in parallel
    results = await parallel_analyzer_hypothesis(state)
    
    # Update state with results
    if results.get("signals"):
        state["signals"] = state.get("signals", []) + results["signals"]
    
    if results.get("hypotheses"):
        state["hypotheses"] = results["hypotheses"]
        state["overall_confidence"] = results.get("confidence_overall", 0.5)
    
    if results.get("errors"):
        print(f"[{session_id}] Parallel errors: {results['errors']}")
    
    # Determine next phase
    messages = state.get("messages", [])
    if state.get("overall_confidence", 0) >= 0.7 and len(messages) >= 8:
        state["current_phase"] = Phase.ADAPTATION_MINING
    else:
        state["current_phase"] = Phase.ADAPTIVE_PROBING
        state["should_ask_question"] = True
    
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"[{session_id}] Parallel analysis complete in {elapsed:.1f}s")
    
    return state


async def fast_path_safety_node(state: MBPState, config: dict = None) -> MBPState:
    """
    Optimized safety check with early exit for clear cases.
    """
    session_id = state.get("session_id", "unknown")
    content = state.get("current_response", "").lower()
    
    # Fast-path: keyword-based pre-screening for obvious safe content
    safe_indicators = [
        "saya", "aku", "kemarin", "hari ini", "besok",  # Normal narrative markers
        "senang", "seneng", "bahagia", "santai",  # Positive affect
        "kerja", "kuliah", "sekolah", "teman",  # Normal activities
    ]
    
    crisis_keywords = [
        "bunuh diri", "mati", "ingin mati", "tidak ada harapan",
        "self harm", "luka", "sakit hati parah",
        "dengar suara", "lihat hal", "orang menguntit",
    ]
    
    # Quick keyword scan
    has_crisis_keyword = any(kw in content for kw in crisis_keywords)
    has_safe_indicator = any(ind in content for ind in safe_indicators)
    
    # If no crisis keywords and has normal narrative markers, fast-track
    if not has_crisis_keyword and len(content) > 50 and has_safe_indicator:
        print(f"[{session_id}] Fast-path safety clearance")
        state["safety_cleared"] = True
        state["safety_data"] = {
            "crisis_detected": False,
            "safety_cleared": True,
            "recommendation": "proceed",
            "reasoning": "Fast-path: no crisis indicators detected"
        }
        state["current_phase"] = Phase.CORE_QUESTIONING
        state["should_ask_question"] = True
        return state
    
    # Otherwise, do full LLM safety check
    from nodes import safety_check_node
    return await safety_check_node(state, config)


# ============================================================================
# CONDITIONAL ROUTING
# ============================================================================

def should_use_parallel_analysis(state: MBPState) -> str:
    """
    Determine if we can use parallel analysis or need sequential.
    """
    # Use parallel if:
    # 1. No existing hypotheses (initial pass)
    # 2. Fewer than 5 messages (early conversation)
    # 3. Not in refinement mode
    
    hypotheses = state.get("hypotheses", [])
    messages = state.get("messages", [])
    
    if not hypotheses and len(messages) < 5:
        return "parallel"
    return "sequential"


def route_after_safety_optimized(state: MBPState) -> str:
    """Optimized routing after safety check"""
    if state.get("current_phase") == Phase.ABORTED:
        return "aborted"
    
    # Check if we can use parallel analysis
    return should_use_parallel_analysis(state)


def route_after_analysis_optimized(state: MBPState) -> str:
    """Optimized routing after analysis"""
    current_phase = state.get("current_phase")
    
    if current_phase == Phase.ADAPTATION_MINING:
        return "adaptation_mining"
    elif current_phase == Phase.ADAPTIVE_PROBING:
        return "question_maker"
    return "question_maker"


def route_after_mining_optimized(state: MBPState) -> str:
    """Optimized routing after adaptation mining"""
    patterns = state.get("adaptation_patterns", [])
    
    # Fast-track to validation if we have enough patterns
    if len(patterns) >= 2:
        state["current_phase"] = Phase.CROSS_VALIDATION
        return "cross_validation"
    
    return "question_maker"


# ============================================================================
# OPTIMIZED GRAPH BUILDER
# ============================================================================

def create_optimized_mbp_graph(checkpointer=None):
    """
    Create optimized MBP graph with parallel execution paths.
    
    Optimizations:
    1. Parallel analyzer + hypothesis for initial passes
    2. Fast-path safety checks
    3. Conditional skipping for mature sessions
    4. Streaming question generation
    """
    workflow = StateGraph(MBPState)
    
    # Add all nodes
    workflow.add_node("safety_check", fast_path_safety_node)
    workflow.add_node("parallel_analysis", parallel_initial_analysis_node)
    workflow.add_node("analyzer", optimized_analyzer_node)
    workflow.add_node("hypothesis_maker", optimized_hypothesis_maker_node)
    workflow.add_node("adaptation_mining", adaptation_mining_node)
    workflow.add_node("cross_validation", cross_validation_node)
    workflow.add_node("assessor", optimized_assessor_node)
    workflow.add_node("synthesizer", optimized_synthesizer_node)
    workflow.add_node("question_maker", streaming_question_maker)
    
    # Set entry point
    workflow.set_entry_point("safety_check")
    
    # Safety check routing (with parallel vs sequential decision)
    workflow.add_conditional_edges(
        "safety_check",
        route_after_safety_optimized,
        {
            "aborted": END,
            "parallel": "parallel_analysis",
            "sequential": "analyzer"
        }
    )
    
    # Parallel analysis goes directly to question maker or mining
    workflow.add_conditional_edges(
        "parallel_analysis",
        route_after_analysis_optimized,
        {
            "adaptation_mining": "adaptation_mining",
            "question_maker": "question_maker"
        }
    )
    
    # Sequential analysis flow
    workflow.add_edge("analyzer", "hypothesis_maker")
    
    workflow.add_conditional_edges(
        "hypothesis_maker",
        route_after_analysis_optimized,
        {
            "adaptation_mining": "adaptation_mining",
            "question_maker": "question_maker"
        }
    )
    
    # Mining and validation flow
    workflow.add_conditional_edges(
        "adaptation_mining",
        route_after_mining_optimized,
        {
            "cross_validation": "cross_validation",
            "question_maker": "question_maker"
        }
    )
    
    workflow.add_conditional_edges(
        "cross_validation",
        lambda s: "assessor" if s.get("current_phase") == Phase.SYNTHESIS else "question_maker",
        {"assessor": "assessor", "question_maker": "question_maker"}
    )
    
    # Question maker loops back based on current phase
    workflow.add_conditional_edges(
        "question_maker",
        lambda s: s.get("current_phase", Phase.CORE_QUESTIONING),
        {
            Phase.CORE_QUESTIONING: "parallel_analysis",  # Use parallel on return
            Phase.ADAPTIVE_PROBING: "parallel_analysis",
            Phase.ADAPTATION_MINING: "adaptation_mining",
            Phase.CROSS_VALIDATION: "cross_validation",
            Phase.SYNTHESIS: END  # Shouldn't happen but safety
        }
    )
    
    # Assessment and synthesis
    workflow.add_edge("assessor", "synthesizer")
    workflow.add_edge("synthesizer", END)
    
    # Compile
    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    return workflow.compile()


# ============================================================================
# PERFORMANCE-MONITORED RUNNER
# ============================================================================

class MBPPerformanceMonitor:
    """Monitor and track MBP performance metrics"""
    
    def __init__(self):
        self.metrics = {
            "total_runs": 0,
            "total_time": 0.0,
            "phase_times": {},
            "cache_hits": 0,
            "cache_misses": 0,
        }
    
    def record_run(self, duration: float, phase_times: Dict[str, float]):
        """Record metrics from a single run"""
        self.metrics["total_runs"] += 1
        self.metrics["total_time"] += duration
        
        for phase, time in phase_times.items():
            if phase not in self.metrics["phase_times"]:
                self.metrics["phase_times"][phase] = []
            self.metrics["phase_times"][phase].append(time)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        avg_time = self.metrics["total_time"] / max(self.metrics["total_runs"], 1)
        
        phase_avgs = {}
        for phase, times in self.metrics["phase_times"].items():
            phase_avgs[phase] = sum(times) / len(times) if times else 0
        
        return {
            "average_run_time": avg_time,
            "total_runs": self.metrics["total_runs"],
            "average_phase_times": phase_avgs,
        }


# Global monitor instance
_performance_monitor = MBPPerformanceMonitor()


async def run_optimized_mbp_graph(
    session_id: str,
    user_response: str,
    messages: List[Dict],
    previous_state: Optional[Dict] = None,
    enable_monitoring: bool = True
) -> Dict[str, Any]:
    """
    Run the optimized MBP graph with performance monitoring.
    """
    from utils import get_current_timestamp
    
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
    
    # Update with new response
    state["current_response"] = user_response
    state["messages"] = messages
    state["response_timestamp"] = get_current_timestamp()
    
    # Create checkpointer
    checkpointer = MemorySaver()
    
    # Create and run graph
    graph = create_optimized_mbp_graph(checkpointer)
    
    config = {
        "configurable": {"thread_id": session_id},
        "recursion_limit": 50
    }
    
    # Run with timing
    start_time = datetime.now()
    result = await graph.ainvoke(state, config)
    duration = (datetime.now() - start_time).total_seconds()
    
    # Record metrics
    if enable_monitoring:
        _performance_monitor.record_run(
            duration,
            result.get("node_execution_times", {})
        )
        print(f"[MBP Run] Session {session_id}: {duration:.1f}s")
    
    return result


def get_performance_stats() -> Dict[str, Any]:
    """Get current performance statistics"""
    return _performance_monitor.get_stats()


def clear_llm_cache():
    """Clear the LLM response cache"""
    global _llm_cache
    _llm_cache = LLMCache(ttl_seconds=300)
