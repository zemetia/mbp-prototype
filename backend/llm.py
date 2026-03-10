"""
MBP LLM Configuration
Kimi/Moonshot LLM Setup
"""
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


_llm = None

def get_llm():
    """Lazy load LLM"""
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model="kimi-k2.5",
            api_key=os.getenv("MOONSHOT_API_KEY"),
            base_url="https://api.moonshot.ai/v1"
        )
    return _llm


# Usage: from llm import get_llm
# Then call get_llm() when needed
