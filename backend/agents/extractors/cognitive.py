"""
MBP v2.0 - Cognitive Extractor Agent
Extracts cognitive processing patterns
"""
import json
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage

from agents.base import MBPAgent
from graph.state import MBPState
from core.config import MBPConfig


class CognitiveExtractor(MBPAgent):
    """Extracts cognitive processing style and patterns"""
    
    def __init__(self):
        super().__init__("cognitive_extractor", temperature=0.2)
    
    SYSTEM_PROMPT = """You are the Cognitive Extractor for MirrorBreak Protocol.

Extract ONLY cognitive patterns from the user's response:
1. Abstraction level (concrete details vs abstract concepts)
2. Causal complexity (surface correlations vs deep systemic thinking)
3. Processing speed indicators (quick judgments vs deliberation)
4. Cognitive biases (confirmation, binary thinking, etc.)
5. Problem-solving approach (analytical, intuitive, systematic)

Focus on HOW they think and process information.

OUTPUT (JSON):
{
    "abstraction_level": {
        "score": 0-100,
        "evidence": ["concrete phrase", "abstract phrase"]
    },
    "causal_complexity": {
        "score": 0-100,
        "evidence": ["surface explanation", "deep systemic view"]
    },
    "processing_indicators": [
        {"type": "quick|deliberate|systematic", "evidence": "quote"}
    ],
    "bias_patterns": [
        {"bias": "binary|confirmatory", "evidence": "quote"}
    ],
    "problem_solving_style": "analytical|intuitive|systematic|mixed",
    "patterns": [
        {
            "type": "abstraction|causal_depth|rigidity|processing_style",
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
            HumanMessage(content=f"Extract cognitive patterns from:\n\n{user_input}")
        ]
        
        response = await self.llm.ainvoke(messages)
        result = self._parse_output(response.content)
        
        return {
            "abstraction_level": result.get("abstraction_level", {"score": 50, "evidence": []}),
            "causal_complexity": result.get("causal_complexity", {"score": 50, "evidence": []}),
            "processing_indicators": result.get("processing_indicators", []),
            "bias_patterns": result.get("bias_patterns", []),
            "problem_solving_style": result.get("problem_solving_style", "mixed"),
            "patterns": result.get("patterns", [])[:MBPConfig.MAX_SIGNALS_PER_TYPE]
        }
