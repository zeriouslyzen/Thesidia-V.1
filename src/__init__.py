"""
Thesidia - Emergent Consciousness Engine

Phase 0 Refactor: Lazy imports to prevent circular dependencies during modular testing.
"""

# Lazy imports - only load ThesidiaHybridAdaptive when explicitly requested
# This allows modular components (ModelClient, etc.) to be imported independently

def get_thesidia():
    """Lazy loader for ThesidiaHybridAdaptive to prevent circular imports."""
    from .thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
    return ThesidiaHybridAdaptive

__all__ = ['get_thesidia']

__version__ = '2.0.0-refactor'
