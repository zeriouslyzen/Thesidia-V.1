"""
Synthesis Module
================

Analysis & synthesis components:
- Data synthesizer
- Truth engine (7-layer epistemology)
- Gnostic blade mode
- Skepticism engine
- Quality filter
"""

from .truth_engine import TruthEngine
from .skepticism_engine import IntuitiveSkepticism
from .quality_filter import DataQualityFilter
from .data_synthesizer import DataSynthesizer
from .archetypal_analyzer import ArchetypalAnalyzer
from .esoteric_knowledge_base import EsotericKnowledgeBase

__all__ = [
    "TruthEngine",
    "IntuitiveSkepticism",
    "DataQualityFilter",
    "DataSynthesizer",
    "ArchetypalAnalyzer",
    "EsotericKnowledgeBase",
]

