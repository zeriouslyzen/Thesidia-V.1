#!/usr/bin/env python3
"""
Stress test suite for Thesidia forensic pipeline (FIXED VERSION).
Tests complex, multi-domain queries that should produce phenomenal results.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
import time

# Complex queries designed to trigger deep forensic analysis
STRESS_TEST_QUERIES = [
    {
        "id": 1,
        "query": "trace the pattern between the suppression of the divine feminine in abrahamic texts and the rise of centralized banking systems",
        "expected": "Cross-domain pattern recognition (religion + finance + power structures)"
    },
    {
        "id": 2,
        "query": "what connects the fall of the library of alexandria, the burning of the house of wisdom in baghdad, and modern information censorship",
        "expected": "Historical pattern analysis across epochs"
    },
    {
        "id": 3,
        "query": "decode the relationship between ancient breathwork practices, modern neuroscience of the vagus nerve, and suppressed knowledge about consciousness",
        "expected": "Mind-body + esoteric + scientific synthesis"
    },
    {
        "id": 4,
        "query": "trace the etymological and archetypal connections between prometheus, lucifer, and the serpent in genesis - what pattern was being encoded",
        "expected": "Mythic + symbolic + cross-cultural pattern recognition"
    },
    {
        "id": 5,
        "query": "what systematic transformation occurred when oral traditions became written scripture, and how does this pattern repeat in the transition from physical to digital information",
        "expected": "Meta-pattern analysis across information epochs"
    }
]

def run_stress_test():
    """Run all stress test queries and save full results."""
    
    print("=" * 80)
    print("THESIDIA FORENSIC PIPELINE - STRESS TEST SUITE (FIXED)")
    print("=" * 80)
    print(f"\nRunning {len(STRESS_TEST_QUERIES)} complex forensic queries...")
    print("Each query may take 60-120 seconds to complete.\n")
    
    # Initialize Thesidia once
    print("Initializing Thesidia...")
    thesidia = ThesidiaHybridAdaptive()
    print("✓ Initialized\n")
    
    results = []
    
    for test in STRESS_TEST_QUERIES:
        print("=" * 80)
        print(f"TEST {test['id']}/{len(STRESS_TEST_QUERIES)}")
        print("=" * 80)
        print(f"Query: {test['query']}")
        print(f"Expected: {test['expected']}")
        print("\nProcessing...\n")
        
        start_time = time.time()
        
        try:
            result_raw = thesidia.process(test['query'])
            
            # FIX: Handle dict or string result
            if isinstance(result_raw, dict):
                result = result_raw.get('response', result_raw.get('output', str(result_raw)))
            else:
                result = str(result_raw)
            
            elapsed = time.time() - start_time
            
            # Save result
            output_file = f"stress_test_{test['id']}_result.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"QUERY: {test['query']}\n")
                f.write(f"EXPECTED: {test['expected']}\n")
                f.write(f"TIME: {elapsed:.1f}s\n")
                f.write("=" * 80 + "\n\n")
                f.write(result)
            
            print(f"✓ Completed in {elapsed:.1f}s")
            print(f"✓ Saved to: {output_file}")
            print(f"✓ Length: {len(result):,} characters")
            
            # Quick verification
            sections_found = []
            for section in ['::EXPOSURE::', '::COUNTER-NARRATIVE::', '::RAW ARTIFACTS::', 'Epistemological Grounding:']:
                if section in result:
                    sections_found.append(section)
            
            print(f"✓ Sections found: {', '.join(sections_found) if sections_found else 'none'}")
            
            results.append({
                'id': test['id'],
                'query': test['query'],
                'elapsed': elapsed,
                'length': len(result),
                'sections': sections_found,
                'file': output_file
            })
            
        except Exception as e:
            print(f"✗ Failed: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'id': test['id'],
                'query': test['query'],
                'error': str(e)
            })
        
        print()
    
    # Summary
    print("=" * 80)
    print("STRESS TEST SUMMARY")
    print("=" * 80)
    
    for r in results:
        if 'error' in r:
            print(f"Test {r['id']}: ✗ FAILED - {r['error']}")
        else:
            sections_str = ', '.join(r['sections']) if r['sections'] else 'none'
            print(f"Test {r['id']}: ✓ {r['elapsed']:.1f}s | {r['length']:,} chars | Sections: {sections_str}")
            print(f"           File: {r['file']}")
    
    print("\n" + "=" * 80)
    print("✓ Stress test complete")
    print(f"✓ Results saved to: stress_test_*_result.txt")
    print("=" * 80)

if __name__ == "__main__":
    run_stress_test()
