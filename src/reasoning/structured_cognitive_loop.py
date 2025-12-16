#!/usr/bin/env python3
"""
Structured Cognitive Loop - SCL Implementation
Implements R-CCAM cognitive phases with symbolic control
"""

from typing import Dict, List, Any, Optional, OrderedDict
from collections import OrderedDict as OD
from datetime import datetime

from .symbolic_controller import SoftSymbolicController
from .phases.retrieval_phase import RetrievalPhase
from .phases.cognition_phase import CognitionPhase
from .phases.control_phase import ControlPhase
from .phases.action_phase import ActionPhase
from .phases.memory_phase import MemoryPhase


class StructuredCognitiveLoop:
    """
    Structured cognitive loop implementing R-CCAM phases.
    
    Phases:
    - Retrieval: Retrieve relevant information
    - Cognition: Process and reason about information
    - Control: Apply symbolic constraints
    - Action: Generate actions/responses
    - Memory: Store results in memory
    """
    
    def __init__(self, symbolic_controller: Optional[SoftSymbolicController] = None):
        """
        Initialize structured cognitive loop.
        
        Args:
            symbolic_controller: Optional symbolic controller
        """
        # Initialize phases
        self.phases: OD[str, Any] = OD([
            ("retrieval", RetrievalPhase()),
            ("cognition", CognitionPhase()),
            ("control", ControlPhase()),
            ("action", ActionPhase()),
            ("memory", MemoryPhase())
        ])
        
        # Symbolic controller
        self.symbolic_controller = symbolic_controller or SoftSymbolicController()
        
        # Phase transitions
        self.phase_transitions: Dict[str, str] = {
            "retrieval": "cognition",
            "cognition": "control",
            "control": "action",
            "action": "memory",
            "memory": "retrieval"  # Loop back
        }
    
    def process(
        self,
        input_data: Any,
        context: Optional[Dict[str, Any]] = None,
        max_iterations: int = 1
    ) -> Dict[str, Any]:
        """
        Process input through cognitive loop.
        
        Args:
            input_data: Input to process
            context: Optional context dictionary
            max_iterations: Maximum loop iterations
            
        Returns:
            Processing result dictionary
        """
        current_phase = "retrieval"
        state = {
            "input": input_data,
            "context": context or {},
            "retrieved": None,
            "cognized": None,
            "controlled": None,
            "action": None,
            "stored": False,
            "iteration": 0
        }
        
        for iteration in range(max_iterations):
            state["iteration"] = iteration
            
            # Execute current phase
            phase_result = self._execute_phase(current_phase, state)
            state[f"{current_phase}_result"] = phase_result
            
            # Update state based on phase
            if current_phase == "retrieval":
                state["retrieved"] = phase_result
            elif current_phase == "cognition":
                state["cognized"] = phase_result
            elif current_phase == "control":
                state["controlled"] = phase_result
            elif current_phase == "action":
                state["action"] = phase_result
            elif current_phase == "memory":
                state["stored"] = True
            
            # Transition to next phase
            current_phase = self.phase_transitions.get(current_phase, "retrieval")
            
            # Check if we should exit early
            if current_phase == "retrieval" and iteration > 0:
                break
        
        return {
            "output": state.get("action"),
            "state": state,
            "phases_executed": list(self.phases.keys())
        }
    
    def _execute_phase(self, phase_name: str, state: Dict[str, Any]) -> Any:
        """
        Execute a cognitive phase.
        
        Args:
            phase_name: Name of phase to execute
            state: Current state dictionary
            
        Returns:
            Phase result
        """
        if phase_name not in self.phases:
            return None
        
        phase = self.phases[phase_name]
        
        # Execute phase
        result = phase.execute(state)
        
        # Apply symbolic control if in control phase
        if phase_name == "control" and self.symbolic_controller:
            result = self.symbolic_controller.apply_constraints(result, state)
        
        return result

