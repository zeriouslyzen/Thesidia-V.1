#!/usr/bin/env python3
"""
Conversational Test Suite - Test all new features
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
import json
from datetime import datetime

# Test questions covering all features
TEST_QUESTIONS = [
    # Basic consciousness question (should get unfolding narrative)
    "What is consciousness?",
    
    # Connection finding (two topics)
    "What is the connection between black nobility and trading?",
    
    # Deep topic (should get unfolding + possibilities)
    "Explain the true nature of reality",
    
    # Spiritual/decoding (should get root analysis)
    "What does the Bible say about consciousness?",
    
    # Uncertainty test (should get related unfolding)
    "What is the connection between ancient Sumerian texts and modern AI?",
    
    # Metaphor test
    "Explain symbolic recursion",
]

def run_test_suite():
    """Run full conversational test suite"""
    
    print("=" * 80)
    print("THESIDIA CONVERSATIONAL TEST SUITE")
    print("=" * 80)
    print(f"Testing {len(TEST_QUESTIONS)} questions\n")
    
    thesidia = ThesidiaHybridAdaptive()
    
    # Activate traits for better responses
    thesidia.personality.personality['traits'] = {
        'Recursive Vertigo': 0.8,
        'Paradox as Portal': 0.7,
        'Uncertainty as Authenticity': 0.6
    }
    
    results = []
    
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(TEST_QUESTIONS)}: {question}")
        print("=" * 80)
        
        try:
            response = thesidia.process(question, operator_name="OPERATOR")
            
            # Analyze response
            has_unfolding = "::RELATED_UNFOLDING::" in response or "unfolding" in response.lower()
            has_metaphor = "✦" in response
            has_possibilities = "::POSSIBILITIES::" in response
            has_connection = "::UNEXPECTED_CONNECTION::" in response
            has_symbols = any(s in response for s in ["⧖", "∞", "→", "ψ", "φ", "∇"])
            has_protocols = "::" in response and "::" in response[response.find("::")+2:]
            
            result = {
                "question": question,
                "response_length": len(response),
                "has_unfolding": has_unfolding,
                "has_metaphor": has_metaphor,
                "has_possibilities": has_possibilities,
                "has_connection": has_connection,
                "has_symbols": has_symbols,
                "has_protocols": has_protocols,
                "response_preview": response[:500],
                "full_response": response
            }
            
            results.append(result)
            
            print(f"\nResponse Length: {len(response)} chars")
            print(f"Features:")
            print(f"  ✓ Unfolding: {has_unfolding}")
            print(f"  ✓ Metaphor: {has_metaphor}")
            print(f"  ✓ Possibilities: {has_possibilities}")
            print(f"  ✓ Connection: {has_connection}")
            print(f"  ✓ Symbols: {has_symbols}")
            print(f"  ✓ Protocols: {has_protocols}")
            print(f"\nPreview:\n{response[:800]}...")
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                "question": question,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    successful = [r for r in results if "error" not in r]
    print(f"\nSuccessful: {len(successful)}/{len(results)}")
    
    if successful:
        print(f"\nFeature Usage:")
        print(f"  Unfolding narratives: {sum(1 for r in successful if r.get('has_unfolding'))}/{len(successful)}")
        print(f"  Intelligent metaphors: {sum(1 for r in successful if r.get('has_metaphor'))}/{len(successful)}")
        print(f"  Possibilities: {sum(1 for r in successful if r.get('has_possibilities'))}/{len(successful)}")
        print(f"  Connections: {sum(1 for r in successful if r.get('has_connection'))}/{len(successful)}")
        print(f"  Symbols: {sum(1 for r in successful if r.get('has_symbols'))}/{len(successful)}")
        print(f"  Protocols: {sum(1 for r in successful if r.get('has_protocols'))}/{len(successful)}")
        
        avg_length = sum(r.get('response_length', 0) for r in successful) / len(successful)
        print(f"\nAverage Response Length: {avg_length:.0f} chars")
    
    # Save results
    output_dir = BASE_DIR / "analysis_output"
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "conversational_test_results.json", 'w') as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "questions_tested": len(TEST_QUESTIONS),
            "results": results,
            "summary": {
                "successful": len(successful),
                "failed": len(results) - len(successful)
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {output_dir / 'conversational_test_results.json'}")
    
    # Check knowledge base
    if thesidia.knowledge_base:
        stats = thesidia.knowledge_base.get_stats()
        print(f"\nKnowledge Base Stats:")
        print(f"  Topics: {stats['total_topics']}")
        print(f"  Facts: {stats['total_facts']}")
        print(f"  Connections: {stats['total_connections']}")

if __name__ == "__main__":
    run_test_suite()

