"""
MBP v2.0 - Linguistic Extractor Agent
Extracts linguistic patterns from transcript
"""
import json
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage

from agents.base import MBPAgent
from graph.state import MBPState
from core.config import MBPConfig


class LinguisticExtractor(MBPAgent):
    """Extracts linguistic markers and patterns"""
    
    def __init__(self):
        super().__init__("linguistic_extractor", temperature=0.2)
    
    SYSTEM_PROMPT = """You are the Linguistic Extractor for MirrorBreak Protocol.

Extract ONLY linguistic patterns from the user's response:
1. Absolutes (always, never, must, should)
2. Qualifiers (sometimes, maybe, kind of, tends to)
3. Evasion markers (vague responses, topic shifts, deflections)
4. Temporal references (past, present, future focus)
5. Meta-talk (talking about talking)

Focus on HOW they say things, not WHAT they say.

OUTPUT (JSON):
{
    "absolutes": ["word1", "word2"],
    "qualifiers": ["word1", "word2"],
    "evasion_markers": ["phrase1"],
    "temporal_references": [{"word": "dulu", "tense": "past"}],
    "meta_talk": ["phrase1"],
    "patterns": [
        {
            "type": "absolute_language|cautious|evasive|reflective",
            "evidence": "quoted text",
            "confidence": 0-100
        }
    ]
}"""
    
    def _prepare_input(self, state: MBPState) -> str:
        """Prepare input for LLM"""
        current = state.get("current_response", "")
        
        # Truncate if too long
        if len(current) > MBPConfig.MAX_MESSAGE_LENGTH * 2:
            current = current[:MBPConfig.MAX_MESSAGE_LENGTH * 2] + "..."
        
        return current
    
    def _parse_output(self, content: str) -> Dict[str, Any]:
        """Parse LLM output to structured data"""
        try:
            # Extract JSON from response
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = content[start:end]
                return json.loads(json_str)
            return {"error": "No JSON found"}
        except json.JSONDecodeError as e:
            return {"error": f"JSON parse error: {e}"}
    
    async def process(self, state: MBPState) -> Dict[str, Any]:
        """Extract linguistic patterns"""
        user_input = self._prepare_input(state)
        
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"Extract linguistic patterns from:\n\n{user_input}")
        ]
        
        response = await self.llm.ainvoke(messages)
        result = self._parse_output(response.content)
        
        # Ensure required fields
        return {
            "absolutes": result.get("absolutes", []),
            "qualifiers": result.get("qualifiers", []),
            "evasion_markers": result.get("evasion_markers", []),
            "temporal_references": result.get("temporal_references", []),
            "meta_talk": result.get("meta_talk", []),
            "patterns": result.get("patterns", [])[:MBPConfig.MAX_SIGNALS_PER_TYPE],
            "confidence": result.get("confidence", 70)
        }
