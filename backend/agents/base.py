"""
MBP v2.0 - Base Agent Class
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
from contextlib import contextmanager
import time

from core.llm import get_llm
from core.config import MBPConfig
from graph.state import MBPState


class AgentResult:
    """Standard result wrapper for all agents"""
    def __init__(self, success: bool, data: Dict[str, Any], error: str = None, execution_time: float = 0.0):
        self.success = success
        self.data = data
        self.error = error
        self.execution_time = execution_time
    
    @classmethod
    def success(cls, data: Dict[str, Any], execution_time: float = 0.0):
        return cls(True, data, None, execution_time)
    
    @classmethod
    def failure(cls, error: str, execution_time: float = 0.0):
        return cls(False, {}, error, execution_time)


class MBPAgent(ABC):
    """Base class for all MBP v2.0 agents"""
    
    def __init__(self, name: str, model: str = None, temperature: float = None):
        self.name = name
        self.model = model or MBPConfig.DEFAULT_MODEL
        self.temperature = temperature or 0.2
        self._llm = None
    
    @property
    def llm(self):
        """Lazy initialization of LLM - only create when needed"""
        if self._llm is None:
            self._llm = get_llm(self.model, self.temperature)
        return self._llm
    
    @abstractmethod
    async def process(self, state: MBPState) -> Dict[str, Any]:
        """Process state and return updates"""
        pass
    
    async def execute(self, state: MBPState) -> AgentResult:
        """Execute agent with timing and error handling"""
        start_time = time.time()
        
        try:
            result = await self.process(state)
            execution_time = time.time() - start_time
            
            # Log execution time to state
            if "node_execution_times" not in state:
                state["node_execution_times"] = {}
            state["node_execution_times"][self.name] = execution_time
            
            return AgentResult.success(result, execution_time)
            
        except Exception as e:
            execution_time = time.time() - start_time
            return AgentResult.failure(str(e), execution_time)


@contextmanager
def node_timer(state: MBPState, node_name: str):
    """Context manager for timing node execution"""
    start = time.time()
    yield
    elapsed = time.time() - start
    
    if "node_execution_times" not in state:
        state["node_execution_times"] = {}
    state["node_execution_times"][node_name] = elapsed
    
    print(f"[{node_name}] Completed in {elapsed:.2f}s")
