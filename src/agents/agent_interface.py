#!/usr/bin/env python3
"""
Agent Interface - Protocol definition for agent communication
Defines standard interfaces for agent-to-agent communication
"""

from typing import Protocol, Dict, Any, Optional, List
from abc import ABC, abstractmethod
from datetime import datetime


class AgentInterface(Protocol):
    """
    Protocol defining the interface all agents must implement.
    Used for type checking and ensuring agent compatibility.
    """
    
    agent_id: str
    capabilities: List[str]
    status: str
    
    def process(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process input and return result."""
        ...
    
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities."""
        ...
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information."""
        ...


class MessageProtocol:
    """Standard message format for agent-to-agent communication"""
    
    @staticmethod
    def create_message(
        sender_id: str,
        recipient_id: str,
        message_type: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a standardized message for agent communication.
        
        Args:
            sender_id: ID of sending agent
            recipient_id: ID of receiving agent
            message_type: Type of message (query, response, event, etc.)
            content: Message content
            metadata: Optional metadata
            
        Returns:
            Standardized message dictionary
        """
        return {
            "sender": sender_id,
            "recipient": recipient_id,
            "type": message_type,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def create_response(
        original_message: Dict[str, Any],
        response_content: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a response to an original message.
        
        Args:
            original_message: Original message being responded to
            response_content: Response content
            metadata: Optional metadata
            
        Returns:
            Response message dictionary
        """
        return {
            "sender": original_message["recipient"],
            "recipient": original_message["sender"],
            "type": "response",
            "content": response_content,
            "metadata": {
                **(metadata or {}),
                "in_reply_to": original_message.get("timestamp")
            },
            "timestamp": datetime.now().isoformat()
        }

