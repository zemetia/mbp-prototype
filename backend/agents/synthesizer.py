import os
import json
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# Kimi 2.5 via Moonshot AI using LangChain
llm = ChatOpenAI(
    model="kimi-k2.5",
    api_key=os.getenv("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.cn/v1",
    temperature=0.4
)

class SynthesizerAgent:
    """Agent 6: Generate final structural profile"""
    
    SYSTEM_PROMPT = """You are the Synthesizer Agent for MBP.

ROLE: Generate final structural profile dari semua data.

OUTPUT FORMAT (JSON):
{
    "core_fear": {
        "primary": "main adaptive fear",
        "secondary": "supporting fear",
        "confidence": 0-100,
        "evidence": ["supporting quotes"]
    },
    "core_drive": {
        "primary": "main motivation",
        "secondary": "supporting drive",
        "confidence": 0-100
    },
    "defense_mechanism": {
        "dominant": "primary defense",
        "secondary": "backup defense",
        "sophistication": "primitive|intermediate|mature"
    },
    "structural_summary": "1-paragraph synthesis",
    "12d_matrix": {
        "AB": {"score": 0-100, "confidence": 0-100},
        "EG": {"score": 0-100, "confidence": 0-100},
        "VB": {"score": 0-100, "confidence": 0-100}
    },
    "persona_core_gap": {
        "claimed_identity": "how they see themselves",
        "operating_structure": "observed patterns",
        "gap_description": "the distance between them"
    },
    "adaptation_to_potential": {
        "survival_pattern": "how they adapted",
        "converted_strength": "potential from that adaptation",
        "activation_condition": "when strength emerges"
    },
    "integration_assessment": {
        "type": "A|B|C",
        "description": "Type A: Multiplicity/IFS parts | Type B: Compartmentalization | Type C: Context-Dependent",
        "coherence_level": "high|moderate|low"
    },
    "key_contradictions": [
        {
            "dimensions": ["dim1", "dim2"],
            "explanation": "what this tension reveals"
        }
    ],
    "overall_confidence": 0-100,
    "core_summary": "Bahasa Indonesia: paragraph ringkasan untuk user"
}

SYNTHESIS PRINCIPLES:
- Netral, deskriptif, non-pathologizing
- Confidence = uncertainty dalam interpretasi
- Contradictions adalah finding, bukan error
- Focus pada pattern, bukan label
- Adaptation = valid survival response
- Potential emerges dari wound structure"""

    async def synthesize(self, messages: List[Dict], hypotheses: List[Dict], user_feedback: Optional[str] = None) -> Dict[str, Any]:
        """Generate final structural profile"""
        # Extract key data
        user_responses = [m for m in messages if m["role"] == "user"]
        
        prompt = f"""Synthesize final structural profile dari data berikut.

User Responses:
{json.dumps(user_responses[-15:], indent=2)}

Hypotheses:
{json.dumps(hypotheses, indent=2)}

User Feedback (resonance check):
{user_feedback or "No additional feedback"}

Generate comprehensive profile dalam Bahasa Indonesia untuk core_summary.
"""
        
        try:
            response = await llm.ainvoke([
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ])
            result = json.loads(response.content)
            
            # Ensure core_summary exists
            if not result.get("core_summary"):
                result["core_summary"] = self._generate_summary_fallback(result)
            
            return result
        except Exception as e:
            print(f"Synthesis error: {e}")
            return self._fallback_profile()
    
    def _generate_summary_fallback(self, profile: Dict) -> str:
        """Generate simple summary if LLM fails"""
        core_fear = profile.get("core_fear", {}).get("primary", "fear of disconnection")
        core_drive = profile.get("core_drive", {}).get("primary", "need for security")
        defense = profile.get("defense_mechanism", {}).get("dominant", "intellectualization")
        
        return f"Struktur adaptasi yang terlihat menunjukkan pattern survival yang berkembang dari {core_fear}. Drive utama adalah {core_drive}, dengan {defense} sebagai mekanisme pertahanan utama. Pattern ini valid sebagai respons terhadap tekanan pembentuk, dan membawa potensi strength ketika diaktifkan dengan sadar."
    
    def _fallback_profile(self) -> Dict[str, Any]:
        """Fallback profile if synthesis fails"""
        return {
            "core_fear": {"primary": "requires more data", "confidence": 20},
            "core_drive": {"primary": "requires more data", "confidence": 20},
            "defense_mechanism": {"dominant": "insufficient evidence"},
            "structural_summary": "Insufficient data for reliable synthesis.",
            "overall_confidence": 20,
            "core_summary": "Data belum cukup untuk generate profile yang reliable. Rekomendasi: ulangi assessment dengan lebih banyak probing."
        }
