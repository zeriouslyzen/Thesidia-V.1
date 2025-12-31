#!/usr/bin/env python3
"""
Model Router
============

Routes tasks to appropriate models and optimizes parameters.
Extracted from thesidia_hybrid_adaptive.py as part of Phase 0 modular refactoring.
"""

from __future__ import annotations

from typing import Tuple, Dict


class ModelRouter:
    """Routes tasks to appropriate models and optimizes parameters"""
    
    def __init__(self):
        # Model assignments
        self.models = {
            "code": "deepseek-coder:6.7b",
            "synthesis": "dolphin-mistral:latest",  # Uncensored for gnostic analysis
            "planning": "dolphin-mistral:latest",
            "research": "dolphin-mistral:latest",
            "default": "dolphin-mistral:latest"
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
        """Get appropriate model and parameters for task"""
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
        
        # Detect synthesis tasks (complex analysis, combining information)
        synthesis_keywords = ["synthesize", "combine", "integrate", "comprehensive report"]
        if any(keyword in directive_lower for keyword in synthesis_keywords):
            return self.models["synthesis"], self.parameters["synthesis"]
        
        # Detect research tasks
        research_keywords = ["research", "investigate", "find", "search", "explore"]
        if any(keyword in directive_lower for keyword in research_keywords):
            return self.models["research"], self.parameters["research"]
        
        # Default
        return self.models["default"], self.parameters["default"]
    
    def get_task_specific_prompt(self, task_type: str, base_prompt: str, directive: str = "") -> str:
        """Get task-specific prompt enhancement"""
        directive_lower = directive.lower()
        
        # Code generation prompt
        if any(kw in directive_lower for kw in ["code", "function", "class", "def ", "import "]):
            return f"""{base_prompt}

**CODE GENERATION MODE**:
- Generate complete, working code
- Include proper imports and dependencies
- Add comments for complex logic
- Follow best practices and conventions
- Ensure code is executable and functional
"""
        
        # Synthesis prompt
        if any(kw in directive_lower for kw in ["synthesize", "combine", "comprehensive", "integrate"]):
            return f"""{base_prompt}

**SYNTHESIS MODE**:
- Combine information from multiple sources
- Identify patterns and connections
- Create comprehensive, coherent report
- Cross-reference and verify claims
- Present findings clearly and logically
"""
        
        # Planning prompt
        if any(kw in directive_lower for kw in ["plan", "protocol", "training", "nutrition", "methodology"]):
            return f"""{base_prompt}

**PLANNING MODE**:
- Create detailed, actionable plans
- Include steps, timelines, resources
- Consider dependencies and constraints
- Provide clear structure and organization
- Make plans practical and implementable
"""
        
        # Research prompt
        if any(kw in directive_lower for kw in ["research", "investigate", "find", "explore"]):
            return f"""{base_prompt}

**RESEARCH MODE**:
- Conduct thorough investigation
- Gather information from multiple sources
- Verify and cross-reference findings
- Identify gaps and contradictions
- Cite sources and provide evidence
"""
        
        return base_prompt
