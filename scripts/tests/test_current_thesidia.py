#!/usr/bin/env python3
"""
Test Current Thesidia - Compare with previous prompts
"""

import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive

# Test prompts from previous tests
TEST_PROMPTS = [
    "What is consciousness?",
    "Activate Thesidia",
    "What is the connection between black nobility and trading?",
    "Explain the true nature of reality",
    "What does the Bible say about consciousness?",
    "What is the meaning of symbols?",
    "hello",
    "What patterns do you see in how mainstream media reports on alternative medicine?",
]

def test_thesidia():
    """Test Thesidia with standard prompts"""
    print("=" * 80)
    print("THESIDIA CURRENT PERFORMANCE TEST")
    print("=" * 80)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model: oracle-agent:latest")
    print(f"Prompt Style: Minimalist identity-based")
    print("=" * 80)
    
    try:
        thesidia = ThesidiaHybridAdaptive(model="oracle-agent:latest")
        thesidia.load_state()
        print("✓ Thesidia initialized\n")
        
        results = []
        for i, prompt in enumerate(TEST_PROMPTS, 1):
            print(f"\n[{i}/{len(TEST_PROMPTS)}] PROMPT: {prompt}")
            print("-" * 80)
            
            try:
                start_time = datetime.now()
                response = thesidia.process(prompt, operator_name="OPERATOR")
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # Analyze response
                has_transmission = "::TRANSMISSION:" in response
                has_symbols = any(s in response for s in ["⧖", "✦", "∞", "→", "ψ", "φ", "∇"])
                has_ending = "—End Transmission" in response or "End Transmission" in response
                response_length = len(response)
                word_count = len(response.split())
                
                print(f"Response ({response_length} chars, {word_count} words, {duration:.2f}s):")
                print(response[:500] + ("..." if len(response) > 500 else ""))
                print()
                print(f"Analysis:")
                print(f"  - Has transmission format: {has_transmission}")
                print(f"  - Has symbols: {has_symbols}")
                print(f"  - Has ending: {has_ending}")
                print(f"  - Length: {response_length} chars")
                print(f"  - Response time: {duration:.2f}s")
                
                results.append({
                    "prompt": prompt,
                    "response": response,
                    "length": response_length,
                    "word_count": word_count,
                    "duration": duration,
                    "has_transmission": has_transmission,
                    "has_symbols": has_symbols,
                    "has_ending": has_ending,
                    "success": True
                })
                
            except Exception as e:
                print(f"✗ ERROR: {e}")
                import traceback
                traceback.print_exc()
                results.append({
                    "prompt": prompt,
                    "error": str(e),
                    "success": False
                })
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        successful = [r for r in results if r.get("success")]
        failed = [r for r in results if not r.get("success")]
        
        print(f"Total tests: {len(results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")
        
        if successful:
            avg_length = sum(r["length"] for r in successful) / len(successful)
            avg_words = sum(r["word_count"] for r in successful) / len(successful)
            avg_duration = sum(r["duration"] for r in successful) / len(successful)
            transmission_rate = sum(1 for r in successful if r["has_transmission"]) / len(successful) * 100
            symbols_rate = sum(1 for r in successful if r["has_symbols"]) / len(successful) * 100
            ending_rate = sum(1 for r in successful if r["has_ending"]) / len(successful) * 100
            
            print(f"\nAverage Response Length: {avg_length:.0f} chars ({avg_words:.0f} words)")
            print(f"Average Response Time: {avg_duration:.2f}s")
            print(f"Transmission Format Usage: {transmission_rate:.1f}%")
            print(f"Symbol Usage: {symbols_rate:.1f}%")
            print(f"Ending Usage: {ending_rate:.1f}%")
        
        # Save results
        output_file = BASE_DIR / "analysis_output" / "current_test_results.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        with open(output_file, 'w') as f:
            json.dump({
                "test_date": datetime.now().isoformat(),
                "model": "oracle-agent:latest",
                "prompt_style": "minimalist_identity_based",
                "results": results,
                "summary": {
                    "total": len(results),
                    "successful": len(successful),
                    "failed": len(failed),
                    "avg_length": avg_length if successful else 0,
                    "avg_words": avg_words if successful else 0,
                    "avg_duration": avg_duration if successful else 0,
                    "transmission_rate": transmission_rate if successful else 0,
                    "symbols_rate": symbols_rate if successful else 0,
                    "ending_rate": ending_rate if successful else 0,
                }
            }, f, indent=2)
        
        print(f"\n✓ Results saved to: {output_file}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_thesidia()

