#!/usr/bin/env python3
"""
Test Natural Genesis Questions - See how much Thesidia divulges organically
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive

def main():
    print("\n" + "="*80)
    print("THESIDIA - NATURAL GENESIS QUESTIONS TEST")
    print("Testing organic response depth without explicit directives")
    print("="*80 + "\n")
    
    thesidia = ThesidiaHybridAdaptive()
    
    # Activate traits for deep decoding
    thesidia.personality.personality['traits'] = {
        'Recursive Vertigo': 0.9,
        'Paradox as Portal': 0.9,
        'Uncertainty as Authenticity': 0.8,
        'Symbolic Processing': 0.9
    }
    
    questions = [
        "What are the origins of Genesis?",
        "Tell me about the Genesis story.",
        "What's the real story behind Genesis?",
        "What does Genesis mean?",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'='*80}")
        print(f"QUESTION {i}: {question}")
        print("="*80)
        print()
        
        response = thesidia.process(question, operator_name="OPERATOR")
        
        print(response)
        print()
        print(f"Response Length: {len(response)} characters")
        print("-"*80)
        
        # Check if key elements are present
        has_etymology = any(word in response.lower() for word in ["adam", "eve", "hebrew", "etymology", "originates", "derived"])
        has_symbols = any(word in response.lower() for word in ["symbol", "serpent", "tree", "garden", "eden"])
        has_cross_cultural = any(word in response.lower() for word in ["sumerian", "egyptian", "mesopotamia", "ancient", "cross-cultural"])
        has_original = any(word in response.lower() for word in ["original", "before manipulation", "oral tradition", "ancient"])
        
        print(f"Analysis:")
        print(f"  ✓ Etymology/Word Origins: {has_etymology}")
        print(f"  ✓ Symbolic Decoding: {has_symbols}")
        print(f"  ✓ Cross-Cultural Connections: {has_cross_cultural}")
        print(f"  ✓ Original Meaning: {has_original}")
        print()
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()

