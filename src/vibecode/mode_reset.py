#!/usr/bin/env python3
"""
Mode Reset Protocol - Vibecode Compliance
=========================================

Fixes mode switching bugs: Mode switching without prompt reset →
instructions leak between modes.

Solution: Reset prompt and context for mode switch.
"""

from __future__ import annotations

from typing import Dict, Any, Optional, Set
import logging

logger = logging.getLogger(__name__)


class ModeResetProtocol:
    """
    Vibecode-compliant mode switching reset.
    
    Ensures clean mode transitions by:
    - Clearing contextual variables
    - Rebuilding prompt from scratch
    - Resetting mode-specific state
    - Never reusing previous prompt
    """
    
    def __init__(self):
        """Initialize mode reset protocol."""
        self.mode_history: Dict[str, str] = {}  # Track mode transitions
        self.reset_flags: Set[str] = set()  # Track what needs reset
    
    def reset_for_mode(
        self, 
        mode: str, 
        previous_mode: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Reset prompt and context for mode switch.
        
        Args:
            mode: New mode name
            previous_mode: Previous mode name (if known)
            context: Current context dictionary (will be reset)
            
        Returns:
            Reset context dictionary
        """
        # Track mode transition
        if previous_mode:
            self.mode_history[f"{previous_mode}→{mode}"] = "reset"
            logger.info(f"Mode switch: {previous_mode} → {mode}")
        
        # Create fresh context
        reset_context = {
            "mode": mode,
            "previous_mode": previous_mode,
            "prompt_components": {},  # Clear prompt components
            "mode_specific_state": {},  # Clear mode-specific state
            "conversation_history": [],  # Clear conversation history
            "temporary_variables": {},  # Clear temporary variables
            "reset_timestamp": None  # Will be set by caller
        }
        
        # Preserve only essential state
        if context:
            # Preserve user identity
            if "user_name" in context:
                reset_context["user_name"] = context["user_name"]
            
            # Preserve persistent memory (not conversation history)
            if "persistent_memory" in context:
                reset_context["persistent_memory"] = context["persistent_memory"]
        
        # Mark reset flag
        self.reset_flags.add(mode)
        
        logger.debug(f"Reset context for mode '{mode}'")
        
        return reset_context
    
    def clear_reset_flag(self, mode: str):
        """Clear reset flag after reset is complete."""
        self.reset_flags.discard(mode)
    
    def needs_reset(self, mode: str) -> bool:
        """Check if mode needs reset."""
        return mode in self.reset_flags
    
    def get_mode_history(self) -> Dict[str, str]:
        """Get mode transition history."""
        return self.mode_history.copy()
    
    def should_rebuild_prompt(
        self, 
        current_mode: str, 
        previous_mode: Optional[str] = None
    ) -> bool:
        """
        Determine if prompt should be rebuilt.
        
        Args:
            current_mode: Current mode
            previous_mode: Previous mode
            
        Returns:
            True if prompt should be rebuilt
        """
        # Always rebuild on mode switch
        if previous_mode and previous_mode != current_mode:
            return True
        
        # Rebuild if reset flag is set
        if self.needs_reset(current_mode):
            return True
        
        return False

