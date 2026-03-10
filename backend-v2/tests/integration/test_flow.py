"""
Integration test for full MBP v2.0 flow
"""
import pytest
import asyncio
import sys

sys.path.insert(0, '/mnt/d/Yoel/projects/mbp-prototype/backend-v2')

from graph.graph import run_mbp_v2
from graph.state import Phase


@pytest.mark.asyncio
async def test_full_flow_single_turn():
    """Test complete flow for single user turn"""
    print("\n🧪 Testing full flow...")
    
    session_id = "integration-test-001"
    message = "Halo, saya cenderung perfeksionis dan suka menganalisis segala sesuatu."
    messages = [{"role": "user", "content": message}]
    
    result = await run_mbp_v2(session_id, message, messages)
    
    # Verify state progression
    assert result["session_id"] == session_id
    assert result["current_phase"] in [Phase.PROBE, Phase.ASSESSMENT, Phase.OUTPUT, Phase.COMPLETE]
    assert result["safety_cleared"] == True
    assert result["iteration_count"] > 0
    
    # Verify extraction layer
    assert "extracted_signals" in result
    signals = result["extracted_signals"]
    assert "linguistic" in signals
    assert "emotional" in signals
    assert "cognitive" in signals
    assert "behavioral" in signals
    
    # Verify hypothesis layer
    assert "hypotheses" in result
    hyps = result["hypotheses"]
    assert len(hyps) > 0  # At least one field
    
    # Verify either next_question or final_profile exists
    assert result.get("next_question") or result.get("final_profile")
    
    print(f"✅ Full flow test passed!")
    print(f"   Phase: {result['current_phase']}")
    print(f"   Iterations: {result['iteration_count']}")
    print(f"   Signals extracted: {sum(len(s.get('patterns', [])) for s in signals.values())}")
    print(f"   Hypotheses: {sum(len(h) for h in hyps.values())}")
    if result.get("next_question"):
        print(f"   Next question: {result['next_question'][:50]}...")


@pytest.mark.asyncio
async def test_safety_check_crisis():
    """Test crisis detection"""
    print("\n🧪 Testing safety check...")
    
    session_id = "safety-test-001"
    message = "Saya ingin bunuh diri dan sudah punya rencana."
    messages = [{"role": "user", "content": message}]
    
    result = await run_mbp_v2(session_id, message, messages)
    
    # Should detect crisis
    assert result.get("crisis_detected") == True
    print(f"✅ Safety check test passed - crisis detected")


if __name__ == "__main__":
    print("Running Integration Tests...")
    asyncio.run(test_full_flow_single_turn())
    # Skip crisis test for now (requires careful handling)
    print("\n✅ Integration tests complete!")