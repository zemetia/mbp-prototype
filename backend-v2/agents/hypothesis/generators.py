"""
MBP v2.0 - Hypothesis Generators (Per Field)
5 parallel hypothesis generators for different psychological domains
"""
import json
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage

from agents.base import MBPAgent
from graph.state import MBPState
from core.config import MBPConfig


class BaseHypothesisGenerator(MBPAgent):
    """Base class for field-specific hypothesis generators"""
    
    def __init__(self, field: str, temperature: float = 0.7):
        super().__init__(f"hgen_{field}", temperature=temperature)
        self.field = field
    
    def _get_system_prompt(self) -> str:
        """Override in subclasses"""
        raise NotImplementedError
    
    def _format_patterns(self, state: MBPState) -> str:
        """Format patterns for LLM input"""
        patterns = state.get("contextualized_patterns", [])
        themes = state.get("dominant_themes", [])
        
        lines = ["UNIFIED PATTERNS:"]
        for p in patterns[:5]:  # Limit to top 5
            lines.append(f"  - {p.get('pattern_name', 'unnamed')}: {p.get('description', '')[:100]}")
        
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
        """Generate hypotheses for this field"""
        patterns_text = self._format_patterns(state)
        
        messages = [
            SystemMessage(content=self._get_system_prompt()),
            HumanMessage(content=f"Generate {self.field} hypotheses from:\n\n{patterns_text}")
        ]
        
        response = await self.llm.ainvoke(messages)
        result = self._parse_output(response.content)
        
        return {
            "field": self.field,
            "hypotheses": result.get("hypotheses", [])[:MBPConfig.MAX_HYPOTHESES_PER_FIELD]
        }


class HGenAttachment(BaseHypothesisGenerator):
    """Generate attachment-related hypotheses"""
    
    def __init__(self):
        super().__init__("attachment")
    
    def _get_system_prompt(self) -> str:
        return """You are the Attachment Hypothesis Generator for MBP.

Generate 3-5 competing hypotheses about attachment patterns.

Consider:
- Anxious (fear of abandonment, need for reassurance)
- Avoidant (fear of intimacy, defensive independence)
- Disorganized (inconsistent, approach-avoidance)
- Secure (comfortable with closeness and independence)

OUTPUT (JSON):
{
    "hypotheses": [
        {
            "id": "hyp_1",
            "description": "specific attachment pattern claim",
            "confidence": 0.0-1.0,
            "evidence": ["supporting signals"],
            "testable_prediction": "what would confirm this"
        }
    ]
}"""


class HGenCognitive(BaseHypothesisGenerator):
    """Generate cognitive structure hypotheses"""
    
    def __init__(self):
        super().__init__("cognitive")
    
    def _get_system_prompt(self) -> str:
        return """You are the Cognitive Structure Hypothesis Generator for MBP.

Generate 3-5 competing hypotheses about cognitive processing style.

Consider:
- Abstraction level (concrete vs abstract thinking)
- Causal depth (surface vs systemic understanding)
- Cognitive rigidity (binary vs fluid thinking)
- Processing style (intuitive vs analytical)

OUTPUT (JSON):
{
    "hypotheses": [
        {
            "id": "hyp_1",
            "description": "specific cognitive pattern claim",
            "confidence": 0.0-1.0,
            "evidence": ["supporting signals"],
            "testable_prediction": "what would confirm this"
        }
    ]
}"""


class HGenEmotional(BaseHypothesisGenerator):
    """Generate emotional architecture hypotheses"""
    
    def __init__(self):
        super().__init__("emotional")
    
    def _get_system_prompt(self) -> str:
        return """You are the Emotional Architecture Hypothesis Generator for MBP.

Generate 3-5 competing hypotheses about emotional patterns.

Consider:
- Emotional granularity (range of emotions recognized)
- Regulation strategy (suppress vs express)
- Vulnerability bandwidth (comfort with openness)
- Stress response pattern

OUTPUT (JSON):
{
    "hypotheses": [
        {
            "id": "hyp_1",
            "description": "specific emotional pattern claim",
            "confidence": 0.0-1.0,
            "evidence": ["supporting signals"],
            "testable_prediction": "what would confirm this"
        }
    ]
}"""


class HGenRelational(BaseHypothesisGenerator):
    """Generate power dynamics & relational hypotheses"""
    
    def __init__(self):
        super().__init__("relational")
    
    def _get_system_prompt(self) -> str:
        return """You are the Relational Dynamics Hypothesis Generator for MBP.

Generate 3-5 competing hypotheses about power dynamics and relationships.

Consider:
- Authority response (submissive vs dominant)
- Recognition sensitivity (need for validation)
- Control orientation (internal vs external locus)
- Power dynamics in relationships

OUTPUT (JSON):
{
    "hypotheses": [
        {
            "id": "hyp_1",
            "description": "specific relational pattern claim",
            "confidence": 0.0-1.0,
            "evidence": ["supporting signals"],
            "testable_prediction": "what would confirm this"
        }
    ]
}"""


class HGenDefense(BaseHypothesisGenerator):
    """Generate defense mechanism hypotheses"""
    
    def __init__(self):
        super().__init__("defense")
    
    def _get_system_prompt(self) -> str:
        return """You are the Defense Mechanism Hypothesis Generator for MBP.

Generate 3-5 competing hypotheses about defense patterns.

Consider:
- Intellectualization (thinking to avoid feeling)
- Suppression (conscious inhibition)
- Projection (attributing to others)
- Rationalization (justifying with logic)
- Perfectionism (control through standards)

OUTPUT (JSON):
{
    "hypotheses": [
        {
            "id": "hyp_1",
            "description": "specific defense pattern claim",
            "confidence": 0.0-1.0,
            "evidence": ["supporting signals"],
            "testable_prediction": "what would confirm this"
        }
    ]
}"""
