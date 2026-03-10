"""
Unit tests for extraction layer agents
"""
import pytest
import asyncio
import sys
import os

sys.path.insert(0, '/mnt/d/Yoel/projects/mbp-prototype/backend-v2')

from agents.extractors.linguistic import LinguisticExtractor
from agents.extractors.emotional import EmotionalExtractor
from agents.extractors.cognitive import CognitiveExtractor
from agents.extractors.behavioral import BehavioralExtractor
from graph.state import create_initial_state


@pytest.mark.asyncio
async def test_linguistic_extractor():
    """Test linguistic pattern extraction"""
    agent = LinguisticExtractor()
    state = create_initial_state(
        "test-001",
        "Saya selalu merasa harus sempurna dan kadang-kadang cemas.",
        [{"role": "user", "content": "test"}]
    )
    
    result = await agent.execute(state)
    
    assert result.success
    assert "patterns" in result.data
    assert isinstance(result.data["absolutes"], list)
    print(f"✅ LinguisticExtractor: {len(result.data['patterns'])} patterns found")


@pytest.mark.asyncio
async def test_emotional_extractor():
    """Test emotional pattern extraction"""
    agent = EmotionalExtractor()
    state = create_initial_state(
        "test-002",
        "Saya merasa sangat cemas dan kadang sedih.",
        [{"role": "user", "content": "test"}]
    )
    
    result = await agent.execute(state)
    
    assert result.success
    assert "explicit_affects" in result.data
    print(f"✅ EmotionalExtractor: {len(result.data['explicit_affects'])} affects found")


@pytest.mark.asyncio
async def test_cognitive_extractor():
    """Test cognitive pattern extraction"""
    agent = CognitiveExtractor()
    state = create_initial_state(
        "test-003",
        "Saya suka menganalisis masalah secara sistematis dan mencari pola.",
        [{"role": "user", "content": "test"}]
    )
    
    result = await agent.execute(state)
    
    assert result.success
    assert "abstraction_level" in result.data
    print(f"✅ CognitiveExtractor: abstraction={result.data['abstraction_level']['score']}")


@pytest.mark.asyncio
async def test_behavioral_extractor():
    """Test behavioral pattern extraction"""
    agent = BehavioralExtractor()
    state = create_initial_state(
        "test-004",
        "Hmm, ya, mungkin saya bisa cerita...",
        [{"role": "user", "content": "test"}]
    )
    
    result = await agent.execute(state)
    
    assert result.success
    assert "engagement_quality" in result.data
    print(f"✅ BehavioralExtractor: engagement={result.data['engagement_quality']['level']}")


if __name__ == "__main__":
    print("Running Extractor Tests...")
    asyncio.run(test_linguistic_extractor())
    asyncio.run(test_emotional_extractor())
    asyncio.run(test_cognitive_extractor())
    asyncio.run(test_behavioral_extractor())
    print("\n✅ All extractor tests passed!")