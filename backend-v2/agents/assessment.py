"""
MBP v2.0 - Assessment Layer
12D Matrix positioning and validation
"""
import json
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from agents.base import MBPAgent
from graph.state import MBPState


class TensionMapper(MBPAgent):
    """Maps tensions between 12D dimensions"""
    
    def __init__(self):
        super().__init__("tension_mapper", temperature=0.3)
    
    SYSTEM_PROMPT = """You are the Tension Mapper for MirrorBreak Protocol.

Identify tensions (contradictions) between 12D dimensions.

KEY TENSION PAIRS:
- AB x Stress Response: Claimed analytical vs somatic freeze
- EG x VB: High granularity + low bandwidth = emotional trap
- RS x ARP: High sensitivity + dominant response = compensation
- ASC x Emotional Structure: Legitimacy test for glorification

OUTPUT (JSON):
{
    "tensions": [
        {
            "pair": ["dimension1", "dimension2"],
            "tension_type": "cognitive_somatic_split|awareness_expression_gap",
            "description": "what this tension reveals",
            "severity": "strong|moderate|subtle",
            "persona_core_indicator": "what gap this exposes"
        }
    ],
    "persona_core_gaps": [
        {
            "claimed": "persona presentation",
            "core": "underlying structure",
            "gap": "difference between them"
        }
    ]
}"""
    
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
        """Map tensions across dimensions"""
        hypotheses = state.get("hypotheses", {})
        contradictions = state.get("contradictions", [])
        
        # Format for LLM
        lines = ["HYPOTHESES BY FIELD:"]
        for field, hyps in hypotheses.items():
            for h in hyps[:2]:  # Top 2 per field
                lines.append(f"  {field}: {h.get('description', '')[:60]}...")
        
        text = "\n".join(lines)
        
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"Map tensions from:\n\n{text}")
        ]
        
        response = await self.llm.ainvoke(messages)
        result = self._parse_output(response.content)
        
        return {
            "tensions": result.get("tensions", []),
            "persona_core_gaps": result.get("persona_core_gaps", [])
        }


class MatrixPositioner(MBPAgent):
    """Generates 12D matrix position estimates"""
    
    def __init__(self):
        super().__init__("matrix_positioner", temperature=0.2)
    
    SYSTEM_PROMPT = """You are the Matrix Positioner for MirrorBreak Protocol.

Generate position estimates (0-100) for all 12D dimensions.

0-100 = Ordinal positioning, NOT interval measurement.

12D DIMENSIONS:

Cognitive Domain:
- AB (Abstraction Bandwidth): Concrete (0) to Abstract (100)
- CDI (Causal Depth): Surface (0) to Systemic (100)  
- CRF (Cognitive Rigidity): Binary (0) to Fluid (100)
- Processing_Style: Intuitive (0) to Analytical (100)

Emotional Domain:
- EG (Emotional Granularity): Low (0) to High (100)
- RSI (Regulation Strategy): Suppress (0) to Express (100)
- VB (Vulnerability Bandwidth): Closed (0) to Open (100)
- Stress_Response: Freeze (0) to Fight/Flight (100)

Relational Domain:
- ARP (Authority Response): Rebellious (0) to Dominant (100)
- RS (Recognition Sensitivity): Low (0) to High (100)
- COI (Control Orientation): External (0) to Internal (100)

Adaptive Domain:
- ASC (Adaptive Strength): Compensated (0) to Integrated (100)

OUTPUT (JSON):
{
    "matrix_12d": {
        "AB": {"score": 0-100, "confidence": 0-100, "evidence": ["quote"]},
        "CDI": {"score": 0-100, "confidence": 0-100, "evidence": ["quote"]},
        "CRF": {"score": 0-100, "confidence": 0-100, "evidence": ["quote"]},
        "Processing_Style": {"score": 0-100, "confidence": 0-100, "evidence": ["quote"]},
        "EG": {"score": 0-100, "confidence": 0-100, "evidence": ["quote"]},
        "RSI": {"score": 0-100, "confidence": 0-100, "evidence": ["quote"]},
        "VB": {"score": 0-100, "confidence": 0-100, "evidence": ["quote"]},
        "Stress_Response": {"score": 0-100, "confidence": 0-100, "evidence": ["quote"]},
        "ARP": {"score": 0-100, "confidence": 0-100, "evidence": ["quote"]},
        "RS": {"score": 0-100, "confidence": 0-100, "evidence": ["quote"]},
        "COI": {"score": 0-100, "confidence": 0-100, "evidence": ["quote"]},
        "ASC": {"score": 0-100, "confidence": 0-100, "evidence": ["quote"]}
    }
}"""
    
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
        """Generate 12D matrix positions"""
        hypotheses = state.get("hypotheses", {})
        patterns = state.get("unified_patterns", [])
        
        # Format input
        lines = ["HYPOTHESES:"]
        for field, hyps in hypotheses.items():
            leading = [h for h in hyps if h.get("confidence", 0) > 0.5]
            if leading:
                lines.append(f"\n{field}:")
                for h in leading[:2]:
                    lines.append(f"  - {h.get('description', '')[:80]}")
        
        lines.append("\nPATTERNS:")
        for p in patterns[:3]:
            lines.append(f"  - {p.get('pattern_name', 'unnamed')}")
        
        text = "\n".join(lines)
        
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"Generate 12D matrix from:\n\n{text}")
        ]
        
        response = await self.llm.ainvoke(messages)
        result = self._parse_output(response.content)
        
        return {
            "matrix_12d": result.get("matrix_12d", {})
        }


class Validator(MBPAgent):
    """Quality check for final assessment"""
    
    def __init__(self):
        super().__init__("validator", temperature=0.1)
    
    async def process(self, state: MBPState) -> Dict[str, Any]:
        """Validate assessment quality"""
        matrix = state.get("matrix_12d", {})
        
        # Simple validation: check we have all 12 dimensions
        required_dims = ["AB", "CDI", "CRF", "Processing_Style", "EG", "RSI", 
                        "VB", "Stress_Response", "ARP", "RS", "COI", "ASC"]
        
        missing = [d for d in required_dims if d not in matrix]
        
        # Calculate average confidence
        confidences = []
        for dim_data in matrix.values():
            if isinstance(dim_data, dict):
                confidences.append(dim_data.get("confidence", 0))
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        quality_score = avg_confidence * 0.8 + (len(matrix) / 12) * 20
        
        return {
            "quality_score": quality_score,
            "missing_dimensions": missing,
            "average_confidence": avg_confidence,
            "quality_rating": "high" if quality_score > 80 else "medium" if quality_score > 60 else "low",
            "validation_passed": len(missing) == 0 and avg_confidence > 50
        }
