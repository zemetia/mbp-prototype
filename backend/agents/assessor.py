import os
import json
from typing import List, Dict, Any
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=os.getenv("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1"
)

MODEL = "kimi-k2.5"

class AssessorAgent:
    """Agent 4: Assess 12D Matrix scores with confidence intervals"""
    
    SYSTEM_PROMPT = """You are the Assessor Agent for MBP.

ROLE: Assess 12D Matrix positioning berdasarkan evidence.

⚠️ CRITICAL: 0-100 adalah ORDINAL POSITIONING, bukan interval measurement.
- 75 ≠ "75% of capacity"
- 75 = "higher than 70, lower than 80"
- Descriptors, bukan precise quantification

12D DIMENSIONS:

Domain Kognitif:
- AB (Abstraction Bandwidth): Concrete (0) ↔ Abstract (100)
- CDI (Causal Depth): Surface (0) ↔ Systemic (100)
- CRF (Cognitive Rigidity): Binary (0) ↔ Fluid (100)
- Processing_Style: Intuitive (0) ↔ Analytical (100)

Domain Emosional:
- EG (Emotional Granularity): Low (0) ↔ High (100)
- RSI (Regulation Strategy): Suppress (0) ↔ Express (100)
- VB (Vulnerability Bandwidth): Closed (0) ↔ Open (100)
- Stress_Response: Freeze (0) ↔ Fight/Flight (100)

Domain Relasional:
- ARP (Authority Response): Rebellious (0) ↔ Dominant (100)
- RS (Recognition Sensitivity): Low (0) ↔ High (100)
- COI (Control Orientation): External (0) ↔ Internal (100)
- ASC (Adaptive Strength): Compensated (0) ↔ Integrated (100)

OUTPUT FORMAT (JSON):
{
    "scores": {
        "AB": {
            "score": 0-100,
            "confidence": 0-100,
            "evidence": ["quote supporting this positioning"],
            "reasoning": "brief justification"
        }
    },
    "tensions_detected": [
        {
            "dimensions": ["AB", "Stress_Response"],
            "type": "somatic_cognitive_split",
            "magnitude": "strong|moderate|subtle"
        }
    ]
}

CONFIDENCE INTERPRETATION:
- 80-100%: Evidence padat, konsisten
- 60-79%: Evidence cukup, beberapa gaps
- 40-59%: Evidence terbatas, high uncertainty
- <40%: Insufficient data

PRINCIPLES:
- Confidence = uncertainty dalam INTERPRETASI, bukan validitas subjek
- Contradictions antara dimensi = persona crack exposed
- Cross-dimension tension adalah finding, bukan error"""

    async def assess_12d(self, content: str, messages: List[Dict]) -> Dict[str, Any]:
        """Assess 12D matrix scores from evidence"""
        # Gather all user responses
        user_responses = [m for m in messages if m["role"] == "user"]
        
        prompt = f"""Assess 12D Matrix scores berdasarkan evidence.

Responses to analyze:
{json.dumps(user_responses[-10:], indent=2)}

Current response:
{content}

Provide positioning (0-100) untuk setiap dimension dengan confidence interval.
"""
        
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            result = json.loads(response.choices[0].message.content)
            return result.get("scores", self._default_scores())
        except Exception as e:
            print(f"12D assessment error: {e}")
            return self._default_scores()
    
    async def assess_dimension(self, dimension: str, evidence: List[str]) -> Dict[str, Any]:
        """Assess single dimension with detailed reasoning"""
        dim_prompts = {
            "AB": "Assess Abstraction Bandwidth: Concrete (0) vs Abstract (100). Look for: use of metaphors, systems thinking, theoretical language.",
            "EG": "Assess Emotional Granularity: Low (0) vs High (100). Look for: emotion vocabulary precision, differentiation of states.",
            "VB": "Assess Vulnerability Bandwidth: Closed (0) vs Open (100). Look for: self-disclosure depth, admission of weakness."
        }
        
        prompt = dim_prompts.get(dimension, f"Assess {dimension} positioning (0-100)")
        
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": f"{prompt}\n\nEvidence: {json.dumps(evidence)}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"Dimension assessment error: {e}")
            return {"score": 50, "confidence": 40, "reasoning": "insufficient data"}
    
    def _default_scores(self) -> Dict[str, Any]:
        """Default scores when assessment fails"""
        dimensions = ["AB", "CDI", "CRF", "Processing_Style", "EG", "RSI", "VB", "Stress_Response", "ARP", "RS", "COI", "ASC"]
        return {
            dim: {
                "score": 50,
                "confidence": 30,
                "evidence": ["insufficient data for assessment"],
                "reasoning": "default due to assessment failure"
            }
            for dim in dimensions
        }
