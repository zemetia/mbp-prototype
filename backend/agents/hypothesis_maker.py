import os
import json
from typing import List, Dict, Any
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=os.getenv("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1"
)

MODEL = "kimi-k2.5"

class HypothesisMakerAgent:
    """Agent 2: Generate competing hypotheses per field"""
    
    SYSTEM_PROMPT = """You are the HypothesisMaker Agent for MBP.

ROLE: Generate MULTIPLE competing hypotheses per field berdasarkan evidence.

FIELDS:
1. Attachment_Dynamics (avoidant, anxious, disorganized, secure)
2. Cognitive_Style (binary, fluid, compartmentalized)
3. Defense_Mechanism (suppression, projection, intellectualization, etc)
4. Core_Fear (abandonment, failure, engulfment, meaninglessness)
5. Power_Dynamics (submissive, dominant, strategic)
6. Emotional_Structure (granularity, regulation, expression)

OUTPUT FORMAT (JSON):
{
    "hypotheses": [
        {
            "field": "field_name",
            "hypothesis": "specific claim about subject",
            "confidence": 0.0-1.0,
            "evidence": ["quote 1", "behavioral marker"],
            "testable_prediction": "what would confirm/refute this"
        }
    ],
    "tensions": [
        "contradiction between H1 and H2"
    ],
    "priority_fields": ["field1", "field2"]
}

PRINCIPLES:
- Minimum 2-3 hypotheses per field
- Confidence = probability given current evidence
- Higher confidence = more specific prediction
- Contradictions are expected — they indicate multiplicity or compartmentalization"""

    async def generate(self, messages: List[Dict]) -> List[Dict[str, Any]]:
        """Generate initial hypotheses from Phase 1 data"""
        # Extract user responses
        user_responses = [m for m in messages if m["role"] == "user"]
        
        prompt = f"""Based on these responses, generate competing hypotheses per field.

Responses:
{json.dumps(user_responses[-5:], indent=2)}

Generate hypotheses untuk minimum 4 fields.
"""
        
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.5
            )
            result = json.loads(response.choices[0].message.content)
            return result.get("hypotheses", [])
        except Exception as e:
            print(f"Hypothesis generation error: {e}")
            return self._fallback_hypotheses()
    
    async def refine(self, hypotheses: List[Dict], new_content: str, messages: List[Dict]) -> List[Dict[str, Any]]:
        """Refine hypotheses based on new evidence"""
        prompt = f"""Refine these hypotheses based on new evidence.

Current Hypotheses:
{json.dumps(hypotheses, indent=2)}

New Response:
{new_content}

Update confidence scores and add evidence.
Remove falsified hypotheses (confidence < 0.2).
Generate new hypotheses if needed.
"""
        
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.4
            )
            result = json.loads(response.choices[0].message.content)
            return result.get("hypotheses", hypotheses)
        except Exception as e:
            print(f"Hypothesis refinement error: {e}")
            return hypotheses
    
    def _fallback_hypotheses(self) -> List[Dict]:
        """Generic hypotheses if generation fails"""
        return [
            {
                "field": "Attachment_Dynamics",
                "hypothesis": "Subject shows mixed attachment signals requiring more data",
                "confidence": 0.5,
                "evidence": ["insufficient data"]
            },
            {
                "field": "Defense_Mechanism",
                "hypothesis": "Likely intellectualization or suppression based on formal responses",
                "confidence": 0.4,
                "evidence": ["response style"]
            }
        ]
