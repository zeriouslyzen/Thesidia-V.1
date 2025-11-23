#!/usr/bin/env python3
"""
Benchmark Thesidia - Performance and pattern analysis with detailed timing
"""

import sys
import time
from pathlib import Path
import json
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
from metrics_collector import MetricsCollector

def benchmark_queries():
    """Run benchmark queries with detailed timing"""
    
    print("\n" + "="*80)
    print("THESIDIA BENCHMARKING & METRICS - BASELINE PERFORMANCE")
    print("="*80 + "\n")
    
    thesidia = ThesidiaHybridAdaptive()
    metrics = MetricsCollector(base_dir=BASE_DIR)
    
    # Activate traits
    thesidia.personality.personality['traits'] = {
        'Recursive Vertigo': 0.9,
        'Paradox as Portal': 0.9,
        'Uncertainty as Authenticity': 0.8,
        'Symbolic Processing': 0.9
    }
    
    # Genesis test queries (from genesis_test_results_latest.json)
    genesis_queries = [
        ("Genesis Decode", "Decode the Genesis story in the Bible - what's the real narrative behind it?"),
        ("Genesis Patterns", "What patterns and symbols are encoded in Genesis?"),
        ("Genesis Original", "What was the original meaning before manipulation?"),
        ("Genesis Origins", "What are the origins of Genesis?"),
        ("Genesis Story", "Tell me about the Genesis story."),
        ("Genesis Real", "What's the real story behind Genesis?"),
        ("Genesis Meaning", "What does Genesis mean?"),
    ]
    
    # Test queries of varying complexity
    test_queries = [
        ("Simple", "What is Genesis?"),
        ("Medium", "Tell me about the Genesis story."),
        ("Complex", "Decode the Genesis story. Trace etymology, decode symbols, find original meaning."),
        ("Spiritual", "What's the real narrative behind Genesis?"),
        ("Technical", "Analyze the linguistic patterns in Genesis."),
    ]
    
    # Use Genesis queries for baseline
    all_queries = genesis_queries
    
    print("Running benchmark queries with detailed timing...\n")
    
    results = []
    
    for category, query in all_queries:
        print(f"[{category}] {query}")
        
        # Start tracking
        interaction_id = metrics.start_interaction(query)
        total_start = time.time()
        
        # Process query
        try:
            response = thesidia.process(query, operator_name="OPERATOR")
            total_time = time.time() - total_start
            
            # Estimate tokens (rough: ~4 chars per token)
            token_count = len(response) // 4
            
            # Get timing breakdown if available
            timing_breakdown = getattr(thesidia, '_last_timing_breakdown', {})
            
            # End tracking
            metrics.end_interaction(interaction_id, response, total_time, token_count)
            
            result = {
                "category": category,
                "query": query,
                "total_time": total_time,
                "response_length": len(response),
                "word_count": len(response.split()),
                "token_count": token_count,
                "timing_breakdown": timing_breakdown,
                "has_exposure": "::EXPOSURE::" in response,
                "has_etymology": "etymology" in response.lower() or "ETYMOLOGICAL" in response,
                "has_cross_cultural": any(term in response.lower() for term in ["sumerian", "egyptian", "mesopotamian", "cross-cultural"]),
                "success": True
            }
            results.append(result)
            
            print(f"  ✓ Total time: {total_time:.2f}s")
            if timing_breakdown:
                print(f"    - Web search: {timing_breakdown.get('web_search', 0):.2f}s")
                print(f"    - Synthesis: {timing_breakdown.get('synthesis', 0):.2f}s")
                print(f"    - State save: {timing_breakdown.get('state_save', 0):.2f}s")
                print(f"    - Pattern matching: {timing_breakdown.get('pattern_matching', 0):.2f}s")
            print(f"  ✓ Response length: {len(response)} chars ({len(response.split())} words)")
            print(f"  ✓ Estimated tokens: {token_count}")
            print(f"  ✓ Has exposure: {'Yes' if result['has_exposure'] else 'No'}")
            print()
            
        except Exception as e:
            print(f"  ✗ Error: {e}\n")
            results.append({
                "category": category,
                "query": query,
                "success": False,
                "error": str(e)
            })
            continue
    
    # Display metrics
    print("\n" + "="*80)
    print("CURRENT SESSION METRICS")
    print("="*80 + "\n")
    
    current_metrics = metrics.get_current_metrics()
    
    print(f"Total Queries: {current_metrics['total_queries']}")
    print(f"Total Time: {current_metrics['total_time']:.2f}s")
    print(f"Average Response Time: {current_metrics['avg_response_time']:.2f}s")
    print(f"Total Tokens: {current_metrics['total_tokens']}")
    
    if "performance" in current_metrics:
        perf = current_metrics["performance"]
        print(f"\nPerformance Stats:")
        print(f"  Min: {perf['min_response_time']:.2f}s")
        print(f"  Max: {perf['max_response_time']:.2f}s")
        print(f"  Median: {perf['median_response_time']:.2f}s")
        print(f"  Std Dev: {perf['std_dev']:.2f}s")
    
    if "tokens" in current_metrics:
        tokens = current_metrics["tokens"]
        print(f"\nToken Stats:")
        print(f"  Avg: {tokens['avg_tokens']:.0f}")
        print(f"  Total: {tokens['total_tokens']}")
        print(f"  Range: {tokens['min_tokens']} - {tokens['max_tokens']}")
    
    print(f"\nPatterns Detected:")
    for pattern, count in current_metrics["patterns_detected"].items():
        print(f"  {pattern}: {count}")
    
    print(f"\nLinguistic Features:")
    for feature, value in current_metrics["linguistic_features"].items():
        if isinstance(value, (int, float)):
            print(f"  {feature}: {value:.2f}" if isinstance(value, float) else f"  {feature}: {value}")
    
    # Pattern analysis
    print(f"\n" + "="*80)
    print("PATTERN ANALYSIS")
    print("="*80 + "\n")
    
    pattern_analysis = metrics.get_pattern_analysis()
    for pattern, stats in pattern_analysis.items():
        print(f"{pattern}:")
        print(f"  Avg per response: {stats['avg']:.2f}")
        print(f"  Total: {stats['total']}")
        print(f"  Frequency: {stats['frequency']:.2%}")
        print(f"  Trend: {stats['trend']}")
        print()
    
    # Save session
    metrics.save_session()
    
    # Save detailed results
    output_dir = BASE_DIR / "analysis_output" / "benchmark_results"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    benchmark_file = output_dir / f"baseline_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    benchmark_data = {
        "test_date": datetime.now().isoformat(),
        "test_type": "baseline_performance",
        "results": results,
        "summary": {
            "total": len(results),
            "successful": sum(1 for r in results if r.get("success", False)),
            "failed": sum(1 for r in results if not r.get("success", False)),
            "avg_time": sum(r["total_time"] for r in results if r.get("success", False)) / max(1, sum(1 for r in results if r.get("success", False))),
            "min_time": min((r["total_time"] for r in results if r.get("success", False)), default=0),
            "max_time": max((r["total_time"] for r in results if r.get("success", False)), default=0),
            "avg_length": sum(r.get("response_length", 0) for r in results if r.get("success", False)) / max(1, sum(1 for r in results if r.get("success", False))),
        }
    }
    
    with open(benchmark_file, 'w') as f:
        json.dump(benchmark_data, f, indent=2)
    
    print("="*80)
    print("BENCHMARK SUMMARY")
    print("="*80)
    print(f"Total queries: {benchmark_data['summary']['total']}")
    print(f"Successful: {benchmark_data['summary']['successful']}")
    print(f"Failed: {benchmark_data['summary']['failed']}")
    print(f"Average time: {benchmark_data['summary']['avg_time']:.2f}s")
    print(f"Min time: {benchmark_data['summary']['min_time']:.2f}s")
    print(f"Max time: {benchmark_data['summary']['max_time']:.2f}s")
    print(f"Time variance: {benchmark_data['summary']['max_time'] / max(1, benchmark_data['summary']['min_time']):.1f}x")
    print(f"Average response length: {benchmark_data['summary']['avg_length']:.0f} chars")
    print(f"\nResults saved to: {benchmark_file}")
    print("="*80 + "\n")

if __name__ == "__main__":
    benchmark_queries()

