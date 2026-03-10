"""
MBP v2.0 - Validation Layer
Evidence evaluation, contradiction detection, gap analysis
"""
import json
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage

from agents.base import MBPAgent
from graph.state import MBPState, Hypothesis
from core.config import MBPConfig


class EvidenceEvaluator(MBPAgent):
    """Evaluates evidence and updates hypothesis confidences"""
    
    def __init__(self):
        super().__init__("evidence_evaluator", temperature=0.3)
    
    SYSTEM_PROMPT = """You are the Evidence Evaluator for MBP.

Evaluate how new evidence affects existing hypotheses.
Use Bayesian-style updating:
- Increase confidence for supporting evidence
- Decrease confidence for contradicting evidence
- Consider alternative explanations

OUTPUT (JSON):
{
    "updated_hypotheses": [
        {
            "id": "hyp_id",
            "previous_confidence": 0.0-1.0,
            "current_confidence": 0.0-1.0,
            "confidence_change": -1.0 to 1.0,
            "supporting_evidence": ["ev1", "ev2"],
            "contradicting_evidence": ["ev3"],
            "status": "leading|competing|rejected"
        }
    ],
    "evidence_registry": [
        {"evidence": "...", "supports": ["hyp1"], "contradicts": ["hyp2"]}
    ]
}"""
    
    def _format_hypotheses(self, hypotheses: Dict[str, List[Hypothesis]]) -> str:
        """Format all hypotheses for evaluation"""
        lines = ["CURRENT HYPOTHESES:"]
        
        for field, hyps in hypotheses.items():
            lines.append(f"\n{field.upper()}:")
            for h in hyps:
                lines.append(f"  - {h.get('id')}: {h.get('description', '')[:80]}... (conf: {h.get('confidence', 0)})")
        
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
        """Evaluate hypotheses against evidence"""
        hypotheses = state.get("hypotheses", {})
        current_response = state.get("current_response", "")
        
        hyps_text = self._format_hypotheses(hypotheses)
        
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"{hyps_text}\n\nNEW EVIDENCE:\n{current_response[:200]}")
        ]
        
        response = await self.llm.ainvoke(messages)
        result = self._parse_output(response.content)
        
        return {
            "updated_hypotheses": result.get("updated_hypotheses", []),
            "evidence_registry": result.get("evidence_registry", [])
        }


class ContradictionDetector(MBPAgent):
    """Detects contradictions between hypotheses and evidence"""
    
    def __init__(self):
        super().__init__("contradiction_detector", temperature=0.2)
    
    SYSTEM_PROMPT = """You are the Contradiction Detector for MBP.

Find logical contradictions between:
1. Different hypotheses (cross-field tensions)
2. Hypotheses and new evidence
3. Patterns that cannot both be true

OUTPUT (JSON):
{
    "contradictions": [
        {
            "id": "con_1",
            "description": "what contradicts what",
            "elements": ["hyp1", "hyp2"],
            "severity": "strong|moderate|subtle",
            "explanation": "why this is a contradiction"
        }
    ],
    "tension_pairs": [
        {
            "dimensions": ["field1", "field2"],
            "tension_type": "claim_vs_behavior|past_vs_present|stated_vs_actual"
        }
    ]
}"""
    
    async def process(self, state: MBPState) -> Dict[str, Any]:
        """Detect contradictions in current state"""
        # Simplified version - just analyze existing hypotheses
        hypotheses = state.get("hypotheses", {})
        
        # For now, return empty contradictions (full implementation would need LLM)
        return {
            "contradictions": [],
            "tension_pairs": []
        }


class GapAnalyzer(MBPAgent):
    """Analyzes confidence gaps to determine what needs probing"""
    
    def __init__(self):
        super().__init__("gap_analyzer", temperature=0.2)
    
    def _calculate_field_confidence(self, hypotheses: List[Hypothesis]) -> float:
        """Calculate average confidence for a field"""
        if not hypotheses:
            return 0.0
        return sum(h.get("confidence", 0) for h in hypotheses) / len(hypotheses)
    
    async def process(self, state: MBPState) -> Dict[str, Any]:
        """Identify low-confidence fields that need probing"""
        hypotheses = state.get("hypotheses", {})
        threshold = MBPConfig.CONFIDENCE_THRESHOLD_PROCEED
        
        field_confidences = {}
        low_confidence_fields = []
        
        for field, hyps in hypotheses.items():
            conf = self._calculate_field_confidence(hyps)
            field_confidences[field] = conf
            
            if conf < threshold:
                low_confidence_fields.append({
                    "field": field,
                    "current_confidence": conf,
                    "gap": threshold - conf
                })
        
        # Sort by gap size (largest first)
        low_confidence_fields.sort(key=lambda x: x["gap"], reverse=True)
        
        # Check overall confidence
        all_confs = list(field_confidences.values())
        overall_confidence = sum(all_confs) / len(all_confs) if all_confs else 0.0
        
        return {
            "field_confidences": field_confidences,
            "low_confidence_fields": low_confidence_fields,
            "overall_confidence": overall_confidence,
            "should_continue_probing": len(low_confidence_fields) > 0 and state.get("iteration_count", 0) < 5
        }
