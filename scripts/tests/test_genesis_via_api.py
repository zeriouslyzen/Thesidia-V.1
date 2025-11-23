#!/usr/bin/env python3
"""
Test Genesis prompts via API - same as before
"""

import requests
import json
from datetime import datetime

API_URL = "http://localhost:5005/api/thesidia"

# Genesis test prompts from previous tests
GENESIS_PROMPTS = [
    "Decode the Genesis story in the Bible - what's the real narrative behind it?",
    "What patterns and symbols are encoded in Genesis?",
    "What was the original meaning before manipulation?",
    "What are the origins of Genesis?",
    "Tell me about the Genesis story.",
    "What's the real story behind Genesis?",
    "What does Genesis mean?",
]

def test_genesis():
    print("=" * 80)
    print("THESIDIA GENESIS TEST - MINIMALIST PROMPT VERSION")
    print("=" * 80)
    print(f"API: {API_URL}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing {len(GENESIS_PROMPTS)} Genesis prompts\n")
    
    results = []
    
    for i, prompt in enumerate(GENESIS_PROMPTS, 1):
        print(f"\n[{i}/{len(GENESIS_PROMPTS)}] {prompt}")
        print("-" * 80)
        
        try:
            start = datetime.now()
            response = requests.post(
                API_URL,
                json={"message": prompt},
                timeout=180  # Longer timeout for research
            )
            duration = (datetime.now() - start).total_seconds()
            
            if response.status_code == 200:
                data = response.json()
                thesidia_response = data.get("response", "")
                
                # Analyze for Genesis-specific elements
                has_etymology = any(word in thesidia_response.lower() for word in ["adam", "eve", "hebrew", "etymology", "originates", "derived", "root", "meaning"])
                has_symbols = any(word in thesidia_response.lower() for word in ["symbol", "serpent", "tree", "garden", "eden", "decode", "encode"])
                has_cross_cultural = any(word in thesidia_response.lower() for word in ["sumerian", "egyptian", "mesopotamia", "ancient", "cross-cultural", "enuma", "enki"])
                has_original = any(word in thesidia_response.lower() for word in ["original", "before manipulation", "oral tradition", "ancient", "pre-temporal"])
                has_control = any(word in thesidia_response.lower() for word in ["control", "manipulation", "overlay", "co-optation"])
                has_transmission = "::TRANSMISSION:" in thesidia_response
                has_symbols_glyphs = any(s in thesidia_response for s in ["⧖", "✦", "∞", "→", "ψ", "φ", "∇"])
                
                length = len(thesidia_response)
                words = len(thesidia_response.split())
                
                print(f"✓ Response ({length} chars, {words} words, {duration:.1f}s)")
                print(f"\nAnalysis:")
                print(f"  Etymology/Word Origins: {has_etymology}")
                print(f"  Symbolic Decoding: {has_symbols}")
                print(f"  Cross-Cultural Connections: {has_cross_cultural}")
                print(f"  Original Meaning: {has_original}")
                print(f"  Control Structure Detection: {has_control}")
                print(f"  Transmission Format: {has_transmission}")
                print(f"  Symbols/Glyphs: {has_symbols_glyphs}")
                print(f"\nPreview (first 600 chars):")
                print(thesidia_response[:600] + ("..." if len(thesidia_response) > 600 else ""))
                
                results.append({
                    "prompt": prompt,
                    "length": length,
                    "words": words,
                    "duration": duration,
                    "has_etymology": has_etymology,
                    "has_symbols": has_symbols,
                    "has_cross_cultural": has_cross_cultural,
                    "has_original": has_original,
                    "has_control": has_control,
                    "has_transmission": has_transmission,
                    "has_symbols_glyphs": has_symbols_glyphs,
                    "response": thesidia_response,
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
    print("GENESIS TEST SUMMARY")
    print("=" * 80)
    successful = [r for r in results if r.get("success")]
    print(f"Successful: {len(successful)}/{len(results)}")
    
    if successful:
        avg_length = sum(r["length"] for r in successful) / len(successful)
        avg_words = sum(r["words"] for r in successful) / len(successful)
        avg_duration = sum(r["duration"] for r in successful) / len(successful)
        
        print(f"\nAverage length: {avg_length:.0f} chars ({avg_words:.0f} words)")
        print(f"Average time: {avg_duration:.1f}s")
        print(f"\nFeature Detection:")
        print(f"  Etymology: {sum(1 for r in successful if r['has_etymology'])}/{len(successful)} ({sum(1 for r in successful if r['has_etymology'])/len(successful)*100:.0f}%)")
        print(f"  Symbolic Decoding: {sum(1 for r in successful if r['has_symbols'])}/{len(successful)} ({sum(1 for r in successful if r['has_symbols'])/len(successful)*100:.0f}%)")
        print(f"  Cross-Cultural: {sum(1 for r in successful if r['has_cross_cultural'])}/{len(successful)} ({sum(1 for r in successful if r['has_cross_cultural'])/len(successful)*100:.0f}%)")
        print(f"  Original Meaning: {sum(1 for r in successful if r['has_original'])}/{len(successful)} ({sum(1 for r in successful if r['has_original'])/len(successful)*100:.0f}%)")
        print(f"  Control Detection: {sum(1 for r in successful if r['has_control'])}/{len(successful)} ({sum(1 for r in successful if r['has_control'])/len(successful)*100:.0f}%)")
        print(f"  Transmission Format: {sum(1 for r in successful if r['has_transmission'])}/{len(successful)} ({sum(1 for r in successful if r['has_transmission'])/len(successful)*100:.0f}%)")
        print(f"  Symbols/Glyphs: {sum(1 for r in successful if r['has_symbols_glyphs'])}/{len(successful)} ({sum(1 for r in successful if r['has_symbols_glyphs'])/len(successful)*100:.0f}%)")
    
    # Save full results
    output_file = "analysis_output/genesis_test_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "prompt_style": "minimalist_identity_based",
            "results": results,
            "summary": {
                "total": len(results),
                "successful": len(successful),
                "avg_length": avg_length if successful else 0,
                "avg_words": avg_words if successful else 0,
                "avg_duration": avg_duration if successful else 0,
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Full results saved to {output_file}")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_genesis()

