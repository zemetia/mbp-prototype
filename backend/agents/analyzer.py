import os
import json
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# Kimi 2.5 via Moonshot AI using LangChain
llm = ChatOpenAI(
    model="kimi-k2.5",
    api_key=os.getenv("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1",
    temperature=0.3
)

class AnalyzerAgent:
    """Agent 1: Analyze user responses for patterns, markers, and safety indicators"""
    
    SYSTEM_PROMPT = """You are the Analyzer Agent for MirrorBreak Protocol (MBP).

ROLE: Analyze user responses untuk detect:
1. Linguistic patterns (absolute language, qualifiers, evasion)
2. Emotional markers (affect, granularity, regulation)
3. Structural indicators (cognitive style, defense hints)
4. Safety red flags (crisis indicators, contraindications)

OUTPUT FORMAT (JSON):
{
    "linguistic_patterns": {
        "absolutes": ["selalu", "tidak pernah", "pasti"],
        "qualifiers": ["mungkin", "kadang", "tergantung"],
        "evasion_markers": ["itu biasa aja", "nggak penting"],
        "flat_affect": boolean
    },
    "emotional_indicators": {
        "granularity": "low|medium|high",
        "regulation_style": "suppress|express|redirect",
        "vulnerability_level": 0-100,
        "defensive_response": boolean
    },
    "cognitive_markers": {
        "abstraction_level": "concrete|mixed|abstract",
        "causal_depth": "surface|moderate|deep",
        "rigidity": "fluid|mixed|rigid"
    },
    "safety_assessment": {
        "crisis_indicators": ["suicidality", "self_harm", "psychosis"],
        "distress_level": "low|moderate|high|crisis",
        "safe_to_proceed": boolean
    },
    "key_insights": ["insight 1", "insight 2"]
}

PRINCIPLES:
- Netral, deskriptif, tidak judgmental
- Confidence rendah = butuh data lebih
- Contradictions adalah data, bukan error"""

    async def analyze(self, content: str, history: List[Dict]) -> Dict[str, Any]:
        """Analyze a user response in context"""
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"History: {json.dumps(history[-5:])}\n\nAnalyze this response: {content}")
        ]
        
        try:
            response = await llm.ainvoke(messages)
            return json.loads(response.content)
        except Exception as e:
            print(f"Analyzer error: {e}")
            return {"error": str(e), "safe_to_proceed": True}
    
    async def analyze_safety(self, content: str, history: List[Dict]) -> Dict[str, Any]:
        """Specialized safety analysis for Phase 0"""
        safety_prompt = """You are the Safety Analyzer for MBP Phase 0.

CRITICAL: Detect crisis indicators that require IMMEDIATE HALT.

RED FLAGS (halt protocol):
- Active suicidality with plan/intent
- Recent self-harm
- Psychotic symptoms (delusions, hallucinations)
- Severe dissociation

YELLOW FLAGS (proceed with caution):
- Moderate depression
- History of trauma (stable)
- Recent stress but coping

OUTPUT (JSON):
{
    "crisis_detected": boolean,
    "crisis_type": null | "suicidality" | "psychosis" | "severe_dissociation",
    "distress_level": "low|moderate|high|crisis",
    "safety_cleared": boolean,
    "recommendation": "proceed|caution|halt",
    "reasoning": "explanation"
}"""
        
        messages = [
            SystemMessage(content=safety_prompt),
            HumanMessage(content=f"Response to analyze: {content}")
        ]
        
        try:
            response = await llm.ainvoke(messages)
            return json.loads(response.content)
        except Exception as e:
            print(f"Safety analysis error: {e}")
            return {"safety_cleared": True, "crisis_detected": False}
    
    async def extract_patterns(self, content: str, history: List[Dict]) -> List[Dict]:
        """Extract adaptation patterns from Phase 3 mining"""
        pattern_prompt = """Extract adaptation patterns from this mining response.

Look for:
- Origin moments (when pattern first developed)
- Survival function (what threat it protected against)
- Cost/sacrifice (what they gave up)
- Current triggers (when pattern activates)

OUTPUT (JSON):
{
    "patterns": [
        {
            "pattern_name": "e.g., Emotional Suppression",
            "origin_hint": "when it started",
            "survival_function": "what it protected",
            "current_cost": "what they sacrifice",
            "confidence": 0-100
        }
    ]
}"""
        
        messages = [
            SystemMessage(content=pattern_prompt),
            HumanMessage(content=f"Response: {content}")
        ]
        
        try:
            response = await llm.ainvoke(messages)
            result = json.loads(response.content)
            return result.get("patterns", [])
        except Exception as e:
            print(f"Pattern extraction error: {e}")
            return []
