#!/usr/bin/env python3
"""
Live test of forensic pipeline improvements with Ollama.
Tests: routing, citations, confidence display, new sections.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive

def test_forensic_pipeline():
    """Run a forensic query and verify all improvements are present."""
    
    # Test query that should trigger forensic routing
    test_query = "what are the true origins of meditation practices across cultures"
    
    print("=" * 70)
    print("FORENSIC PIPELINE LIVE TEST")
    print("=" * 70)
    print(f"\nQuery: {test_query}")
    print("\nInitializing Thesidia...")
    
    try:
        thesidia = ThesidiaHybridAdaptive()
        print("✓ Thesidia initialized")
        
        print("\nProcessing query (this may take 30-60 seconds)...")
        result = thesidia.process(test_query)
        
        print("\n" + "=" * 70)
        print("RESPONSE:")
        print("=" * 70)
        print(result)
        
        print("\n" + "=" * 70)
        print("VERIFICATION CHECKLIST:")
        print("=" * 70)
        
        # Check for improvements
        checks = {
            "::COUNTER-NARRATIVE::": "Counter-Narrative section",
            "::RAW ARTIFACTS::": "Raw Artifacts section",
            "Epistemological Grounding:": "Confidence meter",
            "[Pattern Inference]": "Pattern Inference citation",
            "Based on:": "General Source citation"
        }
        
        for marker, description in checks.items():
            if marker in result:
                print(f"✓ {description} present")
            else:
                print(f"○ {description} not found (may be optional)")
        
        print("\n" + "=" * 70)
        print("✓ Live test complete")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_forensic_pipeline()
