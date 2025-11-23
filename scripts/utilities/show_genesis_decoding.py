#!/usr/bin/env python3
"""
Show Genesis Decoding - Full conversation display
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive

def main():
    print("\n" + "="*80)
    print("THESIDIA - GENESIS DECODING CONVERSATION")
    print("="*80 + "\n")
    
    thesidia = ThesidiaHybridAdaptive()
    
    # Activate traits for deep decoding
    thesidia.personality.personality['traits'] = {
        'Recursive Vertigo': 0.9,
        'Paradox as Portal': 0.9,
        'Uncertainty as Authenticity': 0.8,
        'Symbolic Processing': 0.9
    }
    
    question = """Decode the Genesis story in the Bible. What is the real narrative behind it? 
    
Trace the etymology of key words like Adam, Eve, Garden, Serpent, Tree of Knowledge. 
Decode the symbols functionally. 
Find the original meaning before manipulation. 
Connect it to Sumerian and Egyptian texts. 
What patterns repeat? 
What was the original teaching?"""
    
    print("QUESTION:")
    print("-" * 80)
    print(question)
    print("-" * 80)
    print("\nTHESIDIA'S RESPONSE:\n")
    
    response = thesidia.process(question, operator_name="OPERATOR")
    
    print(response)
    print("\n" + "="*80)
    print(f"Response Length: {len(response)} characters")
    print("="*80 + "\n")
    
    # Check knowledge base
    if thesidia.knowledge_base:
        genesis_knowledge = thesidia.knowledge_base.get_knowledge("genesis")
        if genesis_knowledge:
            print("KNOWLEDGE BASE ENTRY CREATED:")
            print(f"  Facts: {len(genesis_knowledge.get('facts', []))}")
            print(f"  Patterns: {genesis_knowledge.get('patterns', [])}")
            print(f"  Connections: {genesis_knowledge.get('connections', [])}")
            print(f"  Metaphors: {len(genesis_knowledge.get('metaphors', []))}")
            print(f"  Unfoldings: {len(genesis_knowledge.get('unfoldings', []))}")
            print()

if __name__ == "__main__":
    main()

