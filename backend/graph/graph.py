"""
MBP v2.0 - Main LangGraph Definition
Orchestrates all agents through the flow
"""
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from graph.state import MBPState, Phase, create_initial_state
from agents.intake import IntakeAgent
from agents.extractors.runner import run_extraction_layer
from agents.synthesis import PatternSynthesizer
from agents.contextualizer import Contextualizer
from agents.hypothesis.runner import run_hypothesis_layer
from agents.validation import EvidenceEvaluator, ContradictionDetector, GapAnalyzer
from agents.probes import ProbeDesigner, ProbeSelector
from agents.assessment import TensionMapper, MatrixPositioner, Validator
from agents.output import ProfileComposer, Explainer

# Agent instances
_intake = IntakeAgent()
_synthesizer = PatternSynthesizer()
_contextualizer = Contextualizer()
_evidence_eval = EvidenceEvaluator()
_contradiction = ContradictionDetector()
_gap_analyzer = GapAnalyzer()
_probe_designer = ProbeDesigner()
_probe_selector = ProbeSelector()
_tension_mapper = TensionMapper()
_matrix_positioner = MatrixPositioner()
_validator = Validator()
_composer = ProfileComposer()
_explainer = Explainer()


# ============ NODE FUNCTIONS ============

async def intake_node(state: MBPState) -> Dict[str, Any]:
    """Phase: INTAKE - Safety check"""
    print(f"\n[Phase: INTAKE] Running safety check...")
    
    result = await _intake.execute(state)
    
    if result.success:
        return {
            "safety_cleared": result.data.get("safety_cleared", True),
            "crisis_detected": result.data.get("crisis_detected", False),
            "crisis_type": result.data.get("crisis_type"),
            "current_phase": Phase.EXTRACTION if result.data.get("safety_cleared") else Phase.INTAKE
        }
    else:
        return {
            "error": f"Intake failed: {result.error}",
            "current_phase": Phase.INTAKE
        }


async def extraction_node(state: MBPState) -> Dict[str, Any]:
    """Phase: EXTRACTION - Parallel signal extraction"""
    print(f"\n[Phase: EXTRACTION] Running parallel extractors...")
    
    result = await run_extraction_layer(state)
    
    return {
        "extracted_signals": result.get("extracted_signals", {}),
        "current_phase": Phase.SYNTHESIS,
        "iteration_count": state.get("iteration_count", 0) + 1
    }


async def synthesis_node(state: MBPState) -> Dict[str, Any]:
    """Phase: SYNTHESIS - Combine signals"""
    print(f"\n[Phase: SYNTHESIS] Synthesizing patterns...")
    
    result = await _synthesizer.execute(state)
    
    if result.success:
        return {
            "unified_patterns": result.data.get("unified_patterns", []),
            "cross_correlations": result.data.get("cross_correlations", []),
            "dominant_themes": result.data.get("dominant_themes", []),
            "current_phase": Phase.HYPOTHESIS
        }
    else:
        return {
            "current_phase": Phase.HYPOTHESIS
        }


async def contextualizer_node(state: MBPState) -> Dict[str, Any]:
    """Phase: CONTEXTUALIZATION - Add cultural/temporal context"""
    print(f"\n[Phase: CONTEXTUALIZATION] Adding context...")
    
    result = await _contextualizer.execute(state)
    
    if result.success:
        return {
            "contextualized_patterns": result.data.get("contextualized_patterns", []),
            "cultural_frame": result.data.get("cultural_frame", {}),
            "current_phase": Phase.HYPOTHESIS
        }
    else:
        # Fallback: use unified patterns as contextualized
        return {
            "contextualized_patterns": state.get("unified_patterns", []),
            "cultural_frame": {},
            "current_phase": Phase.HYPOTHESIS
        }


async def hypothesis_node(state: MBPState) -> Dict[str, Any]:
    """Phase: HYPOTHESIS - Parallel hypothesis generation"""
    print(f"\n[Phase: HYPOTHESIS] Running parallel generators...")
    
    result = await run_hypothesis_layer(state)
    
    return {
        "hypotheses": result.get("hypotheses", {}),
        "current_phase": Phase.VALIDATION
    }


async def validation_node(state: MBPState) -> Dict[str, Any]:
    """Phase: VALIDATION - Evaluate and detect gaps"""
    print(f"\n[Phase: VALIDATION] Validating hypotheses...")
    
    # Run validation agents
    evidence_result = await _evidence_eval.execute(state)
    contradiction_result = await _contradiction.execute(state)
    gap_result = await _gap_analyzer.execute(state)
    
    updates = {
        "contradictions": contradiction_result.data.get("contradictions", []) if contradiction_result.success else [],
        "current_phase": Phase.PROBE
    }
    
    if gap_result.success:
        updates["low_confidence_fields"] = gap_result.data.get("low_confidence_fields", [])
        updates["overall_confidence"] = gap_result.data.get("overall_confidence", 0)
        
        # If no low confidence fields, skip to assessment
        if not gap_result.data.get("should_continue_probing", True):
            print("  ✅ Confidence threshold met, proceeding to assessment")
            updates["current_phase"] = Phase.ASSESSMENT
    
    return updates


async def probe_node(state: MBPState) -> Dict[str, Any]:
    """Phase: PROBE - Design and select question"""
    print(f"\n[Phase: PROBE] Designing probe...")
    
    # Design probes
    design_result = await _probe_designer.execute(state)
    
    if design_result.success:
        state["candidate_probes"] = design_result.data.get("candidate_probes", [])
    
    # Select probe
    select_result = await _probe_selector.execute(state)
    
    if select_result.success:
        return {
            "next_question": select_result.data.get("next_question"),
            "probe_rationale": select_result.data.get("probe_rationale"),
            "current_phase": Phase.COMPLETE  # Return to user
        }
    else:
        return {
            "next_question": "Ceritakan lebih lanjut tentang pola pikir Anda.",
            "current_phase": Phase.COMPLETE
        }


async def assessment_node(state: MBPState) -> Dict[str, Any]:
    """Phase: ASSESSMENT - Generate 12D matrix"""
    print(f"\n[Phase: ASSESSMENT] Generating 12D matrix...")
    
    # Run assessment agents
    tension_result = await _tension_mapper.execute(state)
    matrix_result = await _matrix_positioner.execute(state)
    
    updates = {"current_phase": Phase.OUTPUT}
    
    if tension_result.success:
        updates["tensions"] = tension_result.data.get("tensions", [])
    
    if matrix_result.success:
        updates["matrix_12d"] = matrix_result.data.get("matrix_12d", {})
    
    return updates


async def output_node(state: MBPState) -> Dict[str, Any]:
    """Phase: OUTPUT - Compose final profile"""
    print(f"\n[Phase: OUTPUT] Composing profile...")
    
    # Validate first
    val_result = await _validator.execute(state)
    
    if val_result.success and not val_result.data.get("validation_passed", True):
        print(f"  ⚠️ Validation failed, quality: {val_result.data.get('quality_rating')}")
    
    # Compose profile
    composer_result = await _composer.execute(state)
    
    updates = {"current_phase": Phase.COMPLETE}
    
    if composer_result.success:
        updates["final_profile"] = composer_result.data.get("final_profile", {})
        
        # Generate user report
        explainer_result = await _explainer.execute(state)
        if explainer_result.success:
            updates["user_report"] = explainer_result.data.get("user_report", {})
            updates["executive_summary"] = explainer_result.data.get("executive_summary", "")
    
    return updates


# ============ ROUTING FUNCTIONS ============

def route_after_intake(state: MBPState) -> Literal["extraction", "end"]:
    """Route based on safety check"""
    if state.get("crisis_detected"):
        return "end"
    if state.get("safety_cleared"):
        return "extraction"
    return "end"


def route_after_validation(state: MBPState) -> Literal["probe", "assessment"]:
    """Route based on confidence check"""
    low_conf = state.get("low_confidence_fields", [])
    iteration = state.get("iteration_count", 0)
    
    # Continue probing if low confidence and not too many iterations
    if low_conf and iteration < 5:
        return "probe"
    return "assessment"


def route_after_probe(state: MBPState) -> Literal["end"]:
    """After probe, return to user"""
    return "end"


def route_after_output(state: MBPState) -> Literal["end"]:
    """After output, complete"""
    return "end"


# ============ GRAPH BUILDER ============

def create_mbp_graph():
    """Create and return the MBP LangGraph"""
    
    # Build graph
    builder = StateGraph(MBPState)
    
    # Add nodes
    builder.add_node("intake", intake_node)
    builder.add_node("extraction", extraction_node)
    builder.add_node("synthesis", synthesis_node)
    builder.add_node("contextualizer", contextualizer_node)
    builder.add_node("hypothesis", hypothesis_node)
    builder.add_node("validation", validation_node)
    builder.add_node("probe", probe_node)
    builder.add_node("assessment", assessment_node)
    builder.add_node("output", output_node)
    
    # Add edges
    builder.add_edge(START, "intake")
    builder.add_conditional_edges("intake", route_after_intake, {
        "extraction": "extraction",
        "end": END
    })
    builder.add_edge("extraction", "synthesis")
    builder.add_edge("synthesis", "contextualizer")
    builder.add_edge("contextualizer", "hypothesis")
    builder.add_edge("hypothesis", "validation")
    builder.add_conditional_edges("validation", route_after_validation, {
        "probe": "probe",
        "assessment": "assessment"
    })
    builder.add_edge("probe", END)  # Return to user
    builder.add_edge("assessment", "output")
    builder.add_edge("output", END)
    
    # Compile with memory saver
    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)
    
    return graph


# Global graph instance
_mbp_graph = None

def get_mbp_graph():
    """Get or create MBP graph singleton"""
    global _mbp_graph
    if _mbp_graph is None:
        _mbp_graph = create_mbp_graph()
    return _mbp_graph


# ============ MAIN ENTRY POINT ============

async def run_mbp_v2(session_id: str, user_response: str, messages: list) -> MBPState:
    """
    Main entry point for MBP v2.0
    
    Args:
        session_id: Unique session identifier
        user_response: Current user message
        messages: Full conversation history
    
    Returns:
        Final state with next_question or final_profile
    """
    # Create initial state
    state = create_initial_state(session_id, user_response, messages)
    
    # Get graph
    graph = get_mbp_graph()
    
    # Run graph
    config = {"configurable": {"thread_id": session_id}}
    
    print(f"\n{'='*60}")
    print(f"🧠 MBP v2.0 - Session {session_id}")
    print(f"{'='*60}")
    
    async for event in graph.astream(state, config):
        for node_name, node_state in event.items():
            if node_name == END:
                break
            # State updates happen automatically
    
    # Get final state
    final_state = graph.get_state(config).values
    
    print(f"\n{'='*60}")
    print(f"✅ Complete - Phase: {final_state.get('current_phase')}")
    print(f"{'='*60}")
    
    return final_state
