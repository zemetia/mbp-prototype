"""
MBP Utility Functions
Helper functions for JSON parsing, error handling, and timing
"""
import json
from datetime import datetime
from typing import Any, Dict, Optional


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()


def safe_json_parse(content: str, fallback: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Safely parse JSON content with fallback
    
    Args:
        content: String content to parse
        fallback: Default value if parsing fails
        
    Returns:
        Parsed dict or fallback value
    """
    if fallback is None:
        fallback = {}
    
    try:
        # Handle markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"[JSON Parse Error] {e}")
        return fallback
    except Exception as e:
        print(f"[JSON Parse Error] {e}")
        return fallback


def log_phase_transition(session_id: str, from_phase: str, to_phase: str, 
                         iteration: int, timestamp: str = None) -> None:
    """
    Log phase transition for debugging
    
    Args:
        session_id: Session identifier
        from_phase: Previous phase
        to_phase: New phase
        iteration: Current iteration count
        timestamp: Optional timestamp override
    """
    ts = timestamp or get_current_timestamp()
    print(f"[{ts}] [Phase Transition] Session {session_id}: {from_phase} -> {to_phase} (iteration {iteration})")


def log_node_execution(session_id: str, node_name: str, phase: str,
                       execution_time_ms: float = None, error: str = None) -> None:
    """
    Log node execution for debugging
    
    Args:
        session_id: Session identifier
        node_name: Name of the node being executed
        phase: Current phase
        execution_time_ms: Execution time in milliseconds
        error: Optional error message
    """
    timestamp = get_current_timestamp()
    
    if error:
        print(f"[{timestamp}] [Node Error] Session {session_id} | {node_name} | Phase: {phase} | Error: {error}")
    elif execution_time_ms:
        print(f"[{timestamp}] [Node Complete] Session {session_id} | {node_name} | Phase: {phase} | Time: {execution_time_ms:.2f}ms")
    else:
        print(f"[{timestamp}] [Node Start] Session {session_id} | {node_name} | Phase: {phase}")


def format_timing_context(state: Dict[str, Any]) -> Dict[str, str]:
    """
    Format timing metadata for prompts
    
    Args:
        state: Current MBP state
        
    Returns:
        Dict with timing context strings
    """
    return {
        "timestamp": get_current_timestamp(),
        "response_timestamp": state.get("response_timestamp", "unknown"),
        "phase_start_time": state.get("phase_start_time", get_current_timestamp())
    }


def calculate_execution_time(start_time: datetime) -> float:
    """
    Calculate execution time in milliseconds
    
    Args:
        start_time: Start datetime
        
    Returns:
        Execution time in milliseconds
    """
    return (datetime.now() - start_time).total_seconds() * 1000


class NodeExecutionTimer:
    """Context manager for timing node execution"""
    
    def __init__(self, session_id: str, node_name: str, phase: str, state: Dict[str, Any]):
        self.session_id = session_id
        self.node_name = node_name
        self.phase = phase
        self.state = state
        self.start_time = None
        
    def __enter__(self):
        self.start_time = datetime.now()
        log_node_execution(self.session_id, self.node_name, self.phase)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = calculate_execution_time(self.start_time)
        
        # Update state with execution time
        if "node_execution_times" not in self.state:
            self.state["node_execution_times"] = {}
        self.state["node_execution_times"][self.node_name] = execution_time
        
        if exc_val:
            log_node_execution(self.session_id, self.node_name, self.phase, 
                             error=str(exc_val))
        else:
            log_node_execution(self.session_id, self.node_name, self.phase, 
                             execution_time_ms=execution_time)
        
        return False  # Don't suppress exceptions
