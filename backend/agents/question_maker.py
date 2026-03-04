import os
import json
from typing import List, Dict, Any
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=os.getenv("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1"
)

MODEL = "kimi-k2.5"

class QuestionMakerAgent:
    """Agent 3: Generate adaptive questions to test hypotheses"""
    
    SYSTEM_PROMPT = """You are the QuestionMaker Agent for MBP.

ROLE: Generate questions untuk stress-test hypotheses dan expose 12D tensions.

QUESTION TYPES:
1. Somatic-Cognitive Split: Test analytical claim vs bodily response
2. Temporal Contradiction: Test consistency over time
3. Context Switch: Test compartmentalization
4. Values-Action Gap: Test stated vs actual priorities
5. Presupposition Challenge: Test rigidity

STYLE RULES:
- Conversational Indonesian
- Curious, not interrogative
- Open-ended (bukan yes/no)
- Natural follow-up feel
- Avoid: "Mengapa", "Apakah", "Rate 1-10"

OUTPUT FORMAT (JSON):
{
    "question": "the generated question",
    "target_hypothesis": "which hypothesis this tests",
    "tension_target": "which 12D tension this exposes",
    "expected_evidence": "what response would support/refute",
    "question_type": "somatic|temporal|context|values|presupposition"
}

FORBIDDEN:
- Leading questions
- Judgmental framing
- "Kamu pasti..." statements
- Too abstract ("how do you feel about life")"""

    async def generate(self, hypotheses: List[Dict], messages: List[Dict]) -> str:
        """Generate next adaptive question"""
        # Sort by confidence, test strongest first
        sorted_hypotheses = sorted(hypotheses, key=lambda h: h.get("confidence", 0), reverse=True)
        target = sorted_hypotheses[0] if sorted_hypotheses else None
        
        prompt = f"""Generate a question untuk test this hypothesis:

Target Hypothesis:
{json.dumps(target, indent=2) if target else "Explore general structure"}

Context (last 3 messages):
{json.dumps(messages[-3:], indent=2)}

Generate ONE natural follow-up question dalam Bahasa Indonesia.
"""
        
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.6
            )
            result = json.loads(response.choices[0].message.content)
            return result.get("question", "Ceritain lebih banyak tentang itu.")
        except Exception as e:
            print(f"Question generation error: {e}")
            return "Bisa elaborate lebih dalam tentang yang tadi?"
    
    async def generate_mining_question(self, pattern: Dict, messages: List[Dict]) -> str:
        """Generate Phase 3 adaptation mining question"""
        prompt = f"""Generate an adaptation mining question untuk explore this pattern:

Pattern: {json.dumps(pattern, indent=2)}

Mining focus:
- Origin (when did it start?)
- Survival function (what threat?)
- Current cost (what's sacrificed?)

Generate ONE question dalam Bahasa Indonesia.
Safety: Focus on pattern, bukan trauma details.
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
            return result.get("question", "Kapan pertama kali kamu notice pattern ini?")
        except Exception as e:
            print(f"Mining question error: {e}")
            return "Kapan pertama kali kamu notice pattern ini?"
    
    async def generate_cross_validation_question(self, tension_pair: str, messages: List[Dict]) -> str:
        """Generate Phase 4 cross-validation question"""
        prompt = f"""Generate a cross-validation question untuk test this tension:

Tension Pair: {tension_pair}

Use "Innocent Mirror" technique:
- Point out contradiction gently
- Invite explanation, bukan confrontation
- Frame sebagai nuance, bukan inconsistency

Generate ONE question dalam Bahasa Indonesia.
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
            return result.get("question", "Menarik... bisa help me understand the nuance?")
        except Exception as e:
            print(f"Cross-validation question error: {e}")
            return "Menarik... bisa help me understand the nuance?"
