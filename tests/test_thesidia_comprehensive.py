#!/usr/bin/env python3
"""
Comprehensive Thesidia Testing Script
Tests different query types: truth-seeking, casual conversation, and task instructions
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5002"

def test_query(query_type, query, description):
    """Test a single query"""
    print(f"\n{'='*80}")
    print(f"TEST: {query_type}")
    print(f"Description: {description}")
    print(f"Query: {query}")
    print(f"{'='*80}\n")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/thesidia",
            json={
                "message": query,
                "stream": False
            },
            timeout=120
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            reply = data.get("response", data.get("reply", ""))
            metrics = data.get("metrics", {})
            
            print(f"✅ Response received in {elapsed:.2f}s")
            print(f"Response length: {len(reply)} characters")
            print(f"\nResponse preview (first 500 chars):")
            print("-" * 80)
            print(reply[:500])
            if len(reply) > 500:
                print("...")
            print("-" * 80)
            
            if metrics:
                print(f"\nMetrics:")
                print(f"  - Response time: {metrics.get('response_time', 'N/A')}s")
                print(f"  - Token count: {metrics.get('token_count', 'N/A')}")
                print(f"  - Pattern frequency: {metrics.get('pattern_frequency', 'N/A')}")
            
            return {
                "query_type": query_type,
                "query": query,
                "success": True,
                "response_time": elapsed,
                "response_length": len(reply),
                "response_preview": reply[:500],
                "metrics": metrics
            }
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return {
                "query_type": query_type,
                "query": query,
                "success": False,
                "error": f"HTTP {response.status_code}",
                "response": response.text[:500]
            }
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return {
            "query_type": query_type,
            "query": query,
            "success": False,
            "error": str(e)
        }

def main():
    """Run comprehensive tests"""
    print("="*80)
    print("THESIDIA COMPREHENSIVE TESTING")
    print("="*80)
    print(f"Testing against: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Check if server is running
    try:
        status_response = requests.get(f"{BASE_URL}/api/status", timeout=5)
        if status_response.status_code == 200:
            print("\n✅ Server is running")
        else:
            print(f"\n⚠️  Server returned status {status_response.status_code}")
    except Exception as e:
        print(f"\n❌ Server not reachable: {e}")
        print("Please start the server first: cd webapp && python3 server.py")
        return
    
    results = []
    
    # Test 1: Simple Greeting / Casual Conversation
    print("\n" + "="*80)
    print("TEST SUITE 1: CASUAL CONVERSATION")
    print("="*80)
    
    results.append(test_query(
        "casual_greeting",
        "hi",
        "Simple greeting - should be fast and natural"
    ))
    
    time.sleep(2)
    
    results.append(test_query(
        "casual_conversation",
        "how are you doing today?",
        "Casual conversation - should feel natural and friendly"
    ))
    
    time.sleep(2)
    
    # Test 2: Truth-Seeking Questions
    print("\n" + "="*80)
    print("TEST SUITE 2: TRUTH-SEEKING QUESTIONS")
    print("="*80)
    
    results.append(test_query(
        "truth_seeking_1",
        "What really happened with the Baghdad Battery? I've heard it might be evidence of ancient electrical technology.",
        "Truth-seeking about ancient technology - should cross-reference, recognize patterns, synthesize gnosis/episteme"
    ))
    
    time.sleep(3)
    
    results.append(test_query(
        "truth_seeking_2",
        "Tell me about the Priestly redaction of Leviticus. What patterns do you see in how it was edited?",
        "Truth-seeking about historical redaction - should use forensic analysis, pattern recognition"
    ))
    
    time.sleep(3)
    
    results.append(test_query(
        "truth_seeking_3",
        "I practice Shaolin and I've experienced unlimited energy through bioelectric processes. Can you cross-reference this with scientific research?",
        "Truth-seeking combining direct experience (gnosis) with research (episteme) - should synthesize both"
    ))
    
    time.sleep(3)
    
    # Test 3: Task Instructions
    print("\n" + "="*80)
    print("TEST SUITE 3: TASK INSTRUCTIONS")
    print("="*80)
    
    results.append(test_query(
        "task_instruction_1",
        "Can you help me understand the connection between Sumerian texts and modern systems? Cross-reference multiple sources.",
        "Task instruction for research - should perform deep research, cross-reference"
    ))
    
    time.sleep(3)
    
    results.append(test_query(
        "task_instruction_2",
        "Explain how patterns repeat across civilizations. Show me connections between ancient artifacts and modern technology.",
        "Task instruction for pattern recognition - should recognize patterns across time"
    ))
    
    time.sleep(3)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    successful = sum(1 for r in results if r.get("success", False))
    total = len(results)
    
    print(f"\nTotal tests: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    
    if successful > 0:
        avg_time = sum(r.get("response_time", 0) for r in results if r.get("success", False)) / successful
        print(f"Average response time: {avg_time:.2f}s")
    
    print("\nDetailed Results:")
    for i, result in enumerate(results, 1):
        status = "✅" if result.get("success", False) else "❌"
        query_type = result.get("query_type", "unknown")
        response_time = result.get("response_time", "N/A")
        print(f"  {i}. {status} {query_type}: {response_time}s")
    
    # Save results
    output_file = "analysis_output/thesidia_comprehensive_test_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": total,
            "successful": successful,
            "failed": total - successful,
            "results": results
        }, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_file}")
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

