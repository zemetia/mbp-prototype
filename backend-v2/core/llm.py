"""
MBP v2.0 - LLM Configuration
"""
import os
from typing import Optional
from langchain_openai import ChatOpenAI
from core.config import MBPConfig

_llm_cache = {}

def get_llm(model: Optional[str] = None, temperature: Optional[float] = None) -> ChatOpenAI:
    """Get LLM instance with caching"""
    model = model or MBPConfig.DEFAULT_MODEL
    
    # Temperature based on mode
    if temperature is None:
        if MBPConfig.MODE.value == "fast":
            temperature = 0.3
        elif MBPConfig.MODE.value == "accuracy":
            temperature = 0.1
        else:
            temperature = 0.2
    
    cache_key = f"{model}_{temperature}"
    
    if cache_key not in _llm_cache:
        _llm_cache[cache_key] = ChatOpenAI(
            model=model,
            api_key=MBPConfig.API_KEY,
            base_url=MBPConfig.BASE_URL,
            temperature=temperature
        )
    
    return _llm_cache[cache_key]
