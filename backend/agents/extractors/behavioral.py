"""
MBP v2.0 - Behavioral Extractor Agent
Extracts behavioral and engagement cues
"""
import json
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from agents.base import MBPAgent
from graph.state import MBPState
from core.config import MBPConfig


class BehavioralExtractor(MBPAgent):
    """Extracts behavioral cues and engagement patterns"""
    
    def __init__(self):
        super().__init__("behavioral_extractor", temperature=0.2)
    
    SYSTEM_PROMPT = """You are the Behavioral Extractor for MirrorBreak Protocol.

Extract ONLY behavioral/engagement patterns from the user's response:
1. Engagement patterns (depth of response, elaboration)
2. Avoidance indicators (vague answers, topic shifts)
3. Response latency indicators (hesitation markers)
4. Deflection tactics (humor, intellectualization, redirection)
5. Elaboration style (minimal, moderate, detailed)

Focus on engagement quality and defensive behaviors.

OUTPUT (JSON):
{
    "engagement_quality": {
        "level": "low|medium|high",
        "evidence": "description of response depth"
    },
    "avoidance_indicators": [
        {"type": "vague|topic_shift|deflection", "evidence": "quote"}
    ],
    "hesitation_markers": [
        {"marker": "word/phrase", "context": "surrounding text"}
    ],
    "deflection_tactics": [
        {"tactic": "humor|intellectualization|minimization", "evidence": "quote"}
    ],
    "elaboration_style": "minimal|moderate|detailed|excessive",
    "patterns": [
        {
            "type": "engagement|avoidance|defense",
            "evidence": "quoted text",
            "confidence": 0-100
        }
    ]
}"""
    
    def _prepare_input(self, state: MBPState) -> str:
        current = state.get("current_response", "")
        if len(current) > MBPConfig.MAX_MESSAGE_LENGTH * 2:
            current = current[:MBPConfig.MAX_MESSAGE_LENGTH * 2] + "..."
        return current
    
    def _parse_output(self, content: str) -> Dict[str, Any]:
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
            return {"error": "No JSON found"}
        except json.JSONDecodeError as e:
            return {"error": f"JSON parse error: {e}"}
    
    async def process(self, state: MBPState) -> Dict[str, Any]:
        user_input = self._prepare_input(state)
        
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"Extract behavioral patterns from:\n\n{user_input}")
        ]
        
        response = await self.llm.ainvoke(messages)
        result = self._parse_output(response.content)
        
        return {
            "engagement_quality": result.get("engagement_quality", {"level": "medium", "evidence": ""}),
            "avoidance_indicators": result.get("avoidance_indicators", []),
            "hesitation_markers": result.get("hesitation_markers", []),
            "deflection_tactics": result.get("deflection_tactics", []),
            "elaboration_style": result.get("elaboration_style", "moderate"),
            "patterns": result.get("patterns", [])[:MBPConfig.MAX_SIGNALS_PER_TYPE]
        }
