#!/usr/bin/env python3
"""
Prompt Builder - Vibecode Compliance
====================================

Fixes prompt shadowing: Too many things in prompt → token competition → unreliable behavior.

Solution: Prompt budget system with prioritization.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    Builds prompts within token budget to prevent shadowing.
    
    Prioritizes: system > user > context > research
    Truncates if over budget.
    """
    
    # Token budgets (approximate, 1 token ≈ 4 characters)
    PROMPT_BUDGET = {
        "system": 2000,      # System instructions (highest priority)
        "context": 1000,     # Context/memory
        "research": 1500,    # Research data
        "user": 500,         # User query
        "total": 5000        # Total budget
    }
    
    def __init__(self, budget: Optional[Dict[str, int]] = None):
        """
        Initialize prompt builder.
        
        Args:
            budget: Custom budget dictionary (optional)
        """
        self.budget = budget or self.PROMPT_BUDGET.copy()
    
    def build_prompt(
        self, 
        components: Dict[str, str],
        prioritize: Optional[List[str]] = None
    ) -> str:
        """
        Build prompt within budget.
        
        Args:
            components: Dictionary of prompt components:
                - "system": System instructions
                - "context": Context/memory
                - "research": Research data
                - "user": User query
            prioritize: Optional list of component names in priority order
                       (default: ["system", "user", "context", "research"])
        
        Returns:
            Built prompt string within budget
        """
        if prioritize is None:
            prioritize = ["system", "user", "context", "research"]
        
        # Calculate character budgets (1 token ≈ 4 chars)
        char_budgets = {
            key: self.budget[key] * 4 
            for key in self.budget.keys() 
            if key != "total"
        }
        total_char_budget = self.budget["total"] * 4
        
        # Build prompt with prioritization
        prompt_parts = []
        used_chars = 0
        
        for component_name in prioritize:
            if component_name not in components:
                continue
            
            component_text = components[component_name]
            component_budget = char_budgets.get(component_name, 0)
            
            # Truncate if over budget
            if len(component_text) > component_budget:
                logger.warning(
                    f"Component '{component_name}' exceeds budget "
                    f"({len(component_text)} > {component_budget} chars), truncating"
                )
                component_text = component_text[:component_budget] + "..."
            
            # Check total budget
            remaining_budget = total_char_budget - used_chars
            if len(component_text) > remaining_budget:
                logger.warning(
                    f"Total budget exceeded, truncating '{component_name}' "
                    f"({len(component_text)} > {remaining_budget} chars)"
                )
                component_text = component_text[:remaining_budget] + "..."
            
            if component_text:
                prompt_parts.append(component_text)
                used_chars += len(component_text)
        
        # Join parts
        prompt = "\n\n".join(prompt_parts)
        
        # Final check
        if len(prompt) > total_char_budget:
            logger.warning(
                f"Final prompt exceeds total budget "
                f"({len(prompt)} > {total_char_budget} chars), truncating"
            )
            prompt = prompt[:total_char_budget] + "..."
        
        return prompt
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count from text.
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count (1 token ≈ 4 characters)
        """
        return len(text) // 4
    
    def get_budget_status(self, components: Dict[str, str]) -> Dict[str, Any]:
        """
        Get budget status for components.
        
        Args:
            components: Dictionary of prompt components
            
        Returns:
            Dictionary with budget status:
                - "within_budget": bool
                - "component_sizes": Dict[str, int]
                - "total_size": int
                - "budget": int
                - "remaining": int
        """
        char_budgets = {
            key: self.budget[key] * 4 
            for key in self.budget.keys() 
            if key != "total"
        }
        total_char_budget = self.budget["total"] * 4
        
        component_sizes = {
            name: len(text) 
            for name, text in components.items()
        }
        
        total_size = sum(component_sizes.values())
        within_budget = total_size <= total_char_budget
        
        return {
            "within_budget": within_budget,
            "component_sizes": component_sizes,
            "total_size": total_size,
            "budget": total_char_budget,
            "remaining": max(0, total_char_budget - total_size),
            "over_budget": max(0, total_size - total_char_budget) if not within_budget else 0
        }

