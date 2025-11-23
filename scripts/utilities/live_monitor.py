#!/usr/bin/env python3
"""
Live Monitor - Real-time metrics dashboard
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

from metrics_collector import MetricsCollector

def display_live_metrics(metrics_file: Path, log_file: Path, refresh_interval: float = 2.0):
    """Display live metrics in terminal"""
    
    import os
    
    print("\n" + "="*80)
    print("THESIDIA LIVE MONITOR")
    print("Press Ctrl+C to exit")
    print("="*80 + "\n")
    
    metrics = MetricsCollector(base_dir=BASE_DIR)
    
    try:
        while True:
            os.system('clear' if os.name != 'nt' else 'cls')
            
            print("\n" + "="*80)
            print(f"THESIDIA LIVE METRICS - {datetime.now().strftime('%H:%M:%S')}")
            print("="*80 + "\n")
            
            current = metrics.get_current_metrics()
            
            # Performance
            print("⚡ PERFORMANCE")
            print("-" * 80)
            if "performance" in current:
                perf = current["performance"]
                print(f"  Avg Response Time: {perf['avg_response_time']:.2f}s")
                print(f"  Min: {perf['min_response_time']:.2f}s | Max: {perf['max_response_time']:.2f}s")
                print(f"  Median: {perf['median_response_time']:.2f}s | Std Dev: {perf['std_dev']:.2f}s")
                print(f"  Total Responses: {perf['total_responses']}")
            else:
                print("  No data yet")
            print()
            
            # Tokens
            print("📊 TOKENS")
            print("-" * 80)
            if "tokens" in current:
                tokens = current["tokens"]
                print(f"  Avg: {tokens['avg_tokens']:.0f} | Total: {tokens['total_tokens']}")
                print(f"  Range: {tokens['min_tokens']} - {tokens['max_tokens']}")
            else:
                print("  No data yet")
            print()
            
            # Patterns
            print("🔍 PATTERNS DETECTED")
            print("-" * 80)
            if current["patterns_detected"]:
                for pattern, count in sorted(current["patterns_detected"].items(), key=lambda x: x[1], reverse=True):
                    print(f"  {pattern:30s}: {count:5d}")
            else:
                print("  No patterns detected yet")
            print()
            
            # Linguistic Features
            print("📝 LINGUISTIC FEATURES")
            print("-" * 80)
            if current["linguistic_features"]:
                for feature, value in sorted(current["linguistic_features"].items()):
                    if isinstance(value, float):
                        print(f"  {feature:30s}: {value:8.2f}")
                    else:
                        print(f"  {feature:30s}: {value:8d}")
            else:
                print("  No linguistic data yet")
            print()
            
            # Pattern Analysis
            print("📈 PATTERN TRENDS")
            print("-" * 80)
            pattern_analysis = metrics.get_pattern_analysis()
            if pattern_analysis:
                for pattern, stats in sorted(pattern_analysis.items(), key=lambda x: x[1]['total'], reverse=True)[:10]:
                    trend_icon = "📈" if stats['trend'] == "increasing" else "➡️"
                    print(f"  {trend_icon} {pattern:30s}: avg={stats['avg']:.1f}, freq={stats['frequency']:.1%}")
            else:
                print("  No trend data yet")
            print()
            
            # Recent interactions
            print("🕐 RECENT INTERACTIONS")
            print("-" * 80)
            if current["interactions"]:
                for inter in current["interactions"][-5:]:
                    query = inter.get("query", "")[:60]
                    rt = inter.get("response_time", 0)
                    print(f"  [{rt:.2f}s] {query}...")
            else:
                print("  No interactions yet")
            print()
            
            print("="*80)
            print(f"Refreshing every {refresh_interval}s... (Ctrl+C to exit)")
            print("="*80)
            
            time.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        print("\n\nMonitor stopped.")

if __name__ == "__main__":
    metrics_file = BASE_DIR / "data" / "thesidia_metrics.json"
    log_file = BASE_DIR / "data" / "thesidia_logs.jsonl"
    display_live_metrics(metrics_file, log_file)

