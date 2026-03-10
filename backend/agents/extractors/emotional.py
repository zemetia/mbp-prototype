"""
MBP v2.0 - Emotional Extractor Agent
Extracts emotional markers and patterns
"""
import json
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from agents.base import MBPAgent
from graph.state import MBPState
from core.config import MBPConfig


class EmotionalExtractor(MBPAgent):
    """Extracts emotional markers and granularity"""
    
    def __init__(self):
        super().__init__("emotional_extractor", temperature=0.2)
    
    SYSTEM_PROMPT = """You are the Emotional Extractor for MirrorBreak Protocol.

Extract ONLY emotional patterns from the user's response:
1. Explicit affects (named emotions: sad, angry, anxious, happy)
2. Implicit emotions (indirect emotional expressions)
3. Granularity indicators (simple vs nuanced emotional vocabulary)
4. Regulation attempts (suppression, expression, redirection)
5. Vulnerability displays (moments of openness)

Focus on emotional content and expression style.

OUTPUT (JSON):
{
    "explicit_affects": [
        {"emotion": "anxious", "evidence": "quote", "intensity": 0-100}
    ],
    "implicit_emotions": [
        {"emotion": "fear", "evidence": "quote", "confidence": 0-100}
    ],
    "granularity_indicators": {
        "level": "low|medium|high",
        "evidence": ["simple word", "nuanced phrase"]
    },
    "regulation_attempts": [
        {"type": "suppress|express|redirect", "evidence": "quote"}
    ],
    "vulnerability_displays": [
        {"content": "what was shared", "context": "surrounding text"}
    ],
    "patterns": [
        {
            "type": "emotional_awareness|regulation_style|vulnerability",
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
            HumanMessage(content=f"Extract emotional patterns from:\n\n{user_input}")
        ]
        
        response = await self.llm.ainvoke(messages)
        result = self._parse_output(response.content)
        
        return {
            "explicit_affects": result.get("explicit_affects", []),
            "implicit_emotions": result.get("implicit_emotions", []),
            "granularity_indicators": result.get("granularity_indicators", {}),
            "regulation_attempts": result.get("regulation_attempts", []),
            "vulnerability_displays": result.get("vulnerability_displays", []),
            "patterns": result.get("patterns", [])[:MBPConfig.MAX_SIGNALS_PER_TYPE]
        }
