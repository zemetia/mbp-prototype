"""
MBP v2.0 - Parallel Extraction Runner
Runs all 4 extractors in parallel
"""
import asyncio
from typing import Dict, Any
from graph.state import MBPState

from agents.extractors.linguistic import LinguisticExtractor
from agents.extractors.emotional import EmotionalExtractor
from agents.extractors.cognitive import CognitiveExtractor
from agents.extractors.behavioral import BehavioralExtractor


# Singleton instances
_linguistic = LinguisticExtractor()
_emotional = EmotionalExtractor()
_cognitive = CognitiveExtractor()
_behavioral = BehavioralExtractor()


async def run_extraction_layer(state: MBPState) -> Dict[str, Any]:
    """
    Run all 4 extractors in parallel
    Returns combined extracted_signals dict
    """
    print("[Extraction Layer] Running 4 extractors in parallel...")
    
    # Run all extractors concurrently
    results = await asyncio.gather(
        _linguistic.execute(state),
        _emotional.execute(state),
        _cognitive.execute(state),
        _behavioral.execute(state),
        return_exceptions=True
    )
    
    # Process results
    extracted_signals = {}
    errors = []
    
    extractors = [
        ("linguistic", results[0]),
        ("emotional", results[1]),
        ("cognitive", results[2]),
        ("behavioral", results[3])
    ]
    
    for name, result in extractors:
        if isinstance(result, Exception):
            print(f"  ❌ {name}_extractor failed: {result}")
            errors.append(f"{name}: {str(result)}")
            extracted_signals[name] = {}
        elif result.success:
            print(f"  ✅ {name}_extractor: {len(result.data.get('patterns', []))} patterns")
            extracted_signals[name] = result.data
        else:
            print(f"  ⚠️ {name}_extractor: {result.error}")
            extracted_signals[name] = {}
    
    return {
        "extracted_signals": extracted_signals,
        "extraction_errors": errors if errors else None
    }
