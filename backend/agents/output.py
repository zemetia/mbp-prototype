"""
MBP v2.0 - Output Layer
Profile composition and user-facing report generation
"""
import json
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from agents.base import MBPAgent
from graph.state import MBPState


class ProfileComposer(MBPAgent):
    """Composes final structural profile"""
    
    def __init__(self):
        super().__init__("profile_composer", temperature=0.4)
    
    SYSTEM_PROMPT = """You are the Profile Composer for MirrorBreak Protocol.

Integrate all assessment data into a coherent structural profile.

OUTPUT FORMAT (JSON):
{
    "core_structure": {
        "core_fear": {
            "primary": {"type": "...", "confidence": 0-100},
            "secondary": {"type": "...", "confidence": 0-100}
        },
        "core_drive": {
            "primary": {"type": "...", "confidence": 0-100},
            "secondary": {"type": "...", "confidence": 0-100}
        },
        "defense_mechanism": {
            "primary": "...",
            "secondary": "...",
            "automation_level": 1-5
        }
    },
    "persona_core_gap": {
        "persona_description": "how they present",
        "core_description": "underlying structure", 
        "gap_description": "the difference",
        "consequences": ["..."]
    },
    "adaptation_patterns": [
        {
            "pattern": "...",
            "origin": "...",
            "cost": "...",
            "latent_strength": "..."
        }
    ],
    "structural_summary": "2-3 paragraph synthesis"
}"""
    
    def _format_input(self, state: MBPState) -> str:
        """Format all data for profile composition"""
        matrix = state.get("matrix_12d", {})
        tensions = state.get("tensions", [])
        hypotheses = state.get("hypotheses", {})
        
        lines = ["12D MATRIX:"]
        for dim, data in matrix.items():
            if isinstance(data, dict):
                lines.append(f"  {dim}: {data.get('score', 50)} (conf: {data.get('confidence', 0)})")
        
        lines.append("\nTENSIONS:")
        for t in tensions[:3]:
            lines.append(f"  - {t.get('description', 'tension')[:60]}...")
        
        lines.append("\nLEADING HYPOTHESES:")
        for field, hyps in hypotheses.items():
            top = [h for h in hyps if h.get("confidence", 0) > 0.5]
            if top:
                lines.append(f"  {field}: {top[0].get('description', '')[:60]}...")
        
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
        """Compose final profile"""
        input_text = self._format_input(state)
        
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"Compose profile from:\n\n{input_text}")
        ]
        
        response = await self.llm.ainvoke(messages)
        result = self._parse_output(response.content)
        
        return {
            "final_profile": result
        }


class Explainer(MBPAgent):
    """Generates user-friendly explanation"""
    
    def __init__(self):
        super().__init__("explainer", temperature=0.5)
    
    SYSTEM_PROMPT = """You are the Explainer for MirrorBreak Protocol.

Create a user-friendly report in Indonesian (Bahasa Indonesia).

OUTPUT FORMAT (JSON):
{
    "executive_summary": "1 paragraph ringkasan utama dalam Bahasa Indonesia",
    "core_insights": [
        "insight 1 dalam Bahasa Indonesia",
        "insight 2 dalam Bahasa Indonesia"
    ],
    "adaptation_to_strengths": [
        {"adaptation": "...", "strength": "...", "context": "..."}
    ],
    "growth_suggestions": [
        {"area": "...", "suggestion": "...", "rationale": "..."}
    ],
    "user_report": {
        "title": "Profil Struktural Anda",
        "introduction": "...",
        "sections": [...]
    }
}

Style:
- Warm but not overly positive
- Specific, not generic
- Acknowledges complexity
- No judgment language"""
    
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
        """Generate user-friendly explanation"""
        profile = state.get("final_profile", {})
        matrix = state.get("matrix_12d", {})
        
        # Format simplified input
        core = profile.get("core_structure", {})
        fear = core.get("core_fear", {}).get("primary", {}).get("type", "unknown")
        drive = core.get("core_drive", {}).get("primary", {}).get("type", "unknown")
        
        input_text = f"""PROFILE DATA:
Core Fear: {fear}
Core Drive: {drive}
Defense: {core.get("defense_mechanism", {}).get("primary", "unknown")}

PERSONA-CORE GAP:
{profile.get("persona_core_gap", {}).get("gap_description", "")[:200]}
"""
        
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"Generate user report from:\n\n{input_text}")
        ]
        
        response = await self.llm.ainvoke(messages)
        result = self._parse_output(response.content)
        
        return {
            "user_report": result.get("user_report", {}),
            "executive_summary": result.get("executive_summary", ""),
            "core_insights": result.get("core_insights", []),
            "adaptation_to_strengths": result.get("adaptation_to_strengths", []),
            "growth_suggestions": result.get("growth_suggestions", [])
        }
