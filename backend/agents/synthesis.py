"""
MBP v2.0 - Synthesis Layer
Combines signals from extractors into unified patterns
"""
import json
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage

from agents.base import MBPAgent
from graph.state import MBPState


class PatternSynthesizer(MBPAgent):
    """Merges signals from all extractors into unified patterns"""
    
    def __init__(self):
        super().__init__("pattern_synthesizer", temperature=0.3)
    
    SYSTEM_PROMPT = """You are the Pattern Synthesizer for MirrorBreak Protocol.

Merge signals from multiple extractors into unified cross-domain patterns.

Look for:
1. Cross-domain correlations (e.g., linguistic absolutes + emotional suppression)
2. Consistent themes across signal types
3. Contradictions between different signal domains
4. Dominant patterns that explain multiple signals

INPUT: Signals from linguistic, emotional, cognitive, and behavioral extractors

OUTPUT (JSON):
{
    "unified_patterns": [
        {
            "pattern_name": "descriptive name",
            "description": "what this pattern represents",
            "supporting_signals": ["linguistic:absolutes", "emotional:suppression"],
            "confidence": 0-100,
            "cross_domain": true
        }
    ],
    "cross_correlations": [
        {
            "domains": ["linguistic", "emotional"],
            "correlation_type": "reinforcing|contradictory",
            "description": "how they relate"
        }
    ],
    "dominant_themes": ["theme1", "theme2"],
    "pattern_confidences": {
        "theme1": 85,
        "theme2": 72
    }
}"""
    
    def _format_signals(self, state: MBPState) -> str:
        """Format all extracted signals for LLM"""
        signals = state.get("extracted_signals", {})
        
        sections = []
        
        # Linguistic
        ling = signals.get("linguistic", {})
        sections.append("LINGUISTIC SIGNALS:")
        sections.append(f"  Absolutes: {ling.get('absolutes', [])}")
        sections.append(f"  Qualifiers: {ling.get('qualifiers', [])}")
        sections.append(f"  Patterns: {[p.get('type') for p in ling.get('patterns', [])]}")
        
        # Emotional
        emo = signals.get("emotional", {})
        sections.append("\nEMOTIONAL SIGNALS:")
        affects = emo.get("explicit_affects", [])
        sections.append(f"  Explicit: {[a.get('emotion') for a in affects]}")
        reg = emo.get("regulation_attempts", [])
        sections.append(f"  Regulation: {[r.get('type') for r in reg]}")
        
        # Cognitive
        cog = signals.get("cognitive", {})
        sections.append("\nCOGNITIVE SIGNALS:")
        ab = cog.get("abstraction_level", {})
        sections.append(f"  Abstraction: {ab.get('score', 50)}")
        ca = cog.get("causal_complexity", {})
        sections.append(f"  Causal depth: {ca.get('score', 50)}")
        
        # Behavioral
        beh = signals.get("behavioral", {})
        sections.append("\nBEHAVIORAL SIGNALS:")
        eq = beh.get("engagement_quality", {})
        sections.append(f"  Engagement: {eq.get('level', 'medium')}")
        sections.append(f"  Elaboration: {beh.get('elaboration_style', 'moderate')}")
        
        return "\n".join(sections)
    
    def _parse_output(self, content: str) -> Dict[str, Any]:
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
            return {"error": "No JSON found"}
        except json.JSONDecodeError:
            return {"error": "JSON parse error"}
    
    async def process(self, state: MBPState) -> Dict[str, Any]:
        """Synthesize patterns from all signals"""
        signals_text = self._format_signals(state)
        
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"Synthesize these signals:\n\n{signals_text}")
        ]
        
        response = await self.llm.ainvoke(messages)
        result = self._parse_output(response.content)
        
        return {
            "unified_patterns": result.get("unified_patterns", []),
            "cross_correlations": result.get("cross_correlations", []),
            "dominant_themes": result.get("dominant_themes", []),
            "pattern_confidences": result.get("pattern_confidences", {})
        }
