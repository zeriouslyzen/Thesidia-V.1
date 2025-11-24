#!/usr/bin/env python3
"""
Test Decoding Configuration - Replicate Working Genesis Config

Tests the configuration that worked well for "genesis" on other questions
that need decoding/breaking down/tracking.

Configuration:
- Mode: Regular (spacious)
- Model: clean-mistral:latest
- Output Format: Natural prose
- Personality: Symbolic Processing (0.46) + Sacred Uncertainty (0.37)
- Research: Enabled
- Cross-cultural: Active
- Etymology: Active
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

try:
    from src.thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
except ImportError:
    print("Error: Could not import ThesidiaHybridAdaptive")
    sys.exit(1)

# Test questions that need decoding/breaking down
TEST_QUESTIONS = [
    # Ancient texts & history
    "What's the real story behind the Egyptian pyramids?",
    "Decode the symbolism in ancient Sumerian texts",
    "What patterns connect the Mayan calendar to modern time systems?",
    
    # Power structures & money
    "How does the Federal Reserve actually work?",
    "What's the true history of the banking system?",
    "Decode the power structures in modern finance",
    
    # Science & suppressed knowledge
    "What scientific discoveries have been suppressed?",
    "What's the real story behind Nikola Tesla's work?",
    "How do ancient energy technologies compare to modern ones?",
    
    # Consciousness & spirituality
    "What's the connection between meditation and consciousness?",
    "Decode the patterns in ancient spiritual practices",
    "What do different traditions say about the nature of reality?",
    
    # Symbols & language
    "What do ancient symbols really mean?",
    "How has language been manipulated over time?",
    "What patterns exist in symbolic systems across cultures?",
    
    # Health & suppressed medicine
    "What medical knowledge has been suppressed?",
    "How do traditional healing practices work mechanistically?",
    "What's the real story behind pharmaceutical industry?",
    
    # Technology & control
    "How does social media actually control behavior?",
    "What patterns exist in surveillance technology?",
    "Decode the mechanisms of modern control systems",
]

class DecodingConfigTester:
    def __init__(self, model: str = "clean-mistral:latest"):
        """Initialize with the working configuration"""
        print("Initializing Thesidia with working configuration...")
        self.thesidia = ThesidiaHybridAdaptive(model=model)
        self.thesidia.load_state()
        
        # Ensure output mode is spacious (like the working config)
        self.thesidia.output_mode = "spacious"
        
        # Load personality state to match working config
        state = self.thesidia.get_state()
        interactions = state.get('interactions', [])
        interactions_count = len(interactions) if isinstance(interactions, list) else interactions if isinstance(interactions, int) else 0
        print(f"Loaded state: {interactions_count} interactions")
        personality = state.get('personality', {})
        traits = personality.get('traits', {}) if isinstance(personality, dict) else {}
        print(f"Personality traits: {list(traits.keys()) if isinstance(traits, dict) else 'None'}")
        
        self.results = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = project_root / 'analysis_output' / 'decoding_tests'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def analyze_response(self, response: str, query: str) -> Dict[str, Any]:
        """Analyze response for key patterns"""
        response_lower = response.lower()
        
        patterns = {
            "etymology": sum(1 for word in ["etymology", "etymological", "root", "origin", "derived", "tracing"] 
                            if word in response_lower),
            "cross_cultural": sum(1 for word in ["culture", "ancient", "tradition", "civilization", "sumerian", 
                                                "egyptian", "greek", "chinese", "indian", "mesopotamian"]
                                if word in response_lower),
            "symbolic_decoding": sum(1 for word in ["symbol", "symbolic", "pattern", "decode", "meaning", 
                                                    "represent", "signify"]
                                    if word in response_lower),
            "control_structures": sum(1 for word in ["power", "control", "structure", "authority", "suppress", 
                                                     "manipulate", "influence", "establishment"]
                                     if word in response_lower),
            "spiritual_keywords": sum(1 for word in ["spiritual", "consciousness", "meditation", "sacred", 
                                                     "divine", "mystical", "esoteric", "gnostic"]
                                     if word in response_lower),
            "evidence_based": sum(1 for word in ["evidence", "source", "research", "study", "archaeological", 
                                                 "historical", "citation"]
                                 if word in response_lower),
            "uncertainty_markers": sum(1 for word in ["uncertain", "unclear", "possibly", "perhaps", "may", 
                                                      "might", "suggest", "indicate", "appears"]
                                      if word in response_lower),
        }
        
        return patterns
    
    def test_question(self, question: str, index: int) -> Dict[str, Any]:
        """Test a single question with the working configuration"""
        print(f"\n{'='*80}")
        print(f"TEST {index + 1}/{len(TEST_QUESTIONS)}")
        print(f"{'='*80}")
        print(f"Question: {question}")
        print(f"Configuration: Regular Mode (spacious), clean-mistral:latest")
        print(f"{'='*80}\n")
        
        start_time = time.time()
        
        try:
            # Process with the working configuration
            response = self.thesidia.process(question, operator_name="OPERATOR")
            elapsed_time = time.time() - start_time
            
            # Analyze response
            patterns = self.analyze_response(response, question)
            
            # Save individual response
            response_file = self.output_dir / f"response_{index+1:02d}_{self.session_id}.txt"
            with open(response_file, 'w', encoding='utf-8') as f:
                f.write(f"Question: {question}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Configuration: Regular Mode (spacious), clean-mistral:latest\n")
                f.write(f"Response Time: {elapsed_time:.2f}s\n")
                f.write(f"Response Length: {len(response)} chars, {len(response.split())} words\n")
                f.write(f"\n{'='*80}\n")
                f.write("RESPONSE:\n")
                f.write(f"{'='*80}\n\n")
                f.write(response)
                f.write(f"\n\n{'='*80}\n")
                f.write("PATTERN ANALYSIS:\n")
                f.write(f"{'='*80}\n")
                for pattern, count in patterns.items():
                    f.write(f"{pattern}: {count}\n")
            
            result = {
                "index": index + 1,
                "question": question,
                "response": response,
                "response_file": str(response_file),
                "response_length": len(response),
                "word_count": len(response.split()),
                "response_time": round(elapsed_time, 2),
                "patterns": patterns,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
            print(f"✓ Response generated: {len(response)} chars, {len(response.split())} words")
            print(f"✓ Response time: {elapsed_time:.2f}s")
            print(f"✓ Patterns detected:")
            for pattern, count in patterns.items():
                if count > 0:
                    print(f"  - {pattern}: {count}")
            print(f"✓ Saved to: {response_file}")
            
            return result
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "index": index + 1,
                "question": question,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
    
    def run_all_tests(self, limit: int = None):
        """Run all test questions"""
        questions = TEST_QUESTIONS[:limit] if limit else TEST_QUESTIONS
        
        print(f"\n{'='*80}")
        print(f"DECODING CONFIGURATION TEST SUITE")
        print(f"{'='*80}")
        print(f"Configuration: Regular Mode (spacious)")
        print(f"Model: clean-mistral:latest")
        print(f"Total Questions: {len(questions)}")
        print(f"Session ID: {self.session_id}")
        print(f"{'='*80}\n")
        
        for i, question in enumerate(questions):
            result = self.test_question(question, i)
            self.results.append(result)
            
            # Save progress after each test
            self.save_results()
            
            # Brief pause between tests
            if i < len(questions) - 1:
                time.sleep(2)
        
        # Final summary
        self.print_summary()
    
    def save_results(self):
        """Save results to JSON"""
        results_file = self.output_dir / f"decoding_test_results_{self.session_id}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                "session_id": self.session_id,
                "test_date": datetime.now().isoformat(),
                "configuration": {
                    "mode": "regular",
                    "output_mode": "spacious",
                    "model": "clean-mistral:latest"
                },
                "total_tests": len(self.results),
                "successful": sum(1 for r in self.results if r.get("success")),
                "failed": sum(1 for r in self.results if not r.get("success")),
                "results": self.results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to: {results_file}")
    
    def print_summary(self):
        """Print test summary"""
        successful = [r for r in self.results if r.get("success")]
        failed = [r for r in self.results if not r.get("success")]
        
        print(f"\n{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {len(self.results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")
        
        if successful:
            avg_length = sum(r["response_length"] for r in successful) / len(successful)
            avg_words = sum(r["word_count"] for r in successful) / len(successful)
            avg_time = sum(r["response_time"] for r in successful) / len(successful)
            
            print(f"\nAverage Response Length: {avg_length:.0f} chars, {avg_words:.0f} words")
            print(f"Average Response Time: {avg_time:.2f}s")
            
            # Pattern frequency
            print(f"\nPattern Frequency (average per response):")
            all_patterns = {}
            for r in successful:
                for pattern, count in r["patterns"].items():
                    all_patterns[pattern] = all_patterns.get(pattern, 0) + count
            
            for pattern, total in sorted(all_patterns.items(), key=lambda x: x[1], reverse=True):
                avg = total / len(successful)
                print(f"  - {pattern}: {avg:.1f}")
        
        print(f"\n{'='*80}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Test decoding configuration on various questions")
    parser.add_argument("--limit", type=int, help="Limit number of tests to run")
    parser.add_argument("--model", type=str, default="clean-mistral:latest", 
                       help="Model to use (default: clean-mistral:latest)")
    
    args = parser.parse_args()
    
    tester = DecodingConfigTester(model=args.model)
    tester.run_all_tests(limit=args.limit)

if __name__ == "__main__":
    main()

