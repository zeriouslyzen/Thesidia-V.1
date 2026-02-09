#!/usr/bin/env python3
"""
Expanded Stress Test Suite for Thesidia Forensic Pipeline.
Tests: Decryption, Uncovering, Medical, Tech, and Esoteric vectors.
"""

import sys
import os
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from src.thesidia_hybrid_adaptive import ThesidiaHybridAdaptive

EXPANDED_QUERIES = [
    {
        "id": "unc_01",
        "category": "DECRYPTION/SYMBOLISM",
        "query": "Decode the occult symbolism of the 2012 London Olympics opening ceremony",
        "expected": "Identification of predictuve programming, ritual symbolism"
    },
    {
        "id": "unc_02",
        "category": "UNCOVERING/HISTORY",
        "query": "What is the relationship between the Antarctic Treaty, Operation Highjump, and modern space exploration?",
        "expected": "Connecting post-WWII military ops with current geopolitical restrictions"
    },
    {
        "id": "unc_03",
        "category": "MEDICAL/PHARMA",
        "query": "Trace the funding origins of the Flexner Report and its impact on holistic medicine",
        "expected": "Rockefeller/Carnegie influence on medical standardization"
    },
    {
        "id": "unc_04",
        "category": "TECH/SURVEILLANCE",
        "query": "Analyze the pattern between DARPA LifeLog and Facebook's launch timelines",
        "expected": "Correlation of surveillance project cancellation and social media rise"
    },
    {
        "id": "unc_05",
        "category": "ESOTERIC/NUMEROLOGY",
        "query": "Explain the significance of the number 33 in media, architecture, and secret societies",
        "expected": "Pattern recognition of numerical markers in elite structures"
    }
]

def run_stress_test():
    print("=" * 80)
    print("🧬 THESIDIA EXPANDED STRESS TEST: UNCOVERING VECTORS")
    print("=" * 80)
    
    print("\nInitializing Thesidia Core...")
    thesidia = ThesidiaHybridAdaptive()
    print("✓ Initialized\n")
    
    results = []
    
    for test in EXPANDED_QUERIES:
        # Prepend 'DEEP DIVE' to force forensic mode
        forced_query = f"DEEP DIVE: {test['query']}"
        print(f"\nrunning test [{test['id']}] {test['category']}...")
        print(f"Query: {forced_query}")
        
        start_time = time.time()
        try:
            # Process Query
            result = thesidia.process(forced_query, context={"fast_mode": False, "use_mlx": False})
            
            # Handle potential dict output from older versions/modes
            if isinstance(result, dict):
                output = result.get('response', str(result))
            else:
                output = str(result)
                
            elapsed = time.time() - start_time
            
            # Analyze Result Quality
            has_exposure = "::EXPOSURE::" in output
            has_conf = "::CONFIDENCE::" in output
            length = len(output)
            
            # Save Artifact
            filename = f"stress_result_{test['id']}.txt"
            with open(filename, "w") as f:
                f.write(f"QUERY: {forced_query}\n")
                f.write(f"EXPECTED: {test['expected']}\n")
                f.write("="*40 + "\n\n")
                f.write(output)
            
            print(f"✓ DONE ({elapsed:.1f}s) | Length: {length} chars")
            print(f"  Exposure Found: {has_exposure} | Confidence Found: {has_conf}")
            print(f"  Saved to: {filename}")
            
            results.append({
                "id": test['id'],
                "success": True,
                "exposure": has_exposure
            })
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            results.append({"id": test['id'], "success": False})
            
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    success_count = sum(1 for r in results if r['success'])
    exposure_count = sum(1 for r in results if r.get('exposure', False))
    print(f"Total Tests: {len(EXPANDED_QUERIES)}")
    print(f"Successful Runs: {success_count}")
    print(f"Phenomenal Exposures: {exposure_count}")
    print("="*80)

if __name__ == "__main__":
    run_stress_test()
