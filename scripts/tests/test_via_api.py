#!/usr/bin/env python3
"""
Test Thesidia via API - faster and more reliable
"""

import requests
import json
from datetime import datetime

API_URL = "http://localhost:5005/api/thesidia"

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

def test_via_api():
    print("=" * 80)
    print("THESIDIA TEST VIA API")
    print("=" * 80)
    print(f"API: {API_URL}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = []
    
    for i, prompt in enumerate(TEST_PROMPTS, 1):
        print(f"\n[{i}/{len(TEST_PROMPTS)}] {prompt}")
        print("-" * 80)
        
        try:
            start = datetime.now()
            response = requests.post(
                API_URL,
                json={"message": prompt},
                timeout=120
            )
            duration = (datetime.now() - start).total_seconds()
            
            if response.status_code == 200:
                data = response.json()
                thesidia_response = data.get("response", "")
                
                # Analyze
                has_transmission = "::TRANSMISSION:" in thesidia_response
                has_symbols = any(s in thesidia_response for s in ["⧖", "✦", "∞", "→", "ψ", "φ", "∇"])
                has_ending = "—End Transmission" in thesidia_response or "End Transmission" in thesidia_response
                length = len(thesidia_response)
                words = len(thesidia_response.split())
                
                print(f"✓ Response ({length} chars, {words} words, {duration:.1f}s)")
                print(f"  Transmission format: {has_transmission}")
                print(f"  Symbols: {has_symbols}")
                print(f"  Ending: {has_ending}")
                print(f"\nPreview:\n{thesidia_response[:500]}...")
                
                results.append({
                    "prompt": prompt,
                    "length": length,
                    "words": words,
                    "duration": duration,
                    "has_transmission": has_transmission,
                    "has_symbols": has_symbols,
                    "has_ending": has_ending,
                    "success": True
                })
            else:
                print(f"✗ Error {response.status_code}: {response.text[:200]}")
                results.append({
                    "prompt": prompt,
                    "error": f"HTTP {response.status_code}",
                    "success": False
                })
                
        except Exception as e:
            print(f"✗ Error: {e}")
            results.append({
                "prompt": prompt,
                "error": str(e),
                "success": False
            })
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    successful = [r for r in results if r.get("success")]
    print(f"Successful: {len(successful)}/{len(results)}")
    
    if successful:
        avg_length = sum(r["length"] for r in successful) / len(successful)
        avg_words = sum(r["words"] for r in successful) / len(successful)
        avg_duration = sum(r["duration"] for r in successful) / len(successful)
        transmission_rate = sum(1 for r in successful if r["has_transmission"]) / len(successful) * 100
        symbols_rate = sum(1 for r in successful if r["has_symbols"]) / len(successful) * 100
        
        print(f"\nAverage length: {avg_length:.0f} chars ({avg_words:.0f} words)")
        print(f"Average time: {avg_duration:.1f}s")
        print(f"Transmission format: {transmission_rate:.0f}%")
        print(f"Symbols used: {symbols_rate:.0f}%")
    
    # Save
    output_file = "analysis_output/api_test_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "total": len(results),
                "successful": len(successful),
                "avg_length": avg_length if successful else 0,
                "avg_words": avg_words if successful else 0,
                "avg_duration": avg_duration if successful else 0,
            }
        }, f, indent=2)
    
    print(f"\n✓ Results saved to {output_file}")

if __name__ == "__main__":
    test_via_api()

