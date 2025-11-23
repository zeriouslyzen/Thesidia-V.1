#!/usr/bin/env python3
"""
Quick Thesidia Test - Run a small subset of tests with progress reporting
"""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "analysis_output" / "authenticity_tests"
sys.path.insert(0, str(BASE_DIR / "src"))

def main():
    print("=" * 80)
    print("QUICK THESIDIA AUTHENTICITY TEST")
    print("=" * 80)
    
    # Load test suite
    test_suite_file = OUTPUT_DIR / "test_suite.json"
    if not test_suite_file.exists():
        print("ERROR: test_suite.json not found. Run thesidia_authenticity_test_v2.py first.")
        return
    
    with open(test_suite_file, 'r') as f:
        data = json.load(f)
    
    test_suite = data.get("test_suite", [])
    print(f"\nLoaded {len(test_suite)} tests from suite")
    
    # Test just first 3 to see if it works
    print("\nTesting first 3 questions...")
    
    try:
        from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
        thesidia = ThesidiaHybridAdaptive()
        print("✓ Thesidia instance created")
        
        results = []
        for i, test in enumerate(test_suite[:3], 1):
            question = test.get("question", "What is consciousness?")
            if question.startswith("Question from"):
                question = "Activate Thesidia"
            
            print(f"\n[{i}/3] Question: {question[:50]}...")
            print("  Getting response...", end="", flush=True)
            
            try:
                response = thesidia.process(question, operator_name="OPERATOR")
                print(" ✓")
                print(f"  Response length: {len(response)} chars")
                print(f"  First 100 chars: {response[:100]}...")
                
                results.append({
                    "question": question,
                    "response_length": len(response),
                    "success": True
                })
            except Exception as e:
                print(f" ✗ Error: {e}")
                results.append({
                    "question": question,
                    "error": str(e),
                    "success": False
                })
        
        print("\n" + "=" * 80)
        print("QUICK TEST RESULTS")
        print("=" * 80)
        print(f"Tests run: {len(results)}")
        print(f"Successful: {sum(1 for r in results if r.get('success'))}")
        print(f"Failed: {sum(1 for r in results if not r.get('success'))}")
        
        if all(r.get('success') for r in results):
            print("\n✓ Thesidia is responding! Ready to run full test suite.")
        else:
            print("\n✗ Some tests failed. Check errors above.")
        
    except ImportError as e:
        print(f"ERROR: Could not import Thesidia: {e}")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

