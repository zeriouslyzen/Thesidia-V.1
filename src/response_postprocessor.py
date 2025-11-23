#!/usr/bin/env python3
"""
Response Postprocessor
Post-processes responses to remove format markers, fix language, and validate citations
"""

import re
from typing import Tuple

def strip_transmission_format(text: str) -> str:
    """Aggressively strip ::TRANSMISSION:: format markers"""
    if not text:
        return text
    
    # Remove transmission headers
    text = re.sub(r'::TRANSMISSION:.*?→.*?\n?', '', text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r'::TRANSMISSION::.*?\n?', '', text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r'THESIDIA\s*→\s*USER', '', text, flags=re.IGNORECASE)
    text = re.sub(r'USER\s*→\s*THESIDIA', '', text, flags=re.IGNORECASE)
    
    # Remove end markers
    text = re.sub(r'[—\-]?\s*End\s+Transmission[^.]*\.?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Thesidia\s+Engaged[^.]*\.?\s*', '', text, flags=re.IGNORECASE)
    
    # Remove old sharpening prompts
    text = re.sub(r'→\s*Cut sharper[^.]*\.?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'What thread do we sever next\?', '', text, flags=re.IGNORECASE)
    
    # Remove any remaining ritualistic markers
    text = re.sub(r'::[A-Z_]+::', '', text, flags=re.MULTILINE)
    
    return text.strip()

def strip_forensic_format(text: str) -> str:
    """
    Strip ::EXPOSURE::, ::ETYMOLOGICAL INCISION::, etc. markers but keep content.
    This is a fallback - ideally naturalization happens before this.
    """
    if not text:
        return text
    
    # Remove forensic section markers but keep content
    forensic_markers = [
        r'::EXPOSURE::\s*',
        r'::ETYMOLOGICAL INCISION::\s*',
        r'::ETYMOLOGICAL::\s*',
        r'::BURIAL SITES::\s*',
        r'::BURIAL::\s*',
        r'::CURRENT VECTORS::\s*',
        r'::CURRENT::\s*',
        r'::CO-EVOLUTION EDGE::\s*',
        r'::CO-EVOLUTION::\s*',
        r'::THREAD OPTIONS::\s*',
        r'::THREADS::\s*',
    ]
    
    for marker in forensic_markers:
        text = re.sub(marker, '', text, flags=re.IGNORECASE | re.MULTILINE)
    
    return text.strip()

def fix_designed_language(text: str) -> str:
    """Replace "I am designed to" with natural language"""
    replacements = [
        (r'I am designed to', "I've found that"),
        (r'I am programmed to', "I recognize"),
        (r'My purpose is to', "I"),
        (r'I have been programmed with', "I can"),
        (r'As a truth-seeking entity', "As someone who recognizes patterns"),
    ]
    
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def detect_fake_citations(text: str) -> Tuple[str, list]:
    """
    Detect potentially fake citations and flag them
    Returns: (cleaned_text, warnings)
    """
    warnings = []
    
    # Pattern: "Source: [something]" or "(Source: [something])"
    citation_pattern = r'(?:Source|source):\s*([^,\n]+?)(?:,|\n|$)'
    citations = re.findall(citation_pattern, text)
    
    # Common fake citation patterns
    suspicious_patterns = [
        r'Source:\s*Unknown',
        r'Source:\s*Unknown\s+Gnostic',
        r'Source:\s*The\s+Gnostic\s+Scriptures',
        r'Source:\s*Unknown\s+text',
    ]
    
    for citation in citations:
        citation_clean = citation.strip()
        
        # Check for suspicious patterns
        for pattern in suspicious_patterns:
            if re.search(pattern, citation_clean, re.IGNORECASE):
                warnings.append(f"Potentially unverified citation: {citation_clean}")
                # Replace with warning
                text = text.replace(f"Source: {citation_clean}", 
                                  f"[UNVERIFIED: No verified source for this claim. Original citation: {citation_clean}]")
    
    return text, warnings

def postprocess_response(response: str, naturalize: bool = True) -> str:
    """
    Main postprocessing function
    Applies all fixes: strip formats, fix language, validate citations
    Optionally naturalizes forensic structure to prose
    """
    if not response:
        return response
    
    # Step 0: Naturalize forensic structure if needed (before stripping)
    if naturalize:
        try:
            from natural_prose_synthesizer import NaturalProseSynthesizer
            synthesizer = NaturalProseSynthesizer()
            if synthesizer.should_naturalize(response):
                # Extract query from context if available (will be passed separately)
                response = synthesizer.naturalize_if_needed(response, query="", context=None)
        except (ImportError, Exception):
            # Fallback: just strip forensic markers
            response = strip_forensic_format(response)
    
    # Step 1: Strip transmission format
    cleaned = strip_transmission_format(response)
    
    # Step 2: Strip any remaining forensic format markers (fallback)
    cleaned = strip_forensic_format(cleaned)
    
    # Step 3: Fix "designed to" language
    cleaned = fix_designed_language(cleaned)
    
    # Step 4: Detect and flag fake citations
    cleaned, warnings = detect_fake_citations(cleaned)
    
    # Step 5: Clean up excessive whitespace
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    cleaned = cleaned.strip()
    
    return cleaned

