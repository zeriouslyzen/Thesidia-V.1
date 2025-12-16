#!/usr/bin/env python3
"""
Base Agent - Abstract base class for all agents
Provides standard interface and common functionality
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from ..core.model_client import ModelClient
from ..memory.memory_manager import MemoryManager


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    
    Provides standard interface and common functionality:
    - Memory access
    - Model calls
    - Reasoning capabilities
    - Event handling
    """
    
    def __init__(
        self,
        agent_id: str,
        model: str = "clean-mistral:latest",
        base_dir: Path = None,
        model_client: Optional[ModelClient] = None,
        memory_manager: Optional[MemoryManager] = None
    ):
        """
        Initialize base agent.
        
        Args:
            agent_id: Unique identifier for this agent
            model: Default model to use
            base_dir: Base directory for data storage
            model_client: Optional shared ModelClient instance
            memory_manager: Optional shared MemoryManager instance
        """
        self.agent_id = agent_id
        self.model = model
        self.base_dir = base_dir or Path(".")
        
        # Initialize or use provided components
        self.model_client = model_client or ModelClient(default_model=model)
        self.memory_manager = memory_manager or MemoryManager(base_dir=self.base_dir)
        
        # Agent state
        self.capabilities: List[str] = []
        self.status: str = "initialized"
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        
        # Event handlers (will be set by event system)
        self._event_handlers: Dict[str, List[callable]] = {}
    
    @abstractmethod
    def process(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process input data and return result.
        
        Args:
            input_data: Input to process (can be string, dict, etc.)
            context: Optional context dictionary
            
        Returns:
            Dictionary with processing result
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Get list of capabilities this agent provides.
        
        Returns:
            List of capability strings
        """
        pass
    
    def get_memory_context(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Retrieve relevant memory context for a query.
        
        Args:
            query: Query string
            top_k: Number of relevant memories to retrieve
            
        Returns:
            Dictionary with memory context
        """
        return self.memory_manager.retrieve_context(query)
    
    def store_memory(self, user_input: str, assistant_output: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Store interaction in memory.
        
        Args:
            user_input: User's message
            assistant_output: Assistant's response
            metadata: Optional metadata
        """
        self.memory_manager.store_interaction(user_input, assistant_output, metadata)
    
    def call_model(
        self,
        input_text: str,
        enhanced_base: Optional[str] = None,
        conversation_context: Optional[str] = None,
        research_context: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a model call through ModelClient.
        
        Args:
            input_text: User's query
            enhanced_base: Optional system prompt
            conversation_context: Optional conversation history
            research_context: Optional research data
            options: Optional model options
            
        Returns:
            Model response dictionary
        """
        return self.model_client.chat(
            model=self.model,
            input_text=input_text,
            enhanced_base=enhanced_base,
            conversation_context=conversation_context,
            research_context=research_context,
            options=options
        )
    
    def update_status(self, status: str):
        """Update agent status."""
        self.status = status
        self.last_active = datetime.now()
    
    def register_event_handler(self, event_type: str, handler: callable):
        """
        Register an event handler for a specific event type.
        
        Args:
            event_type: Type of event to handle
            handler: Handler function
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
    
    def emit_event(self, event_type: str, data: Dict[str, Any]):
        """
        Emit an event (handlers will be called by event system).
        
        Args:
            event_type: Type of event
            data: Event data
        """
        # Event system will handle routing
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get agent information.
        
        Returns:
            Dictionary with agent info
        """
        return {
            "agent_id": self.agent_id,
            "model": self.model,
            "capabilities": self.get_capabilities(),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat()
        }

