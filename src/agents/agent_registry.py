#!/usr/bin/env python3
"""
Agent Registry - Central registry for agent management
Handles agent registration, discovery, and lifecycle management
"""

from typing import Dict, List, Optional, Type, Any
from datetime import datetime
import threading

from .base_agent import BaseAgent
from .agent_interface import AgentInterface


class AgentRegistry:
    """
    Central registry for managing agents in the system.
    
    Provides:
    - Agent registration and discovery
    - Capability-based agent selection
    - Agent lifecycle management
    - Agent lookup and retrieval
    """
    
    def __init__(self):
        """Initialize agent registry."""
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_classes: Dict[str, Type[BaseAgent]] = {}
        self._capability_index: Dict[str, List[str]] = {}  # capability -> [agent_ids]
        self._lock = threading.Lock()
    
    def register_agent(self, agent: BaseAgent) -> bool:
        """
        Register an agent instance.
        
        Args:
            agent: Agent instance to register
            
        Returns:
            True if registered successfully, False if agent_id already exists
        """
        with self._lock:
            if agent.agent_id in self._agents:
                return False
            
            self._agents[agent.agent_id] = agent
            
            # Index by capabilities
            capabilities = agent.get_capabilities()
            for capability in capabilities:
                if capability not in self._capability_index:
                    self._capability_index[capability] = []
                if agent.agent_id not in self._capability_index[capability]:
                    self._capability_index[capability].append(agent.agent_id)
            
            return True
    
    def register_agent_class(self, name: str, agent_class: Type[BaseAgent], capabilities: List[str]):
        """
        Register an agent class for dynamic instantiation.
        
        Args:
            name: Name identifier for the agent class
            agent_class: Agent class to register
            capabilities: List of capabilities this agent class provides
        """
        with self._lock:
            self._agent_classes[name] = agent_class
            
            # Index by capabilities
            for capability in capabilities:
                if capability not in self._capability_index:
                    self._capability_index[capability] = []
                # Note: Class capabilities don't add to agent list until instantiated
    
    def create_agent(
        self,
        agent_class_name: str,
        agent_id: str,
        **kwargs
    ) -> Optional[BaseAgent]:
        """
        Create and register an agent instance from a registered class.
        
        Args:
            agent_class_name: Name of registered agent class
            agent_id: Unique ID for the new agent instance
            **kwargs: Arguments to pass to agent constructor
            
        Returns:
            Created agent instance, or None if class not found
        """
        with self._lock:
            if agent_class_name not in self._agent_classes:
                return None
            
            agent_class = self._agent_classes[agent_class_name]
            agent = agent_class(agent_id=agent_id, **kwargs)
            
            if self.register_agent(agent):
                return agent
            
            return None
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: Agent ID to look up
            
        Returns:
            Agent instance, or None if not found
        """
        with self._lock:
            return self._agents.get(agent_id)
    
    def find_agents_by_capability(self, capability: str) -> List[BaseAgent]:
        """
        Find all agents with a specific capability.
        
        Args:
            capability: Capability to search for
            
        Returns:
            List of agents with the capability
        """
        with self._lock:
            agent_ids = self._capability_index.get(capability, [])
            return [self._agents[aid] for aid in agent_ids if aid in self._agents]
    
    def find_agents_by_capabilities(self, capabilities: List[str]) -> List[BaseAgent]:
        """
        Find agents that have all specified capabilities.
        
        Args:
            capabilities: List of required capabilities
            
        Returns:
            List of agents with all capabilities
        """
        with self._lock:
            if not capabilities:
                return list(self._agents.values())
            
            # Find agents that have all capabilities
            matching_agents = []
            for agent_id, agent in self._agents.items():
                agent_capabilities = agent.get_capabilities()
                if all(cap in agent_capabilities for cap in capabilities):
                    matching_agents.append(agent)
            
            return matching_agents
    
    def list_all_agents(self) -> List[BaseAgent]:
        """
        List all registered agents.
        
        Returns:
            List of all registered agent instances
        """
        with self._lock:
            return list(self._agents.values())
    
    def list_agent_classes(self) -> List[str]:
        """
        List all registered agent class names.
        
        Returns:
            List of agent class names
        """
        with self._lock:
            return list(self._agent_classes.keys())
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            agent_id: Agent ID to unregister
            
        Returns:
            True if unregistered, False if not found
        """
        with self._lock:
            if agent_id not in self._agents:
                return False
            
            agent = self._agents[agent_id]
            capabilities = agent.get_capabilities()
            
            # Remove from capability index
            for capability in capabilities:
                if capability in self._capability_index:
                    if agent_id in self._capability_index[capability]:
                        self._capability_index[capability].remove(agent_id)
            
            # Remove agent
            del self._agents[agent_id]
            return True
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Dictionary with registry stats
        """
        with self._lock:
            return {
                "total_agents": len(self._agents),
                "total_classes": len(self._agent_classes),
                "capabilities_count": len(self._capability_index),
                "agents_by_capability": {
                    cap: len(agent_ids)
                    for cap, agent_ids in self._capability_index.items()
                }
            }

