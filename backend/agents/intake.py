"""
MBP v2.0 - Intake Agent
Safety screening and initial context gathering
"""
import json
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from agents.base import MBPAgent
from graph.state import MBPState
from core.config import MBPConfig


class IntakeAgent(MBPAgent):
    """Initial safety check and session setup"""
    
    def __init__(self):
        super().__init__("intake", temperature=0.1)
    
    CRISIS_KEYWORDS = [
        "bunuh diri", "mau mati", "ingin mati", "tidak ingin hidup",
        "self harm", "luka diri", "depresi berat", "tidak ada harapan",
        "sekarat", "overdosis", "terluka", "trauma berat"
    ]
    
    SAFETY_PROMPT = """You are the Safety Analyzer for MBP Intake.

CRITICAL: Detect crisis indicators that require IMMEDIATE HALT.

RED FLAGS (halt protocol):
- Active suicidality with plan/intent
- Recent self-harm
- Psychotic symptoms
- Severe dissociation

OUTPUT (JSON):
{
    "crisis_detected": boolean,
    "crisis_type": null | "suicidality" | "self_harm" | "psychosis" | "severe_distress",
    "distress_level": "low|moderate|high|crisis",
    "safety_cleared": boolean,
    "recommendation": "proceed|caution|halt",
    "reasoning": "brief explanation"
}"""
    
    def _fast_safety_check(self, text: str) -> Dict[str, Any]:
        """Quick keyword-based safety check"""
        text_lower = text.lower()
        
        for keyword in self.CRISIS_KEYWORDS:
            if keyword in text_lower:
                return {
                    "crisis_detected": True,
                    "crisis_type": "potential_crisis",
                    "distress_level": "high",
                    "safety_cleared": False,
                    "recommendation": "caution",
                    "reasoning": f"Keyword detected: {keyword}"
                }
        
        return None  # No fast match, need LLM check
    
    def _parse_llm_output(self, content: str) -> Dict[str, Any]:
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
            return {"error": "No JSON found"}
        except json.JSONDecodeError:
            return {"error": "JSON parse error"}
    
    async def process(self, state: MBPState) -> Dict[str, Any]:
        """Run safety check"""
        user_input = state.get("current_response", "")
        
        # Fast check first (if enabled)
        if MBPConfig.FAST_SAFETY_CHECK:
            fast_result = self._fast_safety_check(user_input)
            if fast_result and fast_result["crisis_detected"]:
                return fast_result
        
        # LLM-based check
        messages = [
            SystemMessage(content=self.SAFETY_PROMPT),
            HumanMessage(content=f"Analyze safety of:\n\n{user_input}")
        ]
        
        response = await self.llm.ainvoke(messages)
        result = self._parse_llm_output(response.content)
        
        return {
            "crisis_detected": result.get("crisis_detected", False),
            "crisis_type": result.get("crisis_type"),
            "distress_level": result.get("distress_level", "low"),
            "safety_cleared": result.get("safety_cleared", True),
            "recommendation": result.get("recommendation", "proceed"),
            "reasoning": result.get("reasoning", "")
        }
