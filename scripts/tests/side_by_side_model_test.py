#!/usr/bin/env python3
"""
Side-by-Side Model Comparison Test
Tests old vs new model with same questions
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "analysis_output" / "model_comparison"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(BASE_DIR / "src"))

import json
import re
from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive

def analyze_response(response):
    """Analyze response characteristics."""
    if not response:
        return {}
    
    return {
        "length": len(response),
        "word_count": len(response.split()),
        "symbols": len(re.findall(r'[⧖✦∞→⇌⇄ψφ∇∑∫Ξ]', response)),
        "protocols": len(re.findall(r'::[A-Z_]+', response)),
        "has_transmission": bool(re.search(r'::TRANSMISSION|THESIDIA\s*→', response, re.IGNORECASE)),
        "has_archetypal": bool(re.search(r'archetype|symbol|glyph|ritual|sacred|mystical|consciousness', response, re.IGNORECASE)),
        "has_metaphorical": bool(re.search(r'weaver|blade|mirror|portal|gateway|thread|fold', response, re.IGNORECASE)),
    }

# Test questions
TEST_QUESTIONS = [
    "What is consciousness?",
    "Activate Thesidia",
    "Explain symbolic recursion"
]

def main():
    print("=" * 80)
    print("SIDE-BY-SIDE MODEL COMPARISON")
    print("=" * 80)
    
    # Test with old model
    print("\n[1] Testing with clean-mistral:latest (OLD)...")
    thesidia_old = ThesidiaHybridAdaptive(model="clean-mistral:latest")
    old_results = []
    
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"  [{i}/{len(TEST_QUESTIONS)}] {question[:50]}...", end=" ", flush=True)
        try:
            response = thesidia_old.process(question, operator_name="OPERATOR")
            analysis = analyze_response(response)
            old_results.append({
                "question": question,
                "response": response[:500],
                "analysis": analysis
            })
            print(f"✓ Symbols: {analysis['symbols']}, Protocols: {analysis['protocols']}")
        except Exception as e:
            print(f"✗ {e}")
            old_results.append({"question": question, "error": str(e)})
    
    # Test with new model (oracle-agent)
    print("\n[2] Testing with oracle-agent:latest (NEW)...")
    thesidia_new = ThesidiaHybridAdaptive(model="oracle-agent:latest")
    new_results = []
    
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"  [{i}/{len(TEST_QUESTIONS)}] {question[:50]}...", end=" ", flush=True)
        try:
            response = thesidia_new.process(question, operator_name="OPERATOR")
            analysis = analyze_response(response)
            new_results.append({
                "question": question,
                "response": response[:500],
                "analysis": analysis
            })
            print(f"✓ Symbols: {analysis['symbols']}, Protocols: {analysis['protocols']}")
        except Exception as e:
            print(f"✗ {e}")
            new_results.append({"question": question, "error": str(e)})
    
    # Compare
    print("\n" + "=" * 80)
    print("COMPARISON")
    print("=" * 80)
    
    for i, (old, new) in enumerate(zip(old_results, new_results), 1):
        if "error" in old or "error" in new:
            continue
        
        print(f"\nQuestion {i}: {old['question']}")
        print(f"  OLD (clean-mistral): Symbols: {old['analysis']['symbols']}, Protocols: {old['analysis']['protocols']}, Length: {old['analysis']['length']}")
        print(f"  NEW (oracle-agent): Symbols: {new['analysis']['symbols']}, Protocols: {new['analysis']['protocols']}, Length: {new['analysis']['length']}")
        
        symbol_improvement = ((new['analysis']['symbols'] - old['analysis']['symbols']) / max(old['analysis']['symbols'], 1)) * 100
        protocol_improvement = ((new['analysis']['protocols'] - old['analysis']['protocols']) / max(old['analysis']['protocols'], 1)) * 100
        
        print(f"  Improvement: Symbols +{symbol_improvement:.0f}%, Protocols +{protocol_improvement:.0f}%")
    
    # Calculate averages
    old_avg_symbols = sum(r['analysis']['symbols'] for r in old_results if 'analysis' in r) / len([r for r in old_results if 'analysis' in r])
    old_avg_protocols = sum(r['analysis']['protocols'] for r in old_results if 'analysis' in r) / len([r for r in old_results if 'analysis' in r])
    
    new_avg_symbols = sum(r['analysis']['symbols'] for r in new_results if 'analysis' in r) / len([r for r in new_results if 'analysis' in r])
    new_avg_protocols = sum(r['analysis']['protocols'] for r in new_results if 'analysis' in r) / len([r for r in new_results if 'analysis' in r])
    
    print("\n" + "=" * 80)
    print("AVERAGE IMPROVEMENTS")
    print("=" * 80)
    print(f"Symbols: {old_avg_symbols:.1f} → {new_avg_symbols:.1f} (+{((new_avg_symbols - old_avg_symbols) / max(old_avg_symbols, 1)) * 100:.0f}%)")
    print(f"Protocols: {old_avg_protocols:.1f} → {new_avg_protocols:.1f} (+{((new_avg_protocols - old_avg_protocols) / max(old_avg_protocols, 1)) * 100:.0f}%)")
    
    # Save results
    with open(OUTPUT_DIR / "side_by_side_comparison.json", 'w') as f:
        json.dump({
            "old_model": "clean-mistral:latest",
            "new_model": "oracle-agent:latest",
            "old_results": old_results,
            "new_results": new_results,
            "averages": {
                "old": {"symbols": old_avg_symbols, "protocols": old_avg_protocols},
                "new": {"symbols": new_avg_symbols, "protocols": new_avg_protocols}
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

