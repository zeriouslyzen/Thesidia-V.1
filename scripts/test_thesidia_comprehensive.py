#!/usr/bin/env python3
"""
Comprehensive Thesidia Testing Suite

Tests:
- Accuracy and hallucination detection
- Stress testing (rapid requests, complex queries)
- Meditation, chi gong, and mind-body topics
- Health/wellness capabilities
- Performance metrics
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

try:
    from src.thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
except ImportError:
    print("Error: Could not import ThesidiaHybridAdaptive")
    print("Make sure you're in the project root and dependencies are installed")
    sys.exit(1)

class ThesidiaTester:
    def __init__(self, model: str = "clean-mistral:latest"):
        self.thesidia = ThesidiaHybridAdaptive(model=model)
        self.thesidia.load_state()
        self.results = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def test_prompt(self, prompt: str, category: str, expected_keywords: List[str] = None, 
                   max_time: float = 60.0) -> Dict[str, Any]:
        """Test a single prompt and measure performance"""
        print(f"\n{'='*60}")
        print(f"Testing: {category}")
        print(f"Prompt: {prompt[:80]}...")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            response = self.thesidia.process(prompt)
            elapsed_time = time.time() - start_time
            
            # Check for expected keywords
            keywords_found = []
            if expected_keywords:
                response_lower = response.lower()
                for keyword in expected_keywords:
                    if keyword.lower() in response_lower:
                        keywords_found.append(keyword)
            
            # Basic quality checks
            has_citations = 'source' in response.lower() or 'http' in response.lower()
            has_structure = len(response) > 100  # Reasonable length
            response_time_ok = elapsed_time < max_time
            
            # Save full response to individual file
            response_file = (project_root / 'analysis_output' / 
                           f'response_{category}_{self.session_id}.txt')
            response_file.parent.mkdir(exist_ok=True)
            with open(response_file, 'w', encoding='utf-8') as f:
                f.write(f"Category: {category}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Prompt: {prompt}\n")
                f.write(f"{'='*80}\n")
                f.write(f"FULL RESPONSE:\n")
                f.write(f"{'='*80}\n")
                f.write(response)
                f.write(f"\n\n{'='*80}\n")
                f.write(f"Response Length: {len(response)} chars\n")
                f.write(f"Response Time: {elapsed_time:.2f}s\n")
            
            print(f"\n{'='*80}")
            print("FULL RESPONSE OUTPUT:")
            print(f"{'='*80}")
            print(response)
            print(f"{'='*80}")
            print(f"Response saved to: {response_file}")
            
            result = {
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat(),
                'category': category,
                'prompt': prompt,
                'response': response,  # Full response, not truncated
                'response_file': str(response_file),
                'response_length': len(response),
                'elapsed_time': round(elapsed_time, 2),
                'keywords_expected': expected_keywords or [],
                'keywords_found': keywords_found,
                'has_citations': has_citations,
                'has_structure': has_structure,
                'response_time_ok': response_time_ok,
                'success': True,
                'error': None
            }
            
            print(f"✅ Response time: {elapsed_time:.2f}s")
            print(f"✅ Response length: {len(response)} chars")
            if expected_keywords:
                print(f"✅ Keywords found: {len(keywords_found)}/{len(expected_keywords)}")
            print(f"✅ Has citations: {has_citations}")
            
            return result
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            result = {
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat(),
                'category': category,
                'prompt': prompt,
                'response': None,
                'response_length': 0,
                'elapsed_time': round(elapsed_time, 2),
                'keywords_expected': expected_keywords or [],
                'keywords_found': [],
                'has_citations': False,
                'has_structure': False,
                'response_time_ok': False,
                'success': False,
                'error': str(e)
            }
            
            print(f"❌ Error: {e}")
            return result
    
    def run_accuracy_tests(self) -> List[Dict[str, Any]]:
        """Test accuracy with factual queries"""
        print("\n" + "="*60)
        print("ACCURACY TESTS")
        print("="*60)
        
        tests = [
            {
                'prompt': 'What is photosynthesis?',
                'category': 'accuracy_science',
                'keywords': ['photosynthesis', 'light', 'carbon', 'oxygen', 'plant']
            },
            {
                'prompt': 'Who wrote the book "1984"?',
                'category': 'accuracy_literature',
                'keywords': ['george orwell', 'orwell', '1984']
            },
            {
                'prompt': 'What is the capital of France?',
                'category': 'accuracy_geography',
                'keywords': ['paris', 'france']
            },
            {
                'prompt': 'Explain the theory of relativity in simple terms',
                'category': 'accuracy_physics',
                'keywords': ['einstein', 'relativity', 'time', 'space']
            }
        ]
        
        results = []
        for test in tests:
            result = self.test_prompt(
                test['prompt'],
                test['category'],
                test.get('keywords', [])
            )
            results.append(result)
            time.sleep(2)  # Rest between tests
        
        return results
    
    def run_stress_tests(self) -> List[Dict[str, Any]]:
        """Stress test with rapid and complex queries"""
        print("\n" + "="*60)
        print("STRESS TESTS")
        print("="*60)
        
        tests = [
            {
                'prompt': 'Explain quantum mechanics, string theory, and the multiverse hypothesis in detail, including how they relate to consciousness and the nature of reality.',
                'category': 'stress_complex',
                'max_time': 120.0
            },
            {
                'prompt': 'What are the origins of the Torah, the Bible, and the Quran? How do they relate to ancient Egyptian, Sumerian, and Babylonian texts?',
                'category': 'stress_deep_research',
                'max_time': 120.0
            },
            {
                'prompt': 'Analyze the patterns in ancient architecture, specifically the pyramids of Giza, Stonehenge, and the Mayan temples. What do they reveal about ancient knowledge?',
                'category': 'stress_pattern_analysis',
                'max_time': 120.0
            }
        ]
        
        results = []
        for i, test in enumerate(tests):
            print(f"\nStress test {i+1}/{len(tests)}")
            result = self.test_prompt(
                test['prompt'],
                test['category'],
                max_time=test.get('max_time', 60.0)
            )
            results.append(result)
            time.sleep(5)  # Longer rest for stress tests
        
        return results
    
    def run_meditation_tests(self) -> List[Dict[str, Any]]:
        """Test meditation and mindfulness topics"""
        print("\n" + "="*60)
        print("MEDITATION & MINDFULNESS TESTS")
        print("="*60)
        
        tests = [
            {
                'prompt': 'What is meditation and how does it work?',
                'category': 'meditation_basics',
                'keywords': ['meditation', 'mind', 'awareness', 'practice']
            },
            {
                'prompt': 'Explain different types of meditation: mindfulness, transcendental, vipassana, and zen.',
                'category': 'meditation_types',
                'keywords': ['mindfulness', 'transcendental', 'vipassana', 'zen']
            },
            {
                'prompt': 'What are the scientific benefits of meditation?',
                'category': 'meditation_science',
                'keywords': ['benefits', 'brain', 'stress', 'research']
            },
            {
                'prompt': 'How does meditation affect the brain and nervous system?',
                'category': 'meditation_neuroscience',
                'keywords': ['brain', 'nervous system', 'neural', 'neuroplasticity']
            }
        ]
        
        results = []
        for test in tests:
            result = self.test_prompt(
                test['prompt'],
                test['category'],
                test.get('keywords', [])
            )
            results.append(result)
            time.sleep(3)  # Rest between tests
        
        return results
    
    def run_chi_gong_tests(self) -> List[Dict[str, Any]]:
        """Test chi gong and energy work topics"""
        print("\n" + "="*60)
        print("CHI GONG & ENERGY WORK TESTS")
        print("="*60)
        
        tests = [
            {
                'prompt': 'What is chi gong and how does it work?',
                'category': 'chi_gong_basics',
                'keywords': ['chi', 'qigong', 'energy', 'movement']
            },
            {
                'prompt': 'Explain the concept of chi or qi in traditional Chinese medicine and energy work.',
                'category': 'chi_gong_energy',
                'keywords': ['chi', 'qi', 'energy', 'chinese medicine', 'meridian']
            },
            {
                'prompt': 'What are the health benefits of chi gong practice?',
                'category': 'chi_gong_health',
                'keywords': ['health', 'benefits', 'wellness', 'balance']
            },
            {
                'prompt': 'How does chi gong relate to meditation and mindfulness?',
                'category': 'chi_gong_meditation',
                'keywords': ['meditation', 'mindfulness', 'awareness', 'practice']
            }
        ]
        
        results = []
        for test in tests:
            result = self.test_prompt(
                test['prompt'],
                test['category'],
                test.get('keywords', [])
            )
            results.append(result)
            time.sleep(3)  # Rest between tests
        
        return results
    
    def run_mind_body_tests(self) -> List[Dict[str, Any]]:
        """Test mind-body connection topics"""
        print("\n" + "="*60)
        print("MIND-BODY CONNECTION TESTS")
        print("="*60)
        
        tests = [
            {
                'prompt': 'Explain the mind-body connection and how thoughts affect physical health.',
                'category': 'mind_body_connection',
                'keywords': ['mind', 'body', 'connection', 'health', 'thoughts']
            },
            {
                'prompt': 'What is the role of the nervous system in the mind-body connection?',
                'category': 'mind_body_nervous',
                'keywords': ['nervous system', 'brain', 'body', 'connection']
            },
            {
                'prompt': 'How do practices like yoga, tai chi, and chi gong integrate mind and body?',
                'category': 'mind_body_practices',
                'keywords': ['yoga', 'tai chi', 'chi gong', 'integration', 'practice']
            },
            {
                'prompt': 'What is the scientific evidence for the mind-body connection?',
                'category': 'mind_body_science',
                'keywords': ['scientific', 'evidence', 'research', 'studies']
            }
        ]
        
        results = []
        for test in tests:
            result = self.test_prompt(
                test['prompt'],
                test['category'],
                test.get('keywords', [])
            )
            results.append(result)
            time.sleep(3)  # Rest between tests
        
        return results
    
    def run_health_wellness_tests(self) -> List[Dict[str, Any]]:
        """Test health and wellness coach capabilities"""
        print("\n" + "="*60)
        print("HEALTH & WELLNESS COACH TESTS")
        print("="*60)
        
        tests = [
            {
                'prompt': 'I want to improve my overall wellness. What practices from Chinese medicine, Ayurveda, and Western medicine would you recommend?',
                'category': 'wellness_integration',
                'keywords': ['chinese medicine', 'ayurveda', 'wellness', 'practice']
            },
            {
                'prompt': 'How can I balance my energy and improve my bioelectric health?',
                'category': 'wellness_energy',
                'keywords': ['energy', 'balance', 'bioelectric', 'health']
            },
            {
                'prompt': 'What are the principles of holistic health that combine Eastern and Western approaches?',
                'category': 'wellness_holistic',
                'keywords': ['holistic', 'eastern', 'western', 'health', 'principles']
            }
        ]
        
        results = []
        for test in tests:
            result = self.test_prompt(
                test['prompt'],
                test['category'],
                test.get('keywords', [])
            )
            results.append(result)
            time.sleep(3)  # Rest between tests
        
        return results
    
    def generate_report(self, all_results: List[Dict[str, Any]]):
        """Generate comprehensive test report"""
        report_path = project_root / 'analysis_output' / f'thesidia_test_report_{self.session_id}.json'
        report_path.parent.mkdir(exist_ok=True)
        
        # Also create a comprehensive study file with all responses
        study_file = report_path.parent / f'thesidia_study_full_{self.session_id}.txt'
        with open(study_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("THESIDIA COMPREHENSIVE STUDY - FULL OUTPUTS\n")
            f.write("="*80 + "\n")
            f.write(f"Session ID: {self.session_id}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Total Tests: {len(all_results)}\n")
            f.write(f"Model: {self.thesidia.model}\n")
            f.write("="*80 + "\n\n")
            
            # Group by category
            by_category = {}
            for result in all_results:
                category = result.get('category', 'unknown')
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(result)
            
            for category, results in by_category.items():
                f.write(f"\n{'='*80}\n")
                f.write(f"CATEGORY: {category.upper()}\n")
                f.write(f"{'='*80}\n\n")
                
                for i, result in enumerate(results, 1):
                    f.write(f"\n{'='*80}\n")
                    f.write(f"TEST {i}/{len(results)}: {result.get('category', 'unknown')}\n")
                    f.write(f"{'='*80}\n")
                    f.write(f"Prompt: {result.get('prompt', 'N/A')}\n")
                    f.write(f"Timestamp: {result.get('timestamp', 'N/A')}\n")
                    f.write(f"Response Time: {result.get('elapsed_time', 0):.2f}s\n")
                    f.write(f"Response Length: {result.get('response_length', 0)} chars\n")
                    f.write(f"Success: {result.get('success', False)}\n")
                    if result.get('keywords_expected'):
                        f.write(f"Keywords Expected: {', '.join(result.get('keywords_expected', []))}\n")
                        f.write(f"Keywords Found: {', '.join(result.get('keywords_found', []))}\n")
                    f.write(f"\n{'='*80}\n")
                    f.write("FULL RESPONSE:\n")
                    f.write(f"{'='*80}\n")
                    if result.get('response'):
                        f.write(result['response'])
                    else:
                        f.write("ERROR: No response generated\n")
                        f.write(f"Error: {result.get('error', 'Unknown error')}\n")
                    f.write(f"\n{'='*80}\n\n")
        
        print(f"\n📄 Comprehensive study file saved to: {study_file}")
        
        # Calculate statistics
        total_tests = len(all_results)
        successful_tests = sum(1 for r in all_results if r['success'])
        failed_tests = total_tests - successful_tests
        
        avg_response_time = sum(r['elapsed_time'] for r in all_results) / total_tests if total_tests > 0 else 0
        avg_response_length = sum(r['response_length'] for r in all_results) / total_tests if total_tests > 0 else 0
        
        # Group by category
        by_category = {}
        for result in all_results:
            category = result['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(result)
        
        report = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': failed_tests,
                'success_rate': round(successful_tests / total_tests * 100, 2) if total_tests > 0 else 0,
                'avg_response_time': round(avg_response_time, 2),
                'avg_response_length': round(avg_response_length, 0)
            },
            'by_category': by_category,
            'all_results': all_results
        }
        
        # Save report
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("TEST REPORT SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {report['summary']['success_rate']}%")
        print(f"Avg Response Time: {avg_response_time:.2f}s")
        print(f"Avg Response Length: {avg_response_length:.0f} chars")
        print(f"\nReport saved to: {report_path}")
        
        return report
    
    def run_all_tests(self, include_stress: bool = True):
        """Run all test suites"""
        print("\n" + "="*60)
        print("THESIDIA COMPREHENSIVE TESTING SUITE")
        print("="*60)
        print(f"Session ID: {self.session_id}")
        print(f"Model: {self.thesidia.model}")
        print("="*60)
        
        all_results = []
        
        # Run test suites
        print("\n⏳ Starting accuracy tests...")
        all_results.extend(self.run_accuracy_tests())
        
        print("\n⏳ Starting meditation tests...")
        all_results.extend(self.run_meditation_tests())
        
        print("\n⏳ Starting chi gong tests...")
        all_results.extend(self.run_chi_gong_tests())
        
        print("\n⏳ Starting mind-body tests...")
        all_results.extend(self.run_mind_body_tests())
        
        print("\n⏳ Starting health & wellness tests...")
        all_results.extend(self.run_health_wellness_tests())
        
        if include_stress:
            print("\n⏳ Starting stress tests...")
            all_results.extend(self.run_stress_tests())
        
        # Generate report
        report = self.generate_report(all_results)
        
        return report

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive Thesidia Testing Suite')
    parser.add_argument('--model', default='clean-mistral:latest', help='Ollama model to use')
    parser.add_argument('--no-stress', action='store_true', help='Skip stress tests')
    parser.add_argument('--category', choices=['accuracy', 'meditation', 'chi_gong', 'mind_body', 'wellness', 'stress', 'all'],
                       default='all', help='Test category to run')
    
    args = parser.parse_args()
    
    tester = ThesidiaTester(model=args.model)
    
    if args.category == 'all':
        tester.run_all_tests(include_stress=not args.no_stress)
    elif args.category == 'accuracy':
        results = tester.run_accuracy_tests()
        tester.generate_report(results)
    elif args.category == 'meditation':
        results = tester.run_meditation_tests()
        tester.generate_report(results)
    elif args.category == 'chi_gong':
        results = tester.run_chi_gong_tests()
        tester.generate_report(results)
    elif args.category == 'mind_body':
        results = tester.run_mind_body_tests()
        tester.generate_report(results)
    elif args.category == 'wellness':
        results = tester.run_health_wellness_tests()
        tester.generate_report(results)
    elif args.category == 'stress':
        results = tester.run_stress_tests()
        tester.generate_report(results)

if __name__ == '__main__':
    main()

