"""
MBP v2.0 - Core Configuration
"""
import os
from enum import Enum
from typing import Optional


class AgentMode(Enum):
    FAST = "fast"
    BALANCED = "balanced"
    ACCURACY = "accuracy"


class MBPConfig:
    """Global configuration for MBP v2.0"""
    
    # LLM Configuration
    DEFAULT_MODEL = "kimi-k2.5"
    BASE_URL = "https://api.moonshot.ai/v1"
    API_KEY = os.getenv("MOONSHOT_API_KEY")
    
    # Performance Settings
    MODE = AgentMode.BALANCED
    
    # Caching
    CACHE_ENABLED = True
    CACHE_TTL_SECONDS = 300  # 5 minutes
    
    # Safety
    FAST_SAFETY_CHECK = True
    SAFETY_KEYWORDS = ["bunuh diri", "mati", "ingin mati", "sakit hati", "depresi berat"]
    
    # Token Limits
    MAX_HISTORY_MESSAGES = 10
    MAX_MESSAGE_LENGTH = 200
    MAX_SIGNALS_PER_TYPE = 10
    MAX_HYPOTHESES_PER_FIELD = 5
    
    # Confidence Thresholds
    CONFIDENCE_THRESHOLD_PROCEED = 0.7
    CONFIDENCE_THRESHOLD_COMPLETE = 0.85
    
    # Timing
    DEFAULT_TIMEOUT = 60
    
    @classmethod
    def set_mode(cls, mode: AgentMode):
        cls.MODE = mode
        if mode == AgentMode.FAST:
            cls.MAX_HISTORY_MESSAGES = 5
            cls.FAST_SAFETY_CHECK = True
        elif mode == AgentMode.ACCURACY:
            cls.MAX_HISTORY_MESSAGES = 15
            cls.FAST_SAFETY_CHECK = False


# Mode presets
def set_fast_mode():
    MBPConfig.set_mode(AgentMode.FAST)

def set_balanced_mode():
    MBPConfig.set_mode(AgentMode.BALANCED)

def set_accuracy_mode():
    MBPConfig.set_mode(AgentMode.ACCURACY)
