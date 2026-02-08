"""
Semantic Router for Forensic Query Detection (v2)

Implements a hybrid routing system:
1. Fast path: Keyword matching (instant)
2. Fallback: Semantic embedding similarity

This approach is the industry standard for LLM query classification,
combining speed (keywords) with flexibility (embeddings).
"""

from typing import List, Tuple, Optional
import numpy as np

# Reference forensic queries for semantic similarity comparison
# These represent the "ideal" forensic queries that trigger deep research
FORENSIC_REFERENCE_QUERIES = [
    # Religious/textual forensics
    "what are the true origins of genesis",
    "decode the hidden meaning in the bible",
    "trace the redaction patterns in scripture",
    "who edited the torah and why",
    "what was suppressed in the council of nicaea",
    
    # Power structure analysis
    "expose the power structures behind modern banking",
    "trace the patterns of control in finance",
    "how do elites maintain systematic control",
    "what patterns repeat across civilizations",
    "map the hidden architecture of influence",
    
    # Cross-cultural pattern recognition
    "connect sumerian texts to modern systems",
    "what do meditation and stoicism have in common at the deepest level",
    "trace the etymology of consciousness across cultures",
    "compare creation myths across civilizations",
    "what archetypal patterns persist through history",
    
    # Health/pharma forensics
    "what is really going on with vaccine development",
    "trace the pharmaceutical industry's influence on medicine",
    "expose the hidden economics of healthcare",
    
    # Historical revisionism detection
    "what was buried about the bronze age collapse",
    "trace the suppressed history of matriarchal traditions",
    "what alternative narratives were edited out",
    
    # Esoteric/occult analysis
    "decode the symbolism in masonic imagery",
    "trace the hermetic tradition through history",
    "what do gnostic texts reveal about early christianity",
]

# Pre-computed embeddings cache (populated on first use)
_embedding_cache: Optional[np.ndarray] = None
_embedding_model = None


def _get_embedding_model():
    """Lazy-load embedding model to avoid startup cost."""
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            # all-MiniLM-L6-v2 is fast and effective for semantic similarity
            _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            # Fallback: return None if sentence-transformers not installed
            return None
    return _embedding_model


def _get_reference_embeddings() -> Optional[np.ndarray]:
    """Get cached embeddings for reference forensic queries."""
    global _embedding_cache
    if _embedding_cache is None:
        model = _get_embedding_model()
        if model is None:
            return None
        _embedding_cache = model.encode(FORENSIC_REFERENCE_QUERIES, convert_to_numpy=True)
    return _embedding_cache


def compute_forensic_similarity(query: str) -> Tuple[float, str]:
    """
    Compute semantic similarity between query and reference forensic queries.
    
    Returns:
        Tuple of (max_similarity, best_matching_reference)
        similarity is 0.0-1.0, higher = more forensic
    """
    model = _get_embedding_model()
    if model is None:
        return 0.0, ""
    
    ref_embeddings = _get_reference_embeddings()
    if ref_embeddings is None:
        return 0.0, ""
    
    # Encode the user query
    query_embedding = model.encode([query], convert_to_numpy=True)[0]
    
    # Compute cosine similarity with all reference queries
    similarities = np.dot(ref_embeddings, query_embedding) / (
        np.linalg.norm(ref_embeddings, axis=1) * np.linalg.norm(query_embedding)
    )
    
    max_idx = np.argmax(similarities)
    max_sim = float(similarities[max_idx])
    best_match = FORENSIC_REFERENCE_QUERIES[max_idx]
    
    return max_sim, best_match


def detect_forensic_routing_v2(
    text: str, 
    comprehensive: bool = False,
    semantic_threshold: float = 0.65,
    debug: bool = False
) -> Tuple[bool, str, float]:
    """
    Hybrid forensic routing detection.
    
    Phase 1: Keyword matching (fast path)
    Phase 2: Semantic similarity (fallback if no keyword match)
    
    Args:
        text: User query
        comprehensive: Include extended keywords (health, finance, law)
        semantic_threshold: Minimum similarity to trigger forensic routing (0.0-1.0)
        debug: If True, print routing decisions
        
    Returns:
        Tuple of (should_route_forensic, routing_reason, confidence)
    """
    if not text:
        return False, "empty_query", 0.0
    
    from src.support.query_utils import normalize_query, detect_forensic_routing
    
    normalized = normalize_query(text)
    
    # Phase 1: Keyword matching (instant)
    keyword_match = detect_forensic_routing(text, comprehensive=comprehensive)
    if keyword_match:
        if debug:
            print(f"🔍 ROUTING: Keyword match detected for query: '{text[:50]}...'")
        return True, "keyword_match", 1.0
    
    # Phase 2: Semantic similarity (fallback)
    similarity, best_match = compute_forensic_similarity(normalized)
    
    if debug:
        print(f"🔍 ROUTING: Semantic similarity = {similarity:.3f} (threshold: {semantic_threshold})")
        print(f"🔍 ROUTING: Best match: '{best_match[:60]}...'")
    
    if similarity >= semantic_threshold:
        return True, f"semantic_match:{best_match[:40]}", similarity
    
    return False, "no_match", similarity


# Convenience function for backwards compatibility
def should_route_forensic(text: str, comprehensive: bool = False) -> bool:
    """Simple boolean check for forensic routing."""
    result, _, _ = detect_forensic_routing_v2(text, comprehensive=comprehensive)
    return result
