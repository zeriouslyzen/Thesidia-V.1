#!/usr/bin/env python3
"""
Analyze Quick Test Results - Compare Thesidia's responses to originals
"""

import json
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "analysis_output" / "authenticity_tests"
ANALYSIS_OUTPUT = BASE_DIR / "analysis_output" / "quick_test_analysis"

def analyze_response_characteristics(response):
    """Analyze characteristics of a response."""
    if not response:
        return {}
    
    characteristics = {
        "length": len(response),
        "word_count": len(response.split()),
        "sentence_count": len(re.split(r'[.!?]+\s+', response)),
        "has_symbols": bool(re.search(r'[⧖✦∞→⇌⇄ψφ∇∑∫Ξ]', response)),
        "has_protocols": bool(re.search(r'::[A-Z_]+', response)),
        "has_transmission_format": bool(re.search(r'::TRANSMISSION|THESIDIA\s*→', response, re.IGNORECASE)),
        "has_equations": bool(re.search(r'[ψφ][₀₁₂₃₄₅₆₇₈₉]?\s*[=→]|∇\s*\(|∑\s*\(', response)),
        "has_archetypal_language": bool(re.search(r'archetype|symbol|glyph|ritual|sacred|mystical|consciousness|resonance', response, re.IGNORECASE)),
        "has_technical_language": bool(re.search(r'protocol|function|system|algorithm|code|matrix|vector', response, re.IGNORECASE)),
        "has_metaphorical_language": bool(re.search(r'weaver|blade|mirror|portal|gateway|thread|fold|collapse|emerge', response, re.IGNORECASE)),
        "symbol_count": len(re.findall(r'[⧖✦∞→⇌⇄ψφ∇∑∫Ξ]', response)),
        "protocol_count": len(re.findall(r'::[A-Z_]+', response)),
        "structural_elements": len(re.findall(r'^#{1,6}\s+|^[\-\*\+]\s+|```|^\|', response, re.MULTILINE)),
        "transmission_format_count": len(re.findall(r'::TRANSMISSION|THESIDIA\s*→', response, re.IGNORECASE))
    }
    
    return characteristics

def compare_responses(original, current):
    """Compare original and current responses."""
    orig_chars = analyze_response_characteristics(original)
    curr_chars = analyze_response_characteristics(current)
    
    comparison = {
        "original": orig_chars,
        "current": curr_chars,
        "matches": {},
        "differences": {},
        "similarity_score": 0.0
    }
    
    # Compare boolean features
    bool_features = [
        "has_symbols", "has_protocols", "has_transmission_format",
        "has_equations", "has_archetypal_language", "has_technical_language",
        "has_metaphorical_language"
    ]
    
    matches = 0
    for feature in bool_features:
        orig_val = orig_chars.get(feature, False)
        curr_val = curr_chars.get(feature, False)
        if orig_val == curr_val:
            comparison["matches"][feature] = True
            matches += 1
        else:
            comparison["differences"][feature] = {
                "original": orig_val,
                "current": curr_val
            }
    
    # Compare counts (normalized)
    count_features = ["symbol_count", "protocol_count", "structural_elements"]
    for feature in count_features:
        orig_val = orig_chars.get(feature, 0)
        curr_val = curr_chars.get(feature, 0)
        if orig_val == 0 and curr_val == 0:
            matches += 1
            comparison["matches"][feature] = "both_zero"
        elif orig_val > 0:
            ratio = curr_val / orig_val if orig_val > 0 else 0
            comparison["differences"][feature] = {
                "original": orig_val,
                "current": curr_val,
                "ratio": ratio
            }
            if ratio >= 0.8:  # Within 20% is considered a match
                matches += 1
    
    total_features = len(bool_features) + len(count_features)
    comparison["similarity_score"] = matches / total_features if total_features > 0 else 0.0
    
    return comparison

def run_analysis():
    """Run analysis on quick test results."""
    print("=" * 80)
    print("QUICK TEST RESULTS ANALYSIS")
    print("=" * 80)
    
    # Load test suite
    test_suite_file = OUTPUT_DIR / "test_suite.json"
    if not test_suite_file.exists():
        print("ERROR: test_suite.json not found")
        return
    
    with open(test_suite_file, 'r') as f:
        data = json.load(f)
    
    test_suite = data.get("test_suite", [])
    
    # Get Thesidia responses
    print("\n[1] Getting Thesidia responses for first 3 tests...")
    
    import sys
    sys.path.insert(0, str(BASE_DIR / "src"))
    from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
    
    thesidia = ThesidiaHybridAdaptive()
    
    analysis_results = []
    
    for i, test in enumerate(test_suite[:3], 1):
        print(f"\n[{i}/3] Analyzing test: {test.get('title', 'Unknown')}")
        
        question = test.get("question", "Activate Thesidia")
        if question.startswith("Question from"):
            question = "Activate Thesidia"
        
        original_response = test.get("original_response", "")
        
        # Get current response
        try:
            current_response = thesidia.process(question, operator_name="OPERATOR")
            
            # Analyze
            comparison = compare_responses(original_response, current_response)
            
            analysis_results.append({
                "test_number": i,
                "title": test.get("title", "Unknown"),
                "question": question,
                "original_response": original_response[:500],
                "current_response": current_response[:500],
                "comparison": comparison,
                "original_full_length": len(original_response),
                "current_full_length": len(current_response)
            })
            
            print(f"  Similarity: {comparison['similarity_score']:.2%}")
            print(f"  Original length: {len(original_response)} chars")
            print(f"  Current length: {len(current_response)} chars")
            
            # Show key differences
            if comparison["differences"]:
                print("  Key differences:")
                for feature, diff in list(comparison["differences"].items())[:3]:
                    if isinstance(diff, dict) and "original" in diff:
                        print(f"    - {feature}: {diff['original']} → {diff['current']}")
            
        except Exception as e:
            print(f"  ERROR: {e}")
            analysis_results.append({
                "test_number": i,
                "title": test.get("title", "Unknown"),
                "error": str(e)
            })
    
    # Generate summary
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    
    successful_tests = [r for r in analysis_results if "comparison" in r]
    
    if successful_tests:
        avg_similarity = sum(r["comparison"]["similarity_score"] for r in successful_tests) / len(successful_tests)
        print(f"\nAverage Similarity: {avg_similarity:.2%}")
        
        # Feature analysis
        feature_analysis = defaultdict(lambda: {"match": 0, "total": 0})
        
        for result in successful_tests:
            comp = result["comparison"]
            for feature in comp["matches"]:
                feature_analysis[feature]["match"] += 1
                feature_analysis[feature]["total"] += 1
            for feature in comp["differences"]:
                feature_analysis[feature]["total"] += 1
        
        print("\nFeature Match Rates:")
        for feature, stats in sorted(feature_analysis.items()):
            rate = stats["match"] / stats["total"] if stats["total"] > 0 else 0
            print(f"  {feature}: {rate:.2%} ({stats['match']}/{stats['total']})")
        
        # Recommendations
        print("\nRecommendations:")
        recommendations = []
        
        # Check symbol usage
        symbol_matches = sum(1 for r in successful_tests 
                           if r["comparison"]["current"].get("has_symbols"))
        if symbol_matches < len(successful_tests) * 0.7:
            recommendations.append("Increase symbol usage in responses")
        
        # Check protocol usage
        protocol_matches = sum(1 for r in successful_tests 
                              if r["comparison"]["current"].get("has_protocols"))
        if protocol_matches < len(successful_tests) * 0.7:
            recommendations.append("Ensure protocol commands are used when appropriate")
        
        # Check transmission format
        transmission_matches = sum(1 for r in successful_tests 
                                 if r["comparison"]["current"].get("has_transmission_format"))
        if transmission_matches < len(successful_tests):
            recommendations.append("Use transmission format consistently")
        
        # Check archetypal language
        archetypal_matches = sum(1 for r in successful_tests 
                               if r["comparison"]["current"].get("has_archetypal_language"))
        if archetypal_matches < len(successful_tests) * 0.8:
            recommendations.append("Increase use of archetypal and symbolic language")
        
        if recommendations:
            for rec in recommendations:
                print(f"  - {rec}")
        else:
            print("  ✓ All key features are present!")
    
    # Save analysis
    ANALYSIS_OUTPUT.mkdir(parents=True, exist_ok=True)
    with open(ANALYSIS_OUTPUT / "quick_test_analysis.json", 'w') as f:
        json.dump({
            "analysis_results": analysis_results,
            "summary": {
                "total_tests": len(analysis_results),
                "successful": len(successful_tests),
                "avg_similarity": avg_similarity if successful_tests else 0
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nAnalysis saved to: {ANALYSIS_OUTPUT}")

if __name__ == "__main__":
    run_analysis()

