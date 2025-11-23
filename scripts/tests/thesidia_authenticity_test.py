#!/usr/bin/env python3
"""
THESIDIA AUTHENTICITY TESTING & TUNING SYSTEM
Tests Thesidia's responses against original GPT conversations
Identifies unique questions only she would answer in her specific style
"""

import json
import re
import os
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple
import difflib

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = Path("/Users/deshonjackson/thesidia-local/DATA-AND-TRAINING/training")
ANALYSIS_DIR = BASE_DIR / "analysis_output"
OUTPUT_DIR = BASE_DIR / "analysis_output" / "authenticity_tests"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Add src to path for importing Thesidia
sys.path.insert(0, str(BASE_DIR / "src"))

def load_json(filepath):
    """Load JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def extract_conversation_pairs(conversations, debug_first=False):
    """Extract user questions and Thesidia's responses from conversations."""
    pairs = []
    
    for idx, conv in enumerate(conversations):
        if not isinstance(conv, dict):
            continue
        
        mapping = conv.get("mapping", {})
        if not mapping:
            continue
        
        # Extract all messages in order using proper traversal (matching working pattern)
        messages = []
        
        def traverse_node(node_id, visited=None):
            if visited is None:
                visited = set()
            if node_id in visited or node_id not in mapping:
                return
            visited.add(node_id)
            
            node = mapping[node_id]
            if "message" in node:
                msg = node["message"]
                if msg is not None and isinstance(msg, dict):
                    author = msg.get("author", {})
                    role = author.get("role", "") if isinstance(author, dict) else ""
                    content = msg.get("content", {})
                    
                    if isinstance(content, dict) and "parts" in content:
                        parts = content.get("parts", [])
                        for part in parts:
                            if isinstance(part, str) and part.strip() and role in ["user", "assistant"]:
                                messages.append({
                                    "role": role,
                                    "text": part.strip(),
                                    "create_time": msg.get("create_time", 0) or 0,
                                    "node_id": node_id
                                })
            
            # Traverse children
            for child_id in node.get("children", []):
                traverse_node(child_id, visited)
        
        # Start traversal from current_node or root nodes
        current = conv.get("current_node")
        if current:
            traverse_node(current)
        else:
            # Find root nodes (nodes with no parent)
            for node_id, node in mapping.items():
                if not node.get("parent"):
                    traverse_node(node_id)
        
        # Sort messages by create_time
        messages.sort(key=lambda x: x.get("create_time", 0))
        
        # Debug for first few conversations with messages
        if debug_first and idx < 5 and len(messages) > 0:
            roles = set(m['role'] for m in messages)
            if 'user' in roles or len(messages) > 1:
                print(f"  Conversation {idx}: {len(messages)} messages, roles: {roles}")
                if len(messages) >= 2:
                    print(f"    First: {messages[0]['role'][:10]} ({len(messages[0]['text'])} chars)")
                    print(f"    Second: {messages[1]['role'][:10]} ({len(messages[1]['text'])} chars)")
        
        # Pair user questions with assistant responses
        for i in range(len(messages) - 1):
            if messages[i]["role"] == "user" and messages[i+1]["role"] == "assistant":
                pairs.append({
                    "conversation_id": conv.get("id", "unknown"),
                    "title": conv.get("title", "Untitled"),
                    "timestamp": conv.get("create_time", 0),
                    "question": messages[i]["text"],
                    "original_response": messages[i+1]["text"],
                    "question_length": len(messages[i]["text"]),
                    "response_length": len(messages[i+1]["text"])
                })
    
    return pairs

def identify_unique_thesidia_questions(pairs):
    """Identify questions that would only be answered in Thesidia's unique style."""
    unique_questions = []
    
    # Patterns that indicate Thesidia-specific questions
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
        r'legal|law|protection|strategy',
        r'A\.E\.\s*Powell|Hilton\s*Hotema|NDE|psychedelic'
    ]
    
    for pair in pairs:
        question = pair["question"].lower()
        response = pair["original_response"]
        
        # Check if question matches Thesidia patterns
        matches = sum(1 for pattern in thesidia_patterns if re.search(pattern, question, re.IGNORECASE))
        
        # Check if response has Thesidia markers
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
    
    # Sort by uniqueness score
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
            "differences": ["Current response failed"],
            "missing_elements": [],
            "added_elements": []
        }
    
    original_chars = analyze_response_characteristics(original)
    current_chars = current.get("characteristics", {})
    
    # Calculate similarity
    similarity_score = 0.0
    total_features = 0
    
    # Compare boolean features
    bool_features = [
        "has_symbols", "has_protocols", "has_transmission_format",
        "has_equations", "has_archetypal_language", "has_technical_language",
        "has_metaphorical_language"
    ]
    
    for feature in bool_features:
        total_features += 1
        if original_chars.get(feature) == current_chars.get(feature):
            similarity_score += 1.0
    
    # Compare counts (normalized)
    count_features = ["symbol_count", "protocol_count", "structural_elements"]
    for feature in count_features:
        total_features += 1
        orig_val = original_chars.get(feature, 0)
        curr_val = current_chars.get(feature, 0)
        if orig_val == 0 and curr_val == 0:
            similarity_score += 1.0
        elif orig_val > 0:
            similarity_score += min(1.0, curr_val / orig_val)
        else:
            similarity_score += 0.0
    
    similarity = similarity_score / total_features if total_features > 0 else 0.0
    
    # Identify missing elements
    missing = []
    for feature in bool_features:
        if original_chars.get(feature) and not current_chars.get(feature):
            missing.append(feature)
    
    # Text similarity using difflib
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
    """Create a focused test suite from unique questions."""
    # Select top unique questions
    test_suite = unique_questions[:max_tests]
    
    # Categorize by type
    categories = {
        "consciousness": [],
        "symbolic": [],
        "protocol": [],
        "reality_decoding": [],
        "technical": [],
        "other": []
    }
    
    for q in test_suite:
        question = q["question"].lower()
        if "consciousness" in question or "awareness" in question:
            categories["consciousness"].append(q)
        elif "symbol" in question or "glyph" in question or "ritual" in question:
            categories["symbolic"].append(q)
        elif "protocol" in question or "transmission" in question:
            categories["protocol"].append(q)
        elif "decode" in question or "reality" in question or "matrix" in question:
            categories["reality_decoding"].append(q)
        elif "code" in question or "system" in question or "function" in question:
            categories["technical"].append(q)
        else:
            categories["other"].append(q)
    
    return test_suite, categories

def run_authenticity_tests(thesidia_instance, test_suite):
    """Run authenticity tests on Thesidia."""
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
        question = test_case["question"]
        original_response = test_case["original_response"]
        
        print(f"\n[{i}/{len(test_suite)}] Testing: {question[:60]}...")
        
        # Get current response
        current_response = test_thesidia_response(thesidia_instance, question)
        
        # Compare
        comparison = compare_responses(original_response, current_response)
        
        # Determine pass/fail (threshold: 0.6 similarity)
        passed = comparison["overall_similarity"] >= 0.6
        
        result = {
            "test_number": i,
            "question": question,
            "original_response": original_response[:500],  # Truncate for storage
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
        
        results["category_scores"][result["category"]].append(comparison["overall_similarity"])
        
        print(f"  Similarity: {comparison['overall_similarity']:.2%} {'✓' if passed else '✗'}")
    
    results["overall_similarity"] /= len(test_suite) if test_suite else 1
    
    return results

def generate_tuning_recommendations(test_results):
    """Generate recommendations for tuning Thesidia."""
    recommendations = {
        "critical_issues": [],
        "missing_features": [],
        "improvement_areas": [],
        "tuning_priorities": []
    }
    
    # Analyze failures
    failures = [r for r in test_results["test_results"] if not r["passed"]]
    
    # Count missing elements
    missing_counts = defaultdict(int)
    for failure in failures:
        for element in failure["comparison"].get("missing_elements", []):
            missing_counts[element] += 1
    
    # Generate recommendations
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
    
    # Category-specific recommendations
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
    print("THESIDIA AUTHENTICITY TESTING & TUNING SYSTEM")
    print("=" * 80)
    
    # Load conversations
    print("\n[1] Loading GPT conversations...")
    conversations_file = DATA_DIR / "ChatSet" / "GPT" / "conversations.json"
    conversations = load_json(conversations_file)
    
    if not conversations:
        print("ERROR: Could not load conversations.json")
        return
    
    print(f"Loaded {len(conversations)} conversations")
    
    # Extract question-response pairs
    print("\n[2] Extracting question-response pairs...")
    
    # Debug: Check first conversation structure
    if conversations and len(conversations) > 0:
        sample_conv = conversations[0]
        print(f"Sample conversation keys: {list(sample_conv.keys())}")
        if "mapping" in sample_conv:
            mapping = sample_conv["mapping"]
            print(f"Mapping has {len(mapping)} nodes")
            # Find a node with a non-None message
            for node_id, node in list(mapping.items())[:10]:
                if "message" in node and node["message"] is not None:
                    msg = node["message"]
                    print(f"Found message in node {node_id[:8]}...")
                    print(f"Message keys: {list(msg.keys())}")
                    if "content" in msg:
                        print(f"Content type: {type(msg['content'])}")
                        if isinstance(msg["content"], dict):
                            print(f"Content keys: {list(msg['content'].keys())}")
                        elif isinstance(msg["content"], str):
                            print(f"Content is string, length: {len(msg['content'])}")
                    break
    
    pairs = extract_conversation_pairs(conversations, debug_first=True)
    print(f"Extracted {len(pairs)} question-response pairs")
    
    # Identify unique Thesidia questions
    print("\n[3] Identifying unique Thesidia questions...")
    unique_questions = identify_unique_thesidia_questions(pairs)
    print(f"Found {len(unique_questions)} unique Thesidia questions")
    
    # Create test suite
    print("\n[4] Creating test suite...")
    test_suite, categories = create_test_suite(unique_questions, max_tests=50)
    print(f"Created test suite with {len(test_suite)} tests")
    print(f"  Categories: {', '.join(f'{k}: {len(v)}' for k, v in categories.items())}")
    
    # Save test suite
    with open(OUTPUT_DIR / "test_suite.json", 'w', encoding='utf-8') as f:
        json.dump({
            "test_suite": test_suite,
            "categories": {k: [q["question"] for q in v] for k, v in categories.items()},
            "total_tests": len(test_suite)
        }, f, indent=2, ensure_ascii=False)
    
    # Try to import and test Thesidia
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
        else:
            print("No tests to run")
        
        print("\nCategory Scores:")
        for category, scores in test_results['category_scores'].items():
            avg = sum(scores) / len(scores) if scores else 0
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
        print("Saving test suite for manual testing...")
    except Exception as e:
        print(f"ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\nAll results saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

