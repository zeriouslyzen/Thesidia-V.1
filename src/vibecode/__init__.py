"""
Vibecode Compliance Module
==========================

Fixes 9 hidden problems from Vibecode.txt:
1. Prompt Assembly Drift
2. Implicit Context Bleed
3. Race Conditions
4. Prompt Shadowing/Overload
5. Mixing Internal Notes
6. Memory Reinsertion Bugs
7. CSS/HTML Layer Injection
8. Mode Switching Without Reset
9. UI Echoing Old Output
"""

from .request_queue import RequestQueue, get_request_queue
from .memory_reinsertion import MemoryReinsertionProtocol
from .mode_reset import ModeResetProtocol
from .ui_sanitizer import UISanitizer

__all__ = [
    "RequestQueue",
    "get_request_queue",
    "MemoryReinsertionProtocol",
    "ModeResetProtocol",
    "UISanitizer",
]

