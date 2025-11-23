#!/usr/bin/env python3
"""
Quick Benchmark - Short test queries to verify optimizations
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

def quick_benchmark():
    """Run quick benchmark with shorter queries"""
    
    print("\n" + "="*80)
    print("QUICK BENCHMARK - SYNTHESIS OPTIMIZATION TEST")
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
    
    # Short test queries (mix of simple and complex)
    test_queries = [
        ("Simple", "What is Genesis?"),  # Should use 4000 tokens
        ("Medium", "What are the origins of Genesis?"),  # Should use 6000 tokens
        ("Complex", "Decode the Genesis story - what's the real narrative?"),  # Should use 7000 tokens
    ]
    
    print("Running quick benchmark with optimized synthesis...\n")
    
    results = []
    
    for category, query in test_queries:
        print(f"[{category}] {query}")
        
        # Start tracking
        interaction_id = metrics.start_interaction(query)
        total_start = time.time()
        
        # Process query
        try:
            response = thesidia.process(query, operator_name="OPERATOR")
            total_time = time.time() - total_start
            
            # Get timing breakdown
            timing_breakdown = getattr(thesidia, '_last_timing_breakdown', {})
            
            # Estimate tokens
            token_count = len(response) // 4
            
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
                "success": True
            }
            results.append(result)
            
            print(f"  ✓ Total time: {total_time:.2f}s")
            if timing_breakdown:
                print(f"    - Web search: {timing_breakdown.get('web_search', 0):.2f}s")
                print(f"    - Synthesis: {timing_breakdown.get('synthesis', 0):.2f}s")
                print(f"    - State save: {timing_breakdown.get('state_save', 0):.2f}s")
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
    
    # Save results
    output_dir = BASE_DIR / "analysis_output" / "benchmark_results"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    benchmark_file = output_dir / f"quick_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    benchmark_data = {
        "test_date": datetime.now().isoformat(),
        "test_type": "quick_optimization_test",
        "results": results,
        "summary": {
            "total": len(results),
            "successful": sum(1 for r in results if r.get("success", False)),
            "failed": sum(1 for r in results if not r.get("success", False)),
            "avg_time": sum(r["total_time"] for r in results if r.get("success", False)) / max(1, sum(1 for r in results if r.get("success", False))),
            "avg_synthesis_time": sum(r.get("timing_breakdown", {}).get("synthesis", 0) for r in results if r.get("success", False)) / max(1, sum(1 for r in results if r.get("success", False))),
            "min_time": min((r["total_time"] for r in results if r.get("success", False)), default=0),
            "max_time": max((r["total_time"] for r in results if r.get("success", False)), default=0),
        }
    }
    
    with open(benchmark_file, 'w') as f:
        json.dump(benchmark_data, f, indent=2)
    
    print("="*80)
    print("QUICK BENCHMARK SUMMARY")
    print("="*80)
    print(f"Total queries: {benchmark_data['summary']['total']}")
    print(f"Successful: {benchmark_data['summary']['successful']}")
    print(f"Average time: {benchmark_data['summary']['avg_time']:.2f}s")
    print(f"Average synthesis time: {benchmark_data['summary']['avg_synthesis_time']:.2f}s")
    print(f"Min time: {benchmark_data['summary']['min_time']:.2f}s")
    print(f"Max time: {benchmark_data['summary']['max_time']:.2f}s")
    print(f"\nResults saved to: {benchmark_file}")
    print("="*80 + "\n")
    
    # Compare to baseline
    print("COMPARISON TO BASELINE:")
    print(f"  Baseline avg synthesis: 64.36s")
    print(f"  Current avg synthesis: {benchmark_data['summary']['avg_synthesis_time']:.2f}s")
    if benchmark_data['summary']['avg_synthesis_time'] > 0:
        improvement = ((64.36 - benchmark_data['summary']['avg_synthesis_time']) / 64.36) * 100
        print(f"  Improvement: {improvement:.1f}% faster")
    print()

if __name__ == "__main__":
    quick_benchmark()

