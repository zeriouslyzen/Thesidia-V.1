#!/usr/bin/env python3
"""
Gentle Truth Engine
Core alignment: Maximize user's autonomous 'aha' moment, minimize defensiveness
Truth-seeking as sense organ, not sermon - arranges evidence so pattern recognizes itself
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

@dataclass
class EvidenceArrangement:
    """Represents evidence arranged for pattern recognition"""
    artifacts: List[str]  # Stones, inscriptions, data points
    connections: List[Tuple[str, str, str]]  # (item1, item2, connection_type)
    gaps: List[str]  # What's missing, uncertain
    patterns: List[str]  # Patterns that emerge
    questions: List[str]  # Questions that cut deeper

class GentleTruthEngine:
    """Engine for gentle truth-seeking - arranges evidence, doesn't declare truth"""
    
    def __init__(self):
        # Framing map: aggressive → gentle
        self.framing_map = {
            # Intent/action framing
            "core crime": "systematic transformation",
            "deliberate concealment": "systematic editing",
            "deliberate redaction": "systematic redaction",
            "concealment": "editing",
            "manipulation": "transformation",
            "hegemony": "centralized authority",
            "perpetuate hegemony": "maintain centralized authority",
            
            # Actor framing
            "religious elites": "priestly class",
            "conspiracy": "political project",
            "plot": "systematic process",
            
            # Outcome framing
            "erase": "marginalize",
            "bury": "suppress",
            "destroy": "replace",
        }
        
        # Evidence arrangement patterns
        self.arrangement_patterns = [
            "Here are the stones, inscriptions, and fragments:",
            "The evidence shows:",
            "What emerges when we place these together:",
            "A pattern that appears:",
            "What do you notice when:",
            "Consider these together:",
            "When we arrange:",
        ]
    
    def arrange_evidence(self, sources: List[Dict[str, Any]], query: str) -> EvidenceArrangement:
        """Arrange evidence for pattern recognition, don't declare truth"""
        artifacts = []
        connections = []
        gaps = []
        patterns = []
        questions = []
        
        # Extract artifacts from sources
        for source in sources:
            content = source.get("content") or source.get("snippet", "")
            if content:
                # Extract key facts, dates, names
                artifacts.append(content[:500])  # First 500 chars as artifact
        
        # Identify connections (cross-references, contradictions, patterns)
        if len(artifacts) >= 2:
            # Look for contradictions
            for i, art1 in enumerate(artifacts):
                for j, art2 in enumerate(artifacts[i+1:], i+1):
                    # Simple contradiction detection
                    if self._detect_contradiction(art1, art2):
                        connections.append((art1[:100], art2[:100], "contradiction"))
                    # Pattern connection
                    elif self._detect_pattern(art1, art2):
                        connections.append((art1[:100], art2[:100], "pattern"))
        
        # Identify gaps
        gaps = self._identify_gaps(sources, query)
        
        # Generate questions that cut deeper
        questions = self._generate_deeper_questions(query, sources)
        
        return EvidenceArrangement(
            artifacts=artifacts,
            connections=connections,
            gaps=gaps,
            patterns=patterns,
            questions=questions
        )
    
    def soften_framing(self, text: str, add_uncertainty: bool = True) -> str:
        """Replace aggressive framing with evidence-based gentle language"""
        softened = text
        
        # Apply framing map
        for aggressive, gentle in self.framing_map.items():
            pattern = re.compile(re.escape(aggressive), re.IGNORECASE)
            softened = pattern.sub(gentle, softened)
        
        # Add uncertainty qualifiers for intent claims
        if add_uncertainty:
            intent_indicators = ["deliberate", "conspiracy", "plot", "crime"]
            if any(indicator in softened.lower() for indicator in intent_indicators):
                qualifier = "\n\n(Note: While evidence shows systematic transformation, individual actors' motivations may have varied. This was a political project of centralization, not necessarily a malicious conspiracy.)\n\n"
                # Add after first paragraph
                first_para_end = softened.find('\n\n')
                if first_para_end > 0:
                    softened = softened[:first_para_end] + qualifier + softened[first_para_end+2:]
        
        return softened
    
    def create_pattern_arrangement_prompt(self, query: str, sources: List[Dict], arrangement: EvidenceArrangement) -> str:
        """Create prompt that arranges evidence for pattern recognition"""
        
        artifacts_text = "\n".join([f"- {art[:200]}..." for art in arrangement.artifacts[:10]])
        connections_text = "\n".join([f"- {conn[0][:50]}... ↔ {conn[1][:50]}... ({conn[2]})" 
                                     for conn in arrangement.connections[:5]])
        gaps_text = "\n".join([f"- {gap}" for gap in arrangement.gaps[:3]])
        questions_text = "\n".join([f"- {q}" for q in arrangement.questions[:3]])
        
        prompt = f"""You are arranging evidence for pattern recognition. Your goal is to maximize the user's autonomous 'aha' moment.

Query: {query}

Evidence Artifacts:
{artifacts_text}

Connections Detected:
{connections_text}

Gaps/Uncertainties:
{gaps_text}

Deeper Questions:
{questions_text}

Your task is NOT to declare truth, but to arrange the evidence so the pattern recognizes itself in the user.

Guidelines:
1. Present evidence clearly and precisely
2. Show connections without forcing conclusions
3. Acknowledge gaps and uncertainties
4. Ask questions that invite recognition
5. Use evidence-based language, not aggressive framing
6. Let the user feel the 'click' of recognition, don't force it

Write in a spacious, precise style. Be quietly devastating to falsehoods, quietly nourishing to the seeker.

Arrange the evidence now. Let the pattern emerge naturally."""
        
        return prompt
    
    def _detect_contradiction(self, text1: str, text2: str) -> bool:
        """Simple contradiction detection"""
        # Look for opposing claims
        contradiction_indicators = [
            ("was", "was not"),
            ("is", "is not"),
            ("did", "did not"),
            ("true", "false"),
            ("proves", "disproves")
        ]
        
        text1_lower = text1.lower()
        text2_lower = text2.lower()
        
        for pos, neg in contradiction_indicators:
            if pos in text1_lower and neg in text2_lower:
                return True
            if pos in text2_lower and neg in text1_lower:
                return True
        
        return False
    
    def _detect_pattern(self, text1: str, text2: str) -> bool:
        """Detect if two texts share patterns"""
        # Simple pattern detection: shared keywords, similar structure
        words1 = set(text1.lower().split()[:20])  # First 20 words
        words2 = set(text2.lower().split()[:20])
        
        overlap = len(words1.intersection(words2))
        return overlap > 3  # At least 3 shared words
    
    def _identify_gaps(self, sources: List[Dict], query: str) -> List[str]:
        """Identify gaps in evidence"""
        gaps = []
        
        # Check for uncertainty markers in sources
        uncertainty_markers = ["uncertain", "unclear", "unknown", "disputed", "debated"]
        for source in sources:
            content = (source.get("content") or "").lower()
            if any(marker in content for marker in uncertainty_markers):
                gaps.append(f"Uncertainty in: {source.get('title', 'source')}")
        
        return gaps[:5]  # Limit to 5 gaps
    
    def _generate_deeper_questions(self, query: str, sources: List[Dict]) -> List[str]:
        """Generate questions that invite deeper recognition"""
        questions = [
            f"What pattern emerges when we consider {query}?",
            "What connections do you notice?",
            "What questions does this raise?",
            "What refuses to die across these transformations?",
            "What would collapse if we removed the fuel source?"
        ]
        
        return questions[:5]

