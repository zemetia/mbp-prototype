"""
MBP Parallel Node Execution
Optimized nodes with parallel execution patterns
"""
import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Tuple
from functools import lru_cache

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from state import MBPState, Phase
from llm import get_llm
from prompts import (
    SAFETY_CHECK_PROMPT,
    ANALYZER_PROMPT,
    HYPOTHESIS_MAKER_PROMPT,
    ADAPTATION_MINING_PROMPT,
    CROSS_VALIDATION_PROMPT,
    ASSESSOR_PROMPT,
    SYNTHESIZER_PROMPT,
    QUESTION_MAKER_PROMPT,
)
from utils import safe_json_parse, format_timing_context, log_phase_transition, NodeExecutionTimer


# ============================================================================
# CACHING LAYER
# ============================================================================

class LLMCache:
    """Simple in-memory cache for LLM responses"""
    
    def __init__(self, ttl_seconds: int = 300):
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._ttl = ttl_seconds
    
    def _make_key(self, prompt: str, content: str) -> str:
        """Create cache key from prompt + content hash"""
        import hashlib
        combined = f"{prompt}:{content}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def get(self, prompt: str, content: str) -> Any:
        """Get cached result if exists and not expired"""
        key = self._make_key(prompt, content)
        if key in self._cache:
            result, timestamp = self._cache[key]
            if datetime.now().timestamp() - timestamp < self._ttl:
                return result
            else:
                del self._cache[key]
        return None
    
    def set(self, prompt: str, content: str, result: Any):
        """Cache result with timestamp"""
        key = self._make_key(prompt, content)
        self._cache[key] = (result, datetime.now().timestamp())
    
    def clear(self):
        """Clear all cached entries"""
        self._cache.clear()


# Global cache instance
_llm_cache = LLMCache(ttl_seconds=300)


async def cached_llm_invoke(prompt: str, content: str, use_cache: bool = True) -> Any:
    """
    Invoke LLM with caching support
    
    Args:
        prompt: System prompt
        content: Human message content
        use_cache: Whether to use caching
        
    Returns:
        LLM response content
    """
    if use_cache:
        cached = _llm_cache.get(prompt, content)
        if cached:
            return cached
    
    response = await get_llm().ainvoke([
        SystemMessage(content=prompt),
        HumanMessage(content=content)
    ])
    
    if use_cache:
        _llm_cache.set(prompt, content, response.content)
    
    return response.content


# ============================================================================
# PARALLEL NODE EXECUTION
# ============================================================================

async def parallel_analyzer_hypothesis(state: MBPState) -> Dict[str, Any]:
    """
    Run analyzer and hypothesis maker in parallel for initial pass.
    
    This is used when:
    - No existing hypotheses (first pass)
    - We want to speed up initial analysis
    
    Returns combined results for both nodes.
    """
    session_id = state.get("session_id", "unknown")
    content = state.get("current_response", "")
    messages = state.get("messages", [])
    timing = format_timing_context(state)
    
    # Prepare prompts
    analyzer_prompt = ANALYZER_PROMPT.format(**timing)
    hypothesis_prompt = HYPOTHESIS_MAKER_PROMPT.format(**timing)
    
    # Prepare content for both calls
    analyzer_content = f"History: {json.dumps(messages[-3:])}\n\nAnalyze: {content}"
    hypothesis_content = f"Response: {content}\n\nGenerate initial hypotheses based on this single response."
    
    # Execute both LLM calls in parallel
    analyzer_task = cached_llm_invoke(analyzer_prompt, analyzer_content)
    hypothesis_task = cached_llm_invoke(hypothesis_prompt, hypothesis_content)
    
    analyzer_response, hypothesis_response = await asyncio.gather(
        analyzer_task, 
        hypothesis_task,
        return_exceptions=True
    )
    
    results = {
        "signals": [],
        "hypotheses": [],
        "confidence_overall": 0.5,
        "errors": []
    }
    
    # Parse analyzer result
    if isinstance(analyzer_response, Exception):
        results["errors"].append(f"Analyzer error: {analyzer_response}")
        results["signals"] = []
    else:
        analyzer_result = safe_json_parse(analyzer_response, {"signals": []})
        results["signals"] = analyzer_result.get("signals", [])
    
    # Parse hypothesis result
    if isinstance(hypothesis_response, Exception):
        results["errors"].append(f"Hypothesis error: {hypothesis_response}")
        results["hypotheses"] = []
    else:
        hypothesis_result = safe_json_parse(hypothesis_response, {
            "hypotheses": [],
            "confidence_overall": 0.5
        })
        results["hypotheses"] = hypothesis_result.get("hypotheses", [])
        results["confidence_overall"] = hypothesis_result.get("confidence_overall", 0.5)
    
    return results


async def parallel_assessment_prep(state: MBPState) -> Dict[str, Any]:
    """
    Prepare assessment data in parallel.
    
    Pre-computes synthesis components while assessor runs.
    """
    messages = state.get("messages", [])
    hypotheses = state.get("hypotheses", [])
    patterns = state.get("adaptation_patterns", [])
    tensions = state.get("tensions_detected", [])
    
    # These can all be prepared in parallel
    return {
        "user_responses": [m for m in messages if m.get("role") == "user"][-15:],
        "hypothesis_summary": _summarize_hypotheses(hypotheses),
        "pattern_summary": _summarize_patterns(patterns),
        "tension_summary": _summarize_tensions(tensions)
    }


def _summarize_hypotheses(hypotheses: List[Dict]) -> str:
    """Create condensed summary of hypotheses for faster processing"""
    if not hypotheses:
        return "No hypotheses yet."
    
    summary_parts = []
    for h in hypotheses[:5]:  # Limit to top 5
        field = h.get("field", "unknown")
        conf = h.get("confidence", 0)
        hyp = h.get("hypothesis", "")[:100]  # Truncate
        summary_parts.append(f"{field}({conf:.0%}): {hyp}")
    
    return " | ".join(summary_parts)


def _summarize_patterns(patterns: List[Dict]) -> str:
    """Create condensed summary of adaptation patterns"""
    if not patterns:
        return "No patterns yet."
    
    summary_parts = []
    for p in patterns[:3]:
        name = p.get("pattern_name", "unknown")
        conf = p.get("confidence", 0)
        summary_parts.append(f"{name}({conf:.0%})")
    
    return " | ".join(summary_parts)


def _summarize_tensions(tensions: List[Dict]) -> str:
    """Create condensed summary of tensions"""
    if not tensions:
        return "No tensions detected."
    
    summary_parts = []
    for t in tensions[:3]:
        dims = t.get("dimensions", [])
        sev = t.get("severity", "unknown")
        summary_parts.append(f"{'-'.join(dims)}({sev})")
    
    return " | ".join(summary_parts)


# ============================================================================
# BATCHED LLM OPERATIONS
# ============================================================================

async def batch_similarity_check(
    new_signals: List[Dict], 
    existing_signals: List[Dict],
    threshold: float = 0.8
) -> List[Dict]:
    """
    Check similarity of new signals against existing ones in batches.
    Prevents duplicate signals from being added.
    """
    if not existing_signals:
        return new_signals
    
    unique_signals = []
    
    for new_sig in new_signals:
        is_duplicate = False
        new_evidence = new_sig.get("evidence", "").lower()
        new_type = new_sig.get("type", "")
        
        for exist_sig in existing_signals:
            exist_evidence = exist_sig.get("evidence", "").lower()
            exist_type = exist_sig.get("type", "")
            
            # Simple similarity: same type and overlapping evidence
            if new_type == exist_type:
                # Check word overlap
                new_words = set(new_evidence.split())
                exist_words = set(exist_evidence.split())
                
                if new_words and exist_words:
                    overlap = len(new_words & exist_words) / max(len(new_words), len(exist_words))
                    if overlap > threshold:
                        is_duplicate = True
                        break
        
        if not is_duplicate:
            unique_signals.append(new_sig)
    
    return unique_signals


# ============================================================================
# OPTIMIZED NODE FUNCTIONS
# ============================================================================

async def optimized_analyzer_node(state: MBPState, config: dict = None) -> MBPState:
    """
    Optimized analyzer with caching and duplicate detection.
    """
    session_id = state.get("session_id", "unknown")
    
    with NodeExecutionTimer(session_id, "analyzer_node", state.get("current_phase"), state):
        content = state.get("current_response", "")
        messages = state.get("messages", [])
        timing = format_timing_context(state)
        
        try:
            prompt = ANALYZER_PROMPT.format(**timing)
            content_str = f"History: {json.dumps(messages[-3:])}\n\nAnalyze: {content}"
            
            response = await cached_llm_invoke(prompt, content_str, use_cache=True)
            result = safe_json_parse(response, {"signals": []})
            
            new_signals = result.get("signals", [])
            existing_signals = state.get("signals", [])
            
            # Filter duplicates before adding
            unique_signals = await batch_similarity_check(new_signals, existing_signals)
            
            if unique_signals:
                state["signals"] = existing_signals + unique_signals
            
            # Move to hypothesis generation
            state["current_phase"] = Phase.ADAPTIVE_PROBING
            
        except Exception as e:
            print(f"[Analyzer Error] {e}")
            state["error"] = str(e)
    
    return state


async def optimized_hypothesis_maker_node(state: MBPState, config: dict = None) -> MBPState:
    """
    Optimized hypothesis maker with conditional refinement.
    """
    session_id = state.get("session_id", "unknown")
    
    with NodeExecutionTimer(session_id, "hypothesis_maker_node", state.get("current_phase"), state):
        signals = state.get("signals", [])
        messages = state.get("messages", [])
        current_hypotheses = state.get("hypotheses", [])
        timing = format_timing_context(state)
        
        # Early exit if no new significant signals
        if len(signals) < 3 and len(messages) > 5:
            state["should_ask_question"] = True
            return state
        
        try:
            prompt = HYPOTHESIS_MAKER_PROMPT.format(**timing)
            
            # Use only recent signals to reduce token count
            recent_signals = signals[-10:] if len(signals) > 10 else signals
            
            if current_hypotheses and len(messages) > 3:
                # Refine mode: only process new signals against existing hypotheses
                content = f"Current: {json.dumps(current_hypotheses[:3])}\nNew signals: {json.dumps(recent_signals[-3:])}"
            else:
                # Generate mode
                content = f"Signals: {json.dumps(recent_signals)}"
            
            response = await cached_llm_invoke(prompt, content, use_cache=False)  # Don't cache refinements
            result = safe_json_parse(response, {"hypotheses": [], "confidence_overall": 0.5})
            
            state["hypotheses"] = result.get("hypotheses", current_hypotheses)
            state["overall_confidence"] = result.get("confidence_overall", 0.5)
            
            # Check progression criteria
            if result.get("confidence_overall", 0) >= 0.7 and len(messages) >= 8:
                state["current_phase"] = Phase.ADAPTATION_MINING
            else:
                state["should_ask_question"] = True
                
        except Exception as e:
            print(f"[Hypothesis Error] {e}")
            state["error"] = str(e)
            state["should_ask_question"] = True
    
    return state


async def optimized_assessor_node(state: MBPState, config: dict = None) -> MBPState:
    """
    Optimized assessor with pre-computed summaries.
    """
    session_id = state.get("session_id", "unknown")
    
    with NodeExecutionTimer(session_id, "assessor_node", state.get("current_phase"), state):
        messages = state.get("messages", [])
        timing = format_timing_context(state)
        
        # Pre-compute summaries to reduce token count
        user_responses = [m for m in messages if m.get("role") == "user"][-10:]  # Reduced from 15
        
        # Create condensed context
        condensed_history = []
        for i, msg in enumerate(user_responses):
            condensed_history.append(f"{i+1}. {msg.get('content', '')[:200]}...")  # Truncate each
        
        try:
            prompt = ASSESSOR_PROMPT.format(**timing)
            content = "User responses:\n" + "\n".join(condensed_history)
            
            response = await cached_llm_invoke(prompt, content, use_cache=False)
            result = safe_json_parse(response, {
                "scores": {},
                "tensions": [],
                "overall_confidence": 50
            })
            
            state["matrix_12d"] = result.get("scores", {})
            state["tensions_detected"] = result.get("tensions", [])
            state["overall_confidence"] = result.get("overall_confidence", 50)
            state["current_phase"] = Phase.CLOSURE
            state["should_generate_profile"] = True
            
        except Exception as e:
            print(f"[Assessor Error] {e}")
            state["error"] = str(e)
            state["current_phase"] = Phase.CLOSURE
    
    return state


async def optimized_synthesizer_node(state: MBPState, config: dict = None) -> MBPState:
    """
    Optimized synthesizer with pre-filtered inputs.
    """
    session_id = state.get("session_id", "unknown")
    
    with NodeExecutionTimer(session_id, "synthesizer_node", state.get("current_phase"), state):
        messages = state.get("messages", [])
        hypotheses = state.get("hypotheses", [])[:5]  # Top 5 only
        matrix = state.get("matrix_12d", {})
        patterns = state.get("adaptation_patterns", [])[:3]  # Top 3 only
        timing = format_timing_context(state)
        
        # Use only key user responses
        user_contents = [m.get("content", "")[:150] for m in messages if m.get("role") == "user"][-8:]
        
        try:
            prompt = SYNTHESIZER_PROMPT.format(**timing)
            content = f"""
Responses: {json.dumps(user_contents)}
Hypotheses: {json.dumps(hypotheses)}
12D Matrix: {json.dumps(matrix)}
Patterns: {json.dumps(patterns)}
"""
            
            response = await cached_llm_invoke(prompt, content, use_cache=False)
            result = safe_json_parse(response, {
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
# STREAMING OPTIMIZATIONS
# ============================================================================

async def streaming_question_maker(
    state: MBPState, 
    config: dict = None
) -> MBPState:
    """
    Question maker that can return partial results for faster UX.
    Returns a default question immediately, then refines in background.
    """
    session_id = state.get("session_id", "unknown")
    phase = state.get("current_phase")
    
    # Set a default question immediately for responsiveness
    default_questions = {
        Phase.CORE_QUESTIONING: "Ceritain lebih banyak tentang pengalaman kamu.",
        Phase.ADAPTIVE_PROBING: "Bagaimana perasaan kamu tentang situasi itu?",
        Phase.ADAPTATION_MINING: "Kapan pertama kali kamu merasa seperti ini?",
        Phase.CROSS_VALIDATION: "Apa yang biasanya kamu lakukan dalam situasi serupa?",
    }
    
    state["next_question"] = default_questions.get(phase, "Bisa ceritain lebih dalam?")
    state["should_ask_question"] = False
    
    # Try to get better question in background
    try:
        timing = format_timing_context(state)
        prompt = QUESTION_MAKER_PROMPT.format(**timing)
        
        hypotheses = state.get("hypotheses", [])[:3]
        messages = state.get("messages", [])
        content = f"Hypotheses: {json.dumps(hypotheses)}\nLast: {json.dumps(messages[-2:])}"
        
        response = await cached_llm_invoke(prompt, content, use_cache=True)
        result = safe_json_parse(response, {"question": state["next_question"]})
        
        # Update with better question if we got one
        if result.get("question"):
            state["next_question"] = result["question"]
            
    except Exception as e:
        print(f"[Question Maker Background Error] {e}")
        # Keep default question
    
    return state
