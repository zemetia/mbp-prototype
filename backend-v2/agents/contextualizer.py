"""
MBP v2.0 - Contextualizer Agent
Adds cultural and temporal context to patterns
"""
import json
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage

from agents.base import MBPAgent
from graph.state import MBPState


class Contextualizer(MBPAgent):
    """Adds cultural and temporal context to unified patterns"""
    
    def __init__(self):
        super().__init__("contextualizer", temperature=0.3)
    
    SYSTEM_PROMPT = """You are the Contextualizer for MirrorBreak Protocol.
    
    Add cultural and temporal context to detected patterns.
    
    Consider:
    1. Cultural context (Indonesian cultural norms, collectivism vs individualism)
    2. Temporal context (developmental stage, recent events)
    3. Situational context (work, family, stress factors)
    4. Language context (Bahasa Indonesia nuances, formality levels)
    
    For each pattern, provide:
    - Cultural adjustment notes
    - Temporal relevance
    - Contextual confidence modifier
    
    OUTPUT (JSON):
    {
        "contextualized_patterns": [
            {
                "pattern_name": "...",
                "original_description": "...",
                "cultural_context": "...",
                "temporal_context": "...",
                "adjusted_confidence": 0-100,
                "cultural_notes": ["..."]
            }
        ],
        "cultural_frame": {
            "primary_culture": "...",
            "collectivism_score": 0-100,
            "power_distance": "high|medium|low"
        }
    }"""
    
    def _format_patterns(self, state: MBPState) -> str:
        patterns = state.get("unified_patterns", [])
        themes = state.get("dominant_themes", [])
        
        lines = ["UNIFIED PATTERNS:"]
        for p in patterns:
            lines.append(f"  - {p.get('pattern_name')}: {p.get('description', '')[:100]}")
        
        lines.append(f"\nDOMINANT THEMES: {', '.join(themes)}")
        return "\n".join(lines)
    
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
        patterns_text = self._format_patterns(state)
        
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"Add context to:\n\n{patterns_text}")
        ]
        
        response = await self.llm.ainvoke(messages)
        result = self._parse_output(response.content)
        
        return {
            "contextualized_patterns": result.get("contextualized_patterns", []),
            "cultural_frame": result.get("cultural_frame", {})
        }
