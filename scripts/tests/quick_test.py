#!/usr/bin/env python3
"""
Quick test - just 3 prompts to verify Thesidia is working
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive

# Just 3 quick tests
TEST_PROMPTS = [
    "hello",
    "What is consciousness?",
    "Activate Thesidia",
]

def main():
    print("Quick Thesidia Test")
    print("=" * 60)
    
    try:
        thesidia = ThesidiaHybridAdaptive(model="oracle-agent:latest")
        thesidia.load_state()
        print("✓ Thesidia initialized\n")
        
        for i, prompt in enumerate(TEST_PROMPTS, 1):
            print(f"\n[{i}] {prompt}")
            print("-" * 60)
            try:
                response = thesidia.process(prompt, operator_name="OPERATOR")
                print(f"Length: {len(response)} chars")
                print(f"Response:\n{response[:400]}...")
                print()
            except Exception as e:
                print(f"ERROR: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n✓ Test complete")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

