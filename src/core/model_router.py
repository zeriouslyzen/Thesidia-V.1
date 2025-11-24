#!/usr/bin/env python3
"""
Model Router - Core System
==========================

Routes tasks to appropriate models and optimizes parameters.
"""

from __future__ import annotations

from typing import Tuple, Dict


class ModelRouter:
    """Routes tasks to appropriate models and optimizes parameters"""
    
    def __init__(self):
        # Model assignments
        self.models = {
            "code": "deepseek-coder:6.7b",
            "synthesis": "clean-mistral:latest",  # Use clean-mistral (oracle-agent has hardcoded system prompt that refuses)
            "planning": "clean-mistral:latest",
            "research": "clean-mistral:latest",
            "default": "clean-mistral:latest"
        }
        
        # Parameter optimization per task type
        self.parameters = {
            "code": {"temperature": 0.3, "top_p": 0.95},  # Precise
            "synthesis": {"temperature": 0.8, "top_p": 0.9},  # Creative
            "planning": {"temperature": 0.7, "top_p": 0.9},  # Structured
            "research": {"temperature": 0.7, "top_p": 0.95},  # Balanced
            "default": {"temperature": 0.7, "top_p": 0.95}
        }
    
    def get_model_for_task(self, task_type: str, directive: str = "") -> Tuple[str, Dict]:
        """
        Get appropriate model and parameters for task.
        
        Args:
            task_type: Type of task (code, synthesis, planning, research, analysis, engineering)
            directive: Optional directive text for keyword detection
            
        Returns:
            Tuple of (model_name, parameters_dict)
        """
        directive_lower = directive.lower()
        
        # Check task_type first (more reliable)
        if task_type == "synthesis":
            return self.models["synthesis"], self.parameters["synthesis"]
        
        if task_type == "development":
            # Check if it's actually code (not just website planning)
            if any(kw in directive_lower for kw in ["code", "function", "class", "def ", "import ", "algorithm", "script"]):
                return self.models["code"], self.parameters["code"]
            # Website/app development - use planning model
            return self.models["planning"], self.parameters["planning"]
        
        if task_type == "planning":
            return self.models["planning"], self.parameters["planning"]
        
        if task_type == "analysis":
            return self.models["synthesis"], self.parameters["synthesis"]
        
        if task_type == "engineering":
            return self.models["planning"], self.parameters["planning"]  # Engineering uses planning model
        
        # Detect code tasks by keywords (fallback)
        code_keywords = ["code", "function", "class", "def ", "import ", "algorithm", "script"]
        if any(keyword in directive_lower for keyword in code_keywords):
            return self.models["code"], self.parameters["code"]
        
        # Default
        return self.models["default"], self.parameters["default"]

