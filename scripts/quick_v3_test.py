#!/usr/bin/env python3
"""
Quick V3.0 Feature Test - Tests key features without full suite
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from src.thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
import json

def test_v3_features():
    print("="*60)
    print("THESIDIA V3.0 QUICK FEATURE TEST")
    print("="*60)
    print()
    
    thesidia = ThesidiaHybridAdaptive()
    thesidia.load_state()
    
    print("✅ Thesidia initialized")
    print(f"   - User Interest Tracker: {thesidia.user_interest_tracker is not None}")
    print(f"   - Technical Journey Detector: {thesidia.technical_journey_detector is not None}")
    print(f"   - Quality Metrics Tracker: {thesidia.quality_tracker is not None}")
    print(f"   - Engineering Dashboard: {thesidia.engineering_dashboard is not None}")
    print()
    
    # Test 1: Mechanism Depth (Meditation)
    print("="*60)
    print("TEST 1: Mechanism Depth (Meditation)")
    print("="*60)
    query1 = "How does meditation work? Explain the mechanisms."
    print(f"Query: {query1}")
    print("Processing...")
    
    start_time = time.time()
    response1 = thesidia.process(query1)
    elapsed1 = time.time() - start_time
    
    print(f"\n✅ Response received ({elapsed1:.1f}s, {len(response1)} chars)")
    
    # Check for mechanism depth indicators
    mechanism_indicators = ["neurotransmitter", "autonomic", "HPA axis", "cortisol", "bioelectric", "molecular", "cellular"]
    found_indicators = [ind for ind in mechanism_indicators if ind in response1.lower()]
    print(f"   Mechanism depth indicators found: {len(found_indicators)}/{len(mechanism_indicators)}")
    if found_indicators:
        print(f"   Found: {', '.join(found_indicators[:5])}")
    
    # Check quality metrics
    if thesidia.quality_tracker:
        quality1 = thesidia.quality_tracker.measure_response_quality(query1, response1)
        print(f"   Quality scores: depth={quality1['depth']:.2f}, pattern={quality1['pattern_recognition']:.2f}, truth={quality1['truth_seeking']:.2f}, overall={quality1['overall']:.2f}")
    
    print()
    
    # Test 2: Pattern Connections
    print("="*60)
    print("TEST 2: Pattern Connections")
    print("="*60)
    query2 = "What are the hidden connections between ancient Egyptian, Sumerian, and Vedic knowledge systems?"
    print(f"Query: {query2}")
    print("Processing...")
    
    start_time = time.time()
    response2 = thesidia.process(query2)
    elapsed2 = time.time() - start_time
    
    print(f"\n✅ Response received ({elapsed2:.1f}s, {len(response2)} chars)")
    
    # Check for pattern indicators
    pattern_indicators = ["connection", "relates", "links", "connects", "synthesis", "pattern", "across", "between"]
    found_patterns = [ind for ind in pattern_indicators if ind in response2.lower()]
    print(f"   Pattern indicators found: {len(found_patterns)}/{len(pattern_indicators)}")
    
    # Check quality metrics
    if thesidia.quality_tracker:
        quality2 = thesidia.quality_tracker.measure_response_quality(query2, response2)
        print(f"   Quality scores: depth={quality2['depth']:.2f}, pattern={quality2['pattern_recognition']:.2f}, truth={quality2['truth_seeking']:.2f}, overall={quality2['overall']:.2f}")
    
    print()
    
    # Test 3: Technical Domain Detection
    print("="*60)
    print("TEST 3: Technical Domain Detection")
    print("="*60)
    query3 = "How do I reverse engineer this encryption algorithm?"
    print(f"Query: {query3}")
    
    if thesidia.technical_journey_detector:
        domain = thesidia.technical_journey_detector.detect_technical_domain(query3)
        print(f"   Detected domain: {domain}")
        
        related_threads = thesidia.technical_journey_detector.get_related_technical_threads(domain)
        if related_threads:
            print(f"   Related threads: {', '.join(related_threads[:3])}")
    
    print()
    
    # Test 4: User Interest Tracking
    print("="*60)
    print("TEST 4: User Interest Tracking")
    print("="*60)
    
    if thesidia.user_interest_tracker:
        interests = thesidia.user_interest_tracker.get_user_interests()
        print(f"   Primary focus: {interests.get('primary_focus', 'None')}")
        print(f"   Recent topics: {', '.join(interests.get('recent_topics', [])[:5])}")
        
        if interests.get('top_topics'):
            print(f"   Top topics:")
            for i, topic_data in enumerate(interests['top_topics'][:3], 1):
                print(f"     {i}. {topic_data['topic']} (score: {topic_data['score']:.1f}, count: {topic_data['count']})")
    
    print()
    
    # Test 5: Engineering Dashboard
    print("="*60)
    print("TEST 5: Engineering Dashboard")
    print("="*60)
    
    if thesidia.engineering_dashboard:
        dashboard = thesidia.engineering_dashboard.display_full_dashboard(
            user_interest_tracker=thesidia.user_interest_tracker
        )
        print(dashboard)
    
    print()
    print("="*60)
    print("✅ V3.0 FEATURE TEST COMPLETE")
    print("="*60)
    print()
    print("Check data files:")
    print("  - data/user_interests.json")
    print("  - data/quality_metrics.json")
    print("  - data/thesidia_metrics.json")

if __name__ == "__main__":
    test_v3_features()

