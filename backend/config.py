"""
MBP Configuration for Performance Tuning
"""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class MBPPerformanceConfig:
    """
    Configuration for MBP performance optimizations.
    
    Usage:
        config = MBPPerformanceConfig.fast_mode()
        # Or customize:
        config = MBPPerformanceConfig(
            enable_parallel_analysis=True,
            cache_ttl_seconds=600,
            max_signals_per_response=5
        )
    """
    
    # Parallel Execution
    enable_parallel_analysis: bool = True
    parallel_threshold_messages: int = 5  # Use parallel if messages < this
    
    # Caching
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    cache_max_size: int = 1000
    
    # Fast-path optimizations
    enable_fast_safety: bool = True
    fast_safety_min_length: int = 50  # Min chars for fast-path
    
    # Token reduction
    max_signals_per_response: int = 5
    max_hypotheses_active: int = 5
    max_patterns_active: int = 3
    max_history_messages: int = 10
    max_message_length: int = 200
    
    # Early exits
    skip_redundant_analysis: bool = True
    min_new_signals_for_analysis: int = 2
    
    # Streaming
    enable_streaming_questions: bool = True
    default_question_timeout: float = 2.0  # Seconds to wait for better question
    
    # Timing
    max_node_execution_time: float = 45.0  # Timeout per node
    max_total_execution_time: float = 120.0  # Timeout for entire graph
    
    @classmethod
    def fast_mode(cls) -> "MBPPerformanceConfig":
        """Aggressive optimization for speed"""
        return cls(
            enable_parallel_analysis=True,
            parallel_threshold_messages=8,
            enable_caching=True,
            cache_ttl_seconds=600,
            enable_fast_safety=True,
            max_signals_per_response=3,
            max_hypotheses_active=3,
            max_patterns_active=2,
            max_history_messages=5,
            max_message_length=150,
            skip_redundant_analysis=True,
            min_new_signals_for_analysis=3,
            enable_streaming_questions=True,
            default_question_timeout=1.5,
        )
    
    @classmethod
    def accuracy_mode(cls) -> "MBPPerformanceConfig":
        """Prioritize accuracy over speed"""
        return cls(
            enable_parallel_analysis=False,  # Sequential for thoroughness
            enable_caching=True,
            cache_ttl_seconds=300,
            enable_fast_safety=False,  # Always full safety check
            max_signals_per_response=10,
            max_hypotheses_active=8,
            max_patterns_active=5,
            max_history_messages=15,
            max_message_length=300,
            skip_redundant_analysis=False,
            enable_streaming_questions=False,
            default_question_timeout=5.0,
        )
    
    @classmethod
    def balanced_mode(cls) -> "MBPPerformanceConfig":
        """Balanced speed and accuracy (default)"""
        return cls()  # Uses default values


# Default configuration instance
_default_config = MBPPerformanceConfig.balanced_mode()


def get_config() -> MBPPerformanceConfig:
    """Get current configuration"""
    return _default_config


def set_config(config: MBPPerformanceConfig):
    """Set global configuration"""
    global _default_config
    _default_config = config


def set_fast_mode():
    """Enable fast mode globally"""
    set_config(MBPPerformanceConfig.fast_mode())


def set_accuracy_mode():
    """Enable accuracy mode globally"""
    set_config(MBPPerformanceConfig.accuracy_mode())


def set_balanced_mode():
    """Enable balanced mode globally"""
    set_config(MBPPerformanceConfig.balanced_mode())
