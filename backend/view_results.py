#!/usr/bin/env python3
"""
MBP Flow Result Viewer - Shows full JSON output from each phase
"""
import asyncio
import sys
import os
import json

sys.path.insert(0, '/mnt/d/Yoel/projects/mbp-prototype/backend')

# Read .env manually
with open('/mnt/d/Yoel/projects/mbp-prototype/backend/.env', 'r') as f:
    for line in f:
        if '=' in line and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

from graph import run_mbp_graph, create_mbp_graph
from state import MBPState, Phase
from utils import get_current_timestamp
from nodes import (
    safety_check_node, analyzer_node, hypothesis_maker_node,
    adaptation_mining_node, cross_validation_node, assessor_node,
    synthesizer_node, question_maker_node
)
from llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

async def test_individual_nodes():
    """Test each node individually to see JSON output"""
    print("=" * 70)
    print("🧠 MBP NODE OUTPUT VIEWER")
    print("=" * 70)
    
    # Initialize state
    session_id = "test-view-001"
    user_response = "Halo, saya ingin memulai assessment tentang diri saya. Saya cenderung memikirkan banyak hal sebelum bertindak dan kadang merasa cemas kalau semuanya nggak sempurna."
    
    state = MBPState(
        session_id=session_id,
        current_phase=Phase.SAFETY_CHECK,
        messages=[{"role": "user", "content": user_response}],
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
    
    # Test 1: Safety Check
    print("\n" + "=" * 70)
    print("🔒 PHASE 0: SAFETY CHECK")
    print("=" * 70)
    print(f"Input: {user_response[:60]}...")
    
    try:
        result_state = await safety_check_node(state, {})
        print(f"\n✅ Safety Cleared: {result_state.get('safety_cleared')}")
        print(f"📊 Safety Data:")
        print(json.dumps(result_state.get('safety_data', {}), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Analyzer
    print("\n" + "=" * 70)
    print("🔍 PHASE 1: ANALYZER")
    print("=" * 70)
    
    state['current_phase'] = Phase.CORE_QUESTIONING
    try:
        result_state = await analyzer_node(state, {})
        print(f"✅ Signals Extracted: {len(result_state.get('signals', []))}")
        print(f"📊 Signals:")
        for signal in result_state.get('signals', [])[:3]:
            print(f"  - {signal.get('type', 'unknown')}: {signal.get('subtype', 'N/A')} (confidence: {signal.get('confidence', 0)})")
        print(f"\nFull Signals JSON:")
        print(json.dumps(result_state.get('signals', []), indent=2, ensure_ascii=False)[:800] + "...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Hypothesis Maker
    print("\n" + "=" * 70)
    print("💡 PHASE 2: HYPOTHESIS MAKER")
    print("=" * 70)
    
    try:
        result_state = await hypothesis_maker_node(state, {})
        print(f"✅ Hypotheses Generated: {len(result_state.get('hypotheses', []))}")
        print(f"📊 Hypotheses:")
        for hyp in result_state.get('hypotheses', [])[:3]:
            print(f"  - {hyp.get('field', 'unknown')}: {hyp.get('hypothesis', 'N/A')[:50]}... (confidence: {hyp.get('confidence', 0)})")
        print(f"\nFull Hypotheses JSON:")
        print(json.dumps(result_state.get('hypotheses', []), indent=2, ensure_ascii=False)[:1000] + "...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Question Maker
    print("\n" + "=" * 70)
    print("❓ PHASE 3: QUESTION MAKER")
    print("=" * 70)
    
    try:
        result_state = await question_maker_node(state, {})
        print(f"✅ Question Generated:")
        print(f"  Q: {result_state.get('next_question', 'N/A')}")
        print(f"\nFull State Update:")
        print(json.dumps({
            "next_question": result_state.get('next_question'),
            "should_ask_question": result_state.get('should_ask_question')
        }, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ NODE TESTS COMPLETE")
    print("=" * 70)

async def test_full_flow():
    """Run full flow and capture result"""
    print("\n\n" + "=" * 70)
    print("🔄 FULL FLOW TEST (Single Turn)")
    print("=" * 70)
    
    session_id = "full-flow-test-001"
    message = "Halo, saya ingin memulai assessment. Saya cenderung perfeksionis dan suka menganalisis segala sesuatu sebelum bertindak. Di kantor, saya sering jadi orang yang memastikan semua detail beres tapi kadang sulit delegasi tugas ke orang lain."
    
    print(f"\n💬 User Input:")
    print(f"   {message}")
    print(f"\n⏳ Running flow (timeout 3 minutes)...")
    
    try:
        result = await asyncio.wait_for(
            run_mbp_graph(
                session_id=session_id,
                user_response=message,
                messages=[{"role": "user", "content": message}]
            ),
            timeout=180
        )
        
        print(f"\n📊 FULL RESULT JSON:")
        print("=" * 70)
        
        # Pretty print the full result
        output = {
            "session_id": result.get("session_id"),
            "phase": result.get("phase"),
            "safety_cleared": result.get("safety_cleared"),
            "overall_confidence": result.get("overall_confidence"),
            "next_question": result.get("next_question"),
            "signals_count": len(result.get("signals", [])),
            "hypotheses_count": len(result.get("hypotheses", [])),
            "adaptation_patterns_count": len(result.get("adaptation_patterns", [])),
            "tensions_detected_count": len(result.get("tensions_detected", [])),
            "matrix_12d": result.get("matrix_12d"),
            "final_profile": result.get("final_profile"),
            "error": result.get("error"),
            "node_execution_times": result.get("node_execution_times")
        }
        
        print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
        
        # Also save to file
        with open('/tmp/mbp_result.json', 'w') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n💾 Full result saved to: /tmp/mbp_result.json")
        
    except asyncio.TimeoutError:
        print("\n❌ Timeout after 3 minutes")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 MBP Result Viewer")
    print(f"API Key: {os.getenv('MOONSHOT_API_KEY', 'NOT SET')[:20]}...")
    
    # Run individual node tests
    asyncio.run(test_individual_nodes())
    
    # Uncomment to run full flow test (takes longer)
    # asyncio.run(test_full_flow())
