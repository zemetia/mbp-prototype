"""
MBP v2.0 - Parallel Hypothesis Generation Runner
Runs all 5 hypothesis generators in parallel
"""
import asyncio
from typing import Dict, Any
from graph.state import MBPState

from agents.hypothesis.generators import (
    HGenAttachment,
    HGenCognitive,
    HGenEmotional,
    HGenRelational,
    HGenDefense
)


# Singleton instances
_attachment = HGenAttachment()
_cognitive = HGenCognitive()
_emotional = HGenEmotional()
_relational = HGenRelational()
_defense = HGenDefense()


async def run_hypothesis_layer(state: MBPState) -> Dict[str, Any]:
    """
    Run all 5 hypothesis generators in parallel
    Returns combined hypotheses dict organized by field
    """
    print("[Hypothesis Layer] Running 5 generators in parallel...")
    
    # Run all generators concurrently
    results = await asyncio.gather(
        _attachment.execute(state),
        _cognitive.execute(state),
        _emotional.execute(state),
        _relational.execute(state),
        _defense.execute(state),
        return_exceptions=True
    )
    
    # Process results
    hypotheses = {}
    errors = []
    
    generators = [
        ("attachment", results[0]),
        ("cognitive", results[1]),
        ("emotional", results[2]),
        ("relational", results[3]),
        ("defense", results[4])
    ]
    
    for name, result in generators:
        if isinstance(result, Exception):
            print(f"  ❌ hgen_{name} failed: {result}")
            errors.append(f"{name}: {str(result)}")
            hypotheses[name] = []
        elif result.success:
            hyps = result.data.get("hypotheses", [])
            print(f"  ✅ hgen_{name}: {len(hyps)} hypotheses")
            hypotheses[name] = hyps
        else:
            print(f"  ⚠️ hgen_{name}: {result.error}")
            hypotheses[name] = []
    
    return {
        "hypotheses": hypotheses,
        "hypothesis_errors": errors if errors else None
    }
