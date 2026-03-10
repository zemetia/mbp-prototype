"""
MBP v2.0 - Probe Layer
Question generation and selection
"""
import json
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage

from agents.base import MBPAgent
from graph.state import MBPState
from core.config import MBPConfig


class ProbeDesigner(MBPAgent):
    """Designs questions to test hypotheses and fill gaps"""
    
    def __init__(self):
        super().__init__("probe_designer", temperature=0.5)
    
    SYSTEM_PROMPT = """You are the Probe Designer for MirrorBreak Protocol.

Generate strategic questions to:
1. Test competing hypotheses
2. Fill information gaps
3. Expose tensions between dimensions
4. Challenge persona presentations

PROBE TYPES:
- Somatic: "How did your body react when..."
- Temporal: "Compare 5 years ago vs now..."
- Devil's Advocate: "Tell me about a time you didn't..."
- Forced Choice: "If you had to choose X or Y..."
- Surprise: "What do people most misunderstand..."

RULES:
- Conversational Indonesian
- Open-ended (not yes/no)
- Natural follow-up feel
- Target specific gaps

OUTPUT (JSON):
{
    "probes": [
        {
            "probe_id": "prb_1",
            "question": "the question text",
            "probe_type": "somatic|temporal|devil|forced|surprise",
            "target_field": "which field this tests",
            "target_hypotheses": ["hyp1", "hyp2"],
            "rationale": "why this question",
            "expected_signals": {
                "if_hyp1": ["signal1", "signal2"],
                "if_hyp2": ["signal3"]
            }
        }
    ]
}"""
    
    def _format_gaps(self, state: MBPState) -> str:
        """Format information gaps for LLM"""
        gaps = state.get("low_confidence_fields", [])
        hyps = state.get("hypotheses", {})
        
        lines = ["LOW CONFIDENCE FIELDS:"]
        for g in gaps[:3]:
            lines.append(f"  - {g['field']}: {g['current_confidence']:.2f} (gap: {g['gap']:.2f})")
        
        lines.append("\nLEADING HYPOTHESES:")
        for field, field_hyps in hyps.items():
            leading = [h for h in field_hyps if h.get("confidence", 0) > 0.5]
            if leading:
                lines.append(f"  {field}: {leading[0].get('description', '')[:60]}...")
        
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
        """Design probes for identified gaps"""
        gaps_text = self._format_gaps(state)
        
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"Design probes for:\n\n{gaps_text}")
        ]
        
        response = await self.llm.ainvoke(messages)
        result = self._parse_output(response.content)
        
        return {
            "candidate_probes": result.get("probes", [])
        }


class ProbeSelector(MBPAgent):
    """Selects optimal probe from candidates"""
    
    def __init__(self):
        super().__init__("probe_selector", temperature=0.3)
    
    async def process(self, state: MBPState) -> Dict[str, Any]:
        """Select best probe from candidates"""
        probes = state.get("candidate_probes", [])
        
        if not probes:
            # Fallback question
            return {
                "next_question": "Ceritakan lebih banyak tentang pola pikir dan perasaan Anda dalam situasi sulit.",
                "probe_rationale": "Fallback: general exploration",
                "selected_probe_id": "fallback"
            }
        
        # Simple selection: pick first high-quality probe
        # Full implementation would use LLM to rank
        selected = probes[0]
        
        return {
            "next_question": selected.get("question"),
            "probe_rationale": selected.get("rationale"),
            "selected_probe_id": selected.get("probe_id"),
            "target_field": selected.get("target_field"),
            "probe_type": selected.get("probe_type")
        }
