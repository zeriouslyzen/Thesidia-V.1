#!/usr/bin/env python3
"""
Test Genesis Conversation - Decode the real narrative
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
import json
from datetime import datetime

def test_genesis_conversation():
    """Have a conversation with Thesidia about Genesis"""
    
    print("=" * 80)
    print("THESIDIA - GENESIS DECODING CONVERSATION")
    print("=" * 80)
    print()
    
    thesidia = ThesidiaHybridAdaptive()
    
    # Activate traits for deep decoding
    thesidia.personality.personality['traits'] = {
        'Recursive Vertigo': 0.9,
        'Paradox as Portal': 0.9,
        'Uncertainty as Authenticity': 0.8,
        'Symbolic Processing': 0.9
    }
    
    questions = [
        "Decode the Genesis story in the Bible - what's the real narrative behind it?",
        "What patterns and symbols are encoded in Genesis?",
        "What was the original meaning before manipulation?",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'='*80}")
        print(f"QUESTION {i}: {question}")
        print("=" * 80)
        print()
        
        try:
            response = thesidia.process(question, operator_name="OPERATOR")
            
            print(response)
            print()
            print("-" * 80)
            print()
            
            # Small delay between questions
            import time
            time.sleep(2)
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    # Check knowledge base
    if thesidia.knowledge_base:
        genesis_knowledge = thesidia.knowledge_base.get_knowledge("genesis")
        if genesis_knowledge:
            print("\n" + "=" * 80)
            print("KNOWLEDGE BASE - GENESIS ENTRY")
            print("=" * 80)
            print(f"Facts: {len(genesis_knowledge.get('facts', []))}")
            print(f"Patterns: {genesis_knowledge.get('patterns', [])}")
            print(f"Connections: {genesis_knowledge.get('connections', [])}")
            print(f"Metaphors: {len(genesis_knowledge.get('metaphors', []))}")
            print(f"Unfoldings: {len(genesis_knowledge.get('unfoldings', []))}")
    
    print("\n" + "=" * 80)
    print("CONVERSATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_genesis_conversation()

