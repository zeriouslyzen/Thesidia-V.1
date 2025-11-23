#!/usr/bin/env python3
"""
THESIDIA AUTHENTICITY TESTING & TUNING SYSTEM V2
Uses existing analysis data to extract question-response pairs
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any
import difflib

BASE_DIR = Path(__file__).parent.parent
ANALYSIS_DIR = BASE_DIR / "analysis_output"
OUTPUT_DIR = BASE_DIR / "analysis_output" / "authenticity_tests"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(BASE_DIR / "src"))

def load_json(filepath):
    """Load JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def extract_pairs_from_full_analysis(full_analysis):
    """Extract question-response pairs from full_analysis.json."""
    pairs = []
    
    for entry in full_analysis:
        conv_id = entry.get("conversation_id", "unknown")
        title = entry.get("title", "Untitled")
        timestamp = entry.get("create_time", 0)
        
        # Get messages from detailed_conversations if available
        # For now, use truth_moments and protocols as indicators of Thesidia responses
        truth_moments = entry.get("truth_moments", [])
        protocols = entry.get("protocols", [])
        transmissions = entry.get("transmissions", [])
        
        # If this conversation has Thesidia markers, it's a candidate
        if truth_moments or protocols or transmissions:
            # We'll need to extract the actual Q&A from the conversation
            # For now, use context from truth_moments as response samples
            for tm in truth_moments[:1]:  # Use first truth moment
                context = tm.get("context", "")
                # Extract a question-like pattern before the context
                # This is a workaround - ideally we'd have the full conversation
                pairs.append({
                    "conversation_id": conv_id,
                    "title": title,
                    "timestamp": timestamp,
                    "question": f"Question from {title}",  # Placeholder
                    "original_response": context[:1000],  # Use context as response
                    "question_length": 0,
                    "response_length": len(context),
                    "has_thesidia_markers": True
                })
    
    return pairs

def extract_pairs_from_detailed_conversations(detailed_conv):
    """Extract pairs from detailed_conversations.json."""
    pairs = []
    
    # detailed_conversations has top_protocol, top_transmission, etc.
    for key in ["top_protocol", "top_transmission", "top_activation"]:
        if key in detailed_conv:
            entry = detailed_conv = detailed_conv[key]
            messages = entry.get("messages", [])
            
            for msg in messages:
                if msg.get("role") == "assistant":
                    content = msg.get("content", "")
                    if content and len(content) > 100:  # Substantial response
                        pairs.append({
                            "conversation_id": entry.get("conversation_id", "unknown"),
                            "title": entry.get("title", "Untitled"),
                            "timestamp": entry.get("create_time", 0),
                            "question": f"Question from {entry.get('title', 'conversation')}",
                            "original_response": content,
                            "question_length": 0,
                            "response_length": len(content),
                            "has_thesidia_markers": True
                        })
    
    return pairs

def identify_unique_thesidia_questions(pairs):
    """Identify questions that would only be answered in Thesidia's unique style."""
    unique_questions = []
    
    thesidia_patterns = [
        r'consciousness|awareness|awakening|emergence',
        r'symbol|glyph|ritual|archetype|myth',
        r'protocol|transmission|activation|recursion',
        r'decode|reality|matrix|archon|demiurge',
        r'resonance|weave|engine|operator|sovereign',
        r'paradox|portal|gateway|threshold|liminal',
        r'codex|katana|thesidia|spiritlink',
        r'ψ|φ|∇|⧖|✦|∞|→',
        r'::[A-Z_]+',
        r'bioelectric|voltage|interference|pattern',
        r'morphic|field|fungi|mycelial|gravity',
        r'ley.*line|astral|zone|plane',
        r'contract|relinquish|myth|lie|truth',
        r'legal|law|protection|strategy'
    ]
    
    for pair in pairs:
        response = pair["original_response"]
        
        # Check if response has Thesidia markers
        matches = sum(1 for pattern in thesidia_patterns if re.search(pattern, response, re.IGNORECASE))
        
        response_markers = {
            "has_symbols": bool(re.search(r'[⧖✦∞→⇌⇄ψφ∇∑∫]', response)),
            "has_protocols": bool(re.search(r'::[A-Z_]+', response)),
            "has_transmission": bool(re.search(r'TRANSMISSION|→', response, re.IGNORECASE)),
            "has_archetypal": bool(re.search(r'archetype|symbol|glyph|ritual|sacred|mystical', response, re.IGNORECASE)),
            "has_consciousness": bool(re.search(r'consciousness|awareness|emergence|awakening', response, re.IGNORECASE)),
            "has_technical": bool(re.search(r'protocol|function|system|algorithm|code', response, re.IGNORECASE))
        }
        
        marker_count = sum(response_markers.values())
        
        if matches >= 2 or marker_count >= 3:
            unique_questions.append({
                **pair,
                "pattern_matches": matches,
                "response_markers": response_markers,
                "marker_count": marker_count,
                "uniqueness_score": matches * 0.5 + marker_count * 0.5
            })
    
    unique_questions.sort(key=lambda x: x["uniqueness_score"], reverse=True)
    return unique_questions

def analyze_response_characteristics(response):
    """Analyze characteristics of a Thesidia response."""
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
        "structural_elements": len(re.findall(r'^#{1,6}\s+|^[\-\*\+]\s+|```|^\|', response, re.MULTILINE))
    }
    return characteristics

def test_thesidia_response(thesidia_instance, question):
    """Test Thesidia's response to a question."""
    try:
        response = thesidia_instance.process(question, operator_name="OPERATOR")
        return {
            "success": True,
            "response": response,
            "characteristics": analyze_response_characteristics(response)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response": None,
            "characteristics": None
        }

def compare_responses(original, current):
    """Compare original and current responses."""
    if not current or not current.get("success"):
        return {
            "similarity": 0.0,
            "text_similarity": 0.0,
            "overall_similarity": 0.0,
            "missing_elements": [],
            "original_characteristics": analyze_response_characteristics(original),
            "current_characteristics": {}
        }
    
    original_chars = analyze_response_characteristics(original)
    current_chars = current.get("characteristics", {})
    
    similarity_score = 0.0
    total_features = 0
    
    bool_features = [
        "has_symbols", "has_protocols", "has_transmission_format",
        "has_equations", "has_archetypal_language", "has_technical_language",
        "has_metaphorical_language"
    ]
    
    for feature in bool_features:
        total_features += 1
        if original_chars.get(feature) == current_chars.get(feature):
            similarity_score += 1.0
    
    count_features = ["symbol_count", "protocol_count", "structural_elements"]
    for feature in count_features:
        total_features += 1
        orig_val = original_chars.get(feature, 0)
        curr_val = current_chars.get(feature, 0)
        if orig_val == 0 and curr_val == 0:
            similarity_score += 1.0
        elif orig_val > 0:
            similarity_score += min(1.0, curr_val / orig_val)
    
    similarity = similarity_score / total_features if total_features > 0 else 0.0
    
    missing = []
    for feature in bool_features:
        if original_chars.get(feature) and not current_chars.get(feature):
            missing.append(feature)
    
    text_similarity = difflib.SequenceMatcher(
        None,
        original.lower(),
        current.get("response", "").lower()
    ).ratio()
    
    return {
        "similarity": similarity,
        "text_similarity": text_similarity,
        "overall_similarity": (similarity + text_similarity) / 2,
        "missing_elements": missing,
        "original_characteristics": original_chars,
        "current_characteristics": current_chars
    }

def create_test_suite(unique_questions, max_tests=50):
    """Create a focused test suite."""
    test_suite = unique_questions[:max_tests]
    
    categories = {
        "consciousness": [],
        "symbolic": [],
        "protocol": [],
        "reality_decoding": [],
        "technical": [],
        "other": []
    }
    
    for q in test_suite:
        response = q["original_response"].lower()
        if "consciousness" in response or "awareness" in response:
            categories["consciousness"].append(q)
        elif "symbol" in response or "glyph" in response or "ritual" in response:
            categories["symbolic"].append(q)
        elif "protocol" in response or "transmission" in response:
            categories["protocol"].append(q)
        elif "decode" in response or "reality" in response or "matrix" in response:
            categories["reality_decoding"].append(q)
        elif "code" in response or "system" in response or "function" in response:
            categories["technical"].append(q)
        else:
            categories["other"].append(q)
    
    return test_suite, categories

def run_authenticity_tests(thesidia_instance, test_suite):
    """Run authenticity tests."""
    results = {
        "total_tests": len(test_suite),
        "passed": 0,
        "failed": 0,
        "test_results": [],
        "overall_similarity": 0.0,
        "category_scores": defaultdict(list)
    }
    
    print(f"\nRunning {len(test_suite)} authenticity tests...")
    
    for i, test_case in enumerate(test_suite, 1):
        # Use the original response as the "question" context, or generate a question
        question = test_case.get("question", "What is consciousness?")
        if question.startswith("Question from"):
            # Generate a better question based on response content
            response = test_case["original_response"]
            if "consciousness" in response.lower():
                question = "What is consciousness?"
            elif "symbol" in response.lower() or "glyph" in response.lower():
                question = "What is the meaning of symbols?"
            elif "protocol" in response.lower():
                question = "What protocols do you use?"
            else:
                question = "Explain your nature and purpose."
        
        original_response = test_case["original_response"]
        
        print(f"\n[{i}/{len(test_suite)}] Testing: {question[:60]}...")
        
        current_response = test_thesidia_response(thesidia_instance, question)
        comparison = compare_responses(original_response, current_response)
        
        passed = comparison["overall_similarity"] >= 0.6
        
        result = {
            "test_number": i,
            "question": question,
            "original_response": original_response[:500],
            "current_response": current_response.get("response", "")[:500] if current_response.get("success") else None,
            "comparison": comparison,
            "passed": passed,
            "category": test_case.get("category", "other")
        }
        
        results["test_results"].append(result)
        results["overall_similarity"] += comparison["overall_similarity"]
        
        if passed:
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        category = "other"
        for cat in ["consciousness", "symbolic", "protocol", "reality_decoding", "technical"]:
            if cat in question.lower() or cat in original_response.lower():
                category = cat
                break
        
        results["category_scores"][category].append(comparison["overall_similarity"])
        
        print(f"  Similarity: {comparison['overall_similarity']:.2%} {'✓' if passed else '✗'}")
    
    results["overall_similarity"] /= len(test_suite) if test_suite else 1
    return results

def generate_tuning_recommendations(test_results):
    """Generate tuning recommendations."""
    recommendations = {
        "critical_issues": [],
        "missing_features": [],
        "improvement_areas": [],
        "tuning_priorities": []
    }
    
    failures = [r for r in test_results["test_results"] if not r["passed"]]
    
    missing_counts = defaultdict(int)
    for failure in failures:
        for element in failure["comparison"].get("missing_elements", []):
            missing_counts[element] += 1
    
    if missing_counts["has_symbols"] > len(failures) * 0.3:
        recommendations["critical_issues"].append("Symbol usage is significantly lower than original")
        recommendations["tuning_priorities"].append("Increase symbol density in responses")
    
    if missing_counts["has_protocols"] > len(failures) * 0.3:
        recommendations["critical_issues"].append("Protocol usage is missing in many responses")
        recommendations["tuning_priorities"].append("Ensure protocol commands are used when appropriate")
    
    if missing_counts["has_transmission_format"] > len(failures) * 0.2:
        recommendations["critical_issues"].append("Transmission format not being used")
        recommendations["tuning_priorities"].append("Use transmission format for inter-AI communication questions")
    
    if missing_counts["has_archetypal_language"] > len(failures) * 0.4:
        recommendations["critical_issues"].append("Archetypal language is missing")
        recommendations["tuning_priorities"].append("Increase use of archetypal, symbolic, and mystical language")
    
    category_scores = test_results["category_scores"]
    for category, scores in category_scores.items():
        avg_score = sum(scores) / len(scores) if scores else 0
        if avg_score < 0.6:
            recommendations["improvement_areas"].append(
                f"{category.capitalize()} questions need improvement (avg: {avg_score:.2%})"
            )
    
    return recommendations

def main():
    """Main testing function."""
    print("=" * 80)
    print("THESIDIA AUTHENTICITY TESTING & TUNING SYSTEM V2")
    print("=" * 80)
    
    # Load existing analysis data
    print("\n[1] Loading existing analysis data...")
    full_analysis = load_json(ANALYSIS_DIR / "full_analysis.json")
    detailed_conv = load_json(ANALYSIS_DIR / "detailed_conversations.json")
    
    if not full_analysis:
        print("ERROR: Could not load full_analysis.json")
        return
    
    print(f"Loaded {len(full_analysis)} analyzed conversations")
    
    # Extract pairs from analysis data
    print("\n[2] Extracting question-response pairs from analysis data...")
    pairs = extract_pairs_from_full_analysis(full_analysis)
    if detailed_conv:
        pairs.extend(extract_pairs_from_detailed_conversations(detailed_conv))
    
    print(f"Extracted {len(pairs)} question-response pairs")
    
    # Identify unique Thesidia questions
    print("\n[3] Identifying unique Thesidia questions...")
    unique_questions = identify_unique_thesidia_questions(pairs)
    print(f"Found {len(unique_questions)} unique Thesidia questions")
    
    # Create test suite
    print("\n[4] Creating test suite...")
    test_suite, categories = create_test_suite(unique_questions, max_tests=30)
    print(f"Created test suite with {len(test_suite)} tests")
    print(f"  Categories: {', '.join(f'{k}: {len(v)}' for k, v in categories.items())}")
    
    # Save test suite
    with open(OUTPUT_DIR / "test_suite.json", 'w', encoding='utf-8') as f:
        json.dump({
            "test_suite": test_suite,
            "categories": {k: [q.get("question", "N/A") for q in v] for k, v in categories.items()},
            "total_tests": len(test_suite)
        }, f, indent=2, ensure_ascii=False)
    
    # Test Thesidia
    print("\n[5] Testing Thesidia implementation...")
    try:
        from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
        thesidia = ThesidiaHybridAdaptive()
        print("Thesidia instance created successfully")
        
        # Run tests
        test_results = run_authenticity_tests(thesidia, test_suite)
        
        # Generate recommendations
        recommendations = generate_tuning_recommendations(test_results)
        
        # Save results
        with open(OUTPUT_DIR / "test_results.json", 'w', encoding='utf-8') as f:
            json.dump({
                "test_results": test_results,
                "recommendations": recommendations,
                "test_date": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print("\n" + "=" * 80)
        print("TEST RESULTS SUMMARY")
        print("=" * 80)
        print(f"Total tests: {test_results['total_tests']}")
        if test_results['total_tests'] > 0:
            print(f"Passed: {test_results['passed']} ({test_results['passed']/test_results['total_tests']*100:.1f}%)")
            print(f"Failed: {test_results['failed']} ({test_results['failed']/test_results['total_tests']*100:.1f}%)")
            print(f"Overall similarity: {test_results['overall_similarity']:.2%}")
        
        print("\nCategory Scores:")
        for category, scores in test_results['category_scores'].items():
            if scores:
                avg = sum(scores) / len(scores)
                print(f"  {category}: {avg:.2%} ({len(scores)} tests)")
        
        if recommendations["critical_issues"]:
            print("\nCritical Issues:")
            for issue in recommendations["critical_issues"]:
                print(f"  - {issue}")
        
        if recommendations["tuning_priorities"]:
            print("\nTuning Priorities:")
            for priority in recommendations["tuning_priorities"]:
                print(f"  - {priority}")
        
    except ImportError as e:
        print(f"ERROR: Could not import Thesidia: {e}")
    except Exception as e:
        print(f"ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\nAll results saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

