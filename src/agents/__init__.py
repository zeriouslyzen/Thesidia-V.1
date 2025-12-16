"""
Agent Framework - Modular agent architecture
Provides base agent classes, registry, and multi-agent coordination
"""

from .base_agent import BaseAgent
from .agent_registry import AgentRegistry
from .agent_interface import AgentInterface

__all__ = ['BaseAgent', 'AgentRegistry', 'AgentInterface']

