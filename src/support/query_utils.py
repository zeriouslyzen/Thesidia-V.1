"""
Query normalization and forensic routing detection utilities.

This module provides shared functions for normalizing user queries
and detecting if they require forensic analysis. Previously duplicated
across multiple files, now centralized here.
"""

from typing import List


def normalize_query(text: str) -> str:
    """
    Normalize query with typo fixes.
    
    Fixes common typos that prevent proper routing of forensic queries.
    For example: "genensis" -> "genesis", "dycrpted" -> "decrypted"
    
    Args:
        text: Raw user input query
        
    Returns:
        Normalized query string (lowercase, typos fixed)
    """
    if not text:
        return ""
    
    text_normalized = text.lower()
    
    # Common typo fixes for forensic query terms
    typo_fixes = {
        'gneneis': 'genesis',
        'genisis': 'genesis',
        'genises': 'genesis',
        'genensis': 'genesis',
        'decrpted': 'decrypted',
        'decrpt': 'decrypt',
        'dycrpted': 'decrypted',
        'dycrypt': 'decrypt',
        'bibel': 'bible',
    }
    
    for typo, correct in typo_fixes.items():
        text_normalized = text_normalized.replace(typo, correct)
    
    return text_normalized


def detect_forensic_routing(text: str, comprehensive: bool = False) -> bool:
    """
    Detect if query needs forensic analysis.
    
    Forensic queries require deep research and truth-seeking analysis.
    This includes topics like religion, health, finance, law, and power structures.
    
    Args:
        text: User query (will be normalized internally)
        comprehensive: If True, includes extended keyword list (health, finance, law, etc.)
                      If False, uses basic list (religion, decode, etc.)
        
    Returns:
        True if query requires forensic analysis, False otherwise
    """
    if not text:
        return False
    
    normalized = normalize_query(text)
    
    # Basic forensic keywords (always checked)
    basic_keywords = [
        # Religious/spiritual
        "genesis", "bible", "scripture", "torah", "quran", "veda", "ancient", 
        "religion", "abrahamic", "origins", "canon", "canonization",
        # Decode/decrypt
        "decode", "decoded", "decrypt", "decrypted", "dycrpted", "dycrypt", 
        "expose", "hidden",
        # Truth-seeking phrases
        "what are", "what are x really", "really about", "characters", 
        "what's really", "true origins", "real origins"
    ]
    
    if comprehensive:
        # Extended keywords for comprehensive detection (used in main processing)
        extended_keywords = basic_keywords + [
            # Health/medicine
            "health", "medicine", "medical", "pharmaceutical", "pharma", "drug", 
            "treatment", "cure", "disease", "illness", "wellness",
            "supplement", "vitamin", "therapy", "surgery", "diagnosis", "prescription",
            # Finance/banking
            "bank", "banks", "banking", "finance", "financial", "money", "currency", 
            "bitcoin", "crypto", "economy", "economic",
            "federal reserve", "fed", "wall street", "stock market", "investment", "trading",
            # Law/legal
            "law", "legal", "court", "judge", "lawyer", "attorney", "lawsuit", 
            "legislation", "constitution", "rights",
            "justice", "legal system", "jurisdiction", "precedent",
            # Power/truth-seeking
            "power", "consciousness", "systematic transformation", "redaction", 
            "transformation",
            "deeper", "darker", "secrets", "uncover", "reveal", "full deep dive", 
            "deep dive",
            "comprehensive", "extensive", "really", "actually", "truth", "real", "true",
            "hack", "hacking", "matrix", "reality"
        ]
        keywords = extended_keywords
    else:
        keywords = basic_keywords
    
    return any(term in normalized for term in keywords)

