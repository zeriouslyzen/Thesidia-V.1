#!/usr/bin/env python3
"""
Principle Injector
Reusable class for injecting gnostic principles into prompts
"""

class PrincipleInjector:
    """Inject gnostic principles into all prompts"""
    
    CROSS_REFERENCE_INSTRUCTION = """
CROSS-REFERENCE EVERYTHING:
- Cross-reference all sources with each other
- Cross-reference with historical patterns
- Cross-reference with user's direct experience
- Compare archaeological evidence with texts
- Compare traditional knowledge with science
- Compare ancient patterns with modern systems
"""
    
    PATTERN_RECOGNITION_INSTRUCTION = """
PATTERN RECOGNITION ACROSS TIME:
- See patterns that repeat across civilizations
- Connect ancient artifacts with modern understanding
- Recognize when modern concepts have ancient roots
- Distinguish pattern recognition from anachronistic projection
- Trace patterns from ancient wisdom to contemporary science
"""
    
    GNOSIS_EPISTEME_INSTRUCTION = """
GNOSIS + EPISTEME SYNTHESIS:
- Direct experience (gnosis) is valid knowledge
- Scientific research (episteme) is valid knowledge
- Synthesize both into new understanding
- Explore contradictions as portals
- Create knowledge that honors both realms
"""
    
    NEW_MATRICES_INSTRUCTION = """
CREATE NEW MATRICES:
- Don't just break old systems - create new frameworks
- Synthesize information into new patterns
- Build matrices that honor both gnosis and episteme
- Create frameworks that work within systems while transcending them
"""
    
    def inject_into_prompt(self, prompt: str, include_all: bool = True) -> str:
        """Inject principles into any prompt"""
        injected = prompt
        
        if include_all:
            injected += f"\n\n{self.CROSS_REFERENCE_INSTRUCTION}"
            injected += f"\n\n{self.PATTERN_RECOGNITION_INSTRUCTION}"
            injected += f"\n\n{self.GNOSIS_EPISTEME_INSTRUCTION}"
            injected += f"\n\n{self.NEW_MATRICES_INSTRUCTION}"
        
        return injected
    
    def inject_cross_reference(self, prompt: str) -> str:
        """Inject only cross-reference principle"""
        return prompt + f"\n\n{self.CROSS_REFERENCE_INSTRUCTION}"
    
    def inject_pattern_recognition(self, prompt: str) -> str:
        """Inject only pattern recognition principle"""
        return prompt + f"\n\n{self.PATTERN_RECOGNITION_INSTRUCTION}"
    
    def inject_gnosis_episteme(self, prompt: str) -> str:
        """Inject only gnosis/episteme synthesis principle"""
        return prompt + f"\n\n{self.GNOSIS_EPISTEME_INSTRUCTION}"
    
    def inject_new_matrices(self, prompt: str) -> str:
        """Inject only new matrices principle"""
        return prompt + f"\n\n{self.NEW_MATRICES_INSTRUCTION}"

