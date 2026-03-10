"""
Unit tests for hypothesis generation agents
"""
import pytest
import asyncio
import sys

sys.path.insert(0, '/mnt/d/Yoel/projects/mbp-prototype/backend-v2')

from agents.hypothesis.generators import (
    HGenAttachment, HGenCognitive, HGenEmotional,
    HGenRelational, HGenDefense
)
from graph.state import create_initial_state


@pytest.mark.asyncio
async def test_hgen_attachment():
    """Test attachment hypothesis generation"""
    agent = HGenAttachment()
    state = create_initial_state("test-001", "sample", [])
    state["contextualized_patterns"] = [
        {"pattern_name": "emotional_distance", "description": "avoids deep connection"}
    ]
    
    result = await agent.execute(state)
    
    assert result.success
    assert "hypotheses" in result.data
    assert len(result.data["hypotheses"]) > 0
    print(f"✅ HGenAttachment: {len(result.data['hypotheses'])} hypotheses")


@pytest.mark.asyncio
async def test_hgen_cognitive():
    """Test cognitive hypothesis generation"""
    agent = HGenCognitive()
    state = create_initial_state("test-002", "sample", [])
    state["contextualized_patterns"] = [
        {"pattern_name": "systematic_thinking", "description": "breaks down problems"}
    ]
    
    result = await agent.execute(state)
    
    assert result.success
    assert "hypotheses" in result.data
    print(f"✅ HGenCognitive: {len(result.data['hypotheses'])} hypotheses")


@pytest.mark.asyncio
async def test_hgen_emotional():
    """Test emotional hypothesis generation"""
    agent = HGenEmotional()
    state = create_initial_state("test-003", "sample", [])
    state["contextualized_patterns"] = [
        {"pattern_name": "suppressed_affect", "description": "minimizes emotions"}
    ]
    
    result = await agent.execute(state)
    
    assert result.success
    assert "hypotheses" in result.data
    print(f"✅ HGenEmotional: {len(result.data['hypotheses'])} hypotheses")


@pytest.mark.asyncio
async def test_hgen_relational():
    """Test relational hypothesis generation"""
    agent = HGenRelational()
    state = create_initial_state("test-004", "sample", [])
    state["contextualized_patterns"] = [
        {"pattern_name": "authority_avoidance", "description": "deflects control"}
    ]
    
    result = await agent.execute(state)
    
    assert result.success
    assert "hypotheses" in result.data
    print(f"✅ HGenRelational: {len(result.data['hypotheses'])} hypotheses")


@pytest.mark.asyncio
async def test_hgen_defense():
    """Test defense mechanism hypothesis generation"""
    agent = HGenDefense()
    state = create_initial_state("test-005", "sample", [])
    state["contextualized_patterns"] = [
        {"pattern_name": "intellectual_escape", "description": "thinks instead of feels"}
    ]
    
    result = await agent.execute(state)
    
    assert result.success
    assert "hypotheses" in result.data
    print(f"✅ HGenDefense: {len(result.data['hypotheses'])} hypotheses")


if __name__ == "__main__":
    print("Running Hypothesis Tests...")
    asyncio.run(test_hgen_attachment())
    asyncio.run(test_hgen_cognitive())
    asyncio.run(test_hgen_emotional())
    asyncio.run(test_hgen_relational())
    asyncio.run(test_hgen_defense())
    print("\n✅ All hypothesis tests passed!")