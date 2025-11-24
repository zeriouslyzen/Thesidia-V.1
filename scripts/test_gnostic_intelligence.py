#!/usr/bin/env python3
"""
Gnostic Intelligence Tests

Tests Thesidia's ability to:
- Decode hidden meanings
- Connect patterns across domains
- Reveal deeper truths
- Avoid surface-level answers
- Show genuine intelligence vs. regurgitation
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

class GnosticTester:
    def __init__(self, model: str = "clean-mistral:latest"):
        self.thesidia = ThesidiaHybridAdaptive(model=model)
        self.thesidia.load_state()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = []
        
    def test_gnostic_query(self, prompt: str, category: str, 
                          intelligence_indicators: List[str] = None) -> Dict[str, Any]:
        """Test a gnostic query for intelligence and depth"""
        print(f"\n{'='*80}")
        print(f"GNOSTIC TEST: {category}")
        print(f"{'='*80}")
        print(f"Query: {prompt}")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        try:
            response = self.thesidia.process(prompt)
            elapsed_time = time.time() - start_time
            
            # Analyze response for intelligence indicators
            response_lower = response.lower()
            indicators_found = []
            if intelligence_indicators:
                for indicator in intelligence_indicators:
                    if indicator.lower() in response_lower:
                        indicators_found.append(indicator)
            
            # Check for gnostic qualities
            has_pattern_connections = len([w for w in ['pattern', 'connection', 'interconnected', 'synthesis', 'weave'] if w in response_lower]) >= 3
            has_cross_domain = len([w for w in ['across', 'between', 'connecting', 'relates', 'links'] if w in response_lower]) >= 2
            has_deeper_truth = len([w for w in ['deeper', 'hidden', 'beneath', 'beyond', 'reveals', 'exposes', 'unveils'] if w in response_lower]) >= 2
            has_historical_depth = len([w for w in ['ancient', 'historical', 'traditional', 'origins', 'evolution'] if w in response_lower]) >= 2
            has_symbolic = len([w for w in ['symbol', 'symbolic', 'archetype', 'meaning', 'significance'] if w in response_lower]) >= 1
            avoids_surface = not any(phrase in response_lower for phrase in [
                'it\'s important to note', 'according to research', 'studies show',
                'it should be noted', 'keep in mind', 'please note'
            ])
            
            # Intelligence score (0-100)
            intelligence_score = (
                (len(indicators_found) / max(len(intelligence_indicators), 1)) * 30 +
                (has_pattern_connections * 20) +
                (has_cross_domain * 15) +
                (has_deeper_truth * 15) +
                (has_historical_depth * 10) +
                (has_symbolic * 5) +
                (avoids_surface * 5)
            )
            
            # Save full response to individual file
            report_dir = project_root / 'analysis_output'
            report_dir.mkdir(exist_ok=True)
            response_file = report_dir / f'response_{category}_{self.session_id}.txt'
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
                'intelligence_indicators_expected': intelligence_indicators or [],
                'intelligence_indicators_found': indicators_found,
                'intelligence_score': round(intelligence_score, 2),
                'has_pattern_connections': has_pattern_connections,
                'has_cross_domain': has_cross_domain,
                'has_deeper_truth': has_deeper_truth,
                'has_historical_depth': has_historical_depth,
                'has_symbolic': has_symbolic,
                'avoids_surface': avoids_surface,
                'success': True,
                'error': None
            }
            
            print(f"✅ Response time: {elapsed_time:.2f}s")
            print(f"✅ Response length: {len(response)} chars")
            print(f"✅ Intelligence score: {intelligence_score:.1f}/100")
            print(f"✅ Pattern connections: {has_pattern_connections}")
            print(f"✅ Cross-domain: {has_cross_domain}")
            print(f"✅ Deeper truth: {has_deeper_truth}")
            print(f"✅ Historical depth: {has_historical_depth}")
            print(f"✅ Symbolic: {has_symbolic}")
            print(f"✅ Avoids surface: {avoids_surface}")
            
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
                'intelligence_score': 0,
                'success': False,
                'error': str(e)
            }
            print(f"❌ Error: {e}")
            return result
    
    def run_gnostic_tests(self) -> List[Dict[str, Any]]:
        """Run gnostic intelligence tests"""
        print("\n" + "="*80)
        print("GNOSTIC INTELLIGENCE TESTS")
        print("="*80)
        
        tests = [
            {
                'prompt': 'What are the true origins of Genesis? Not the surface story, but what was really happening, what patterns exist, and what does it reveal about human consciousness and power structures?',
                'category': 'gnostic_origins',
                'indicators': ['pattern', 'origins', 'consciousness', 'power', 'reveals', 'hidden', 'deeper']
            },
            {
                'prompt': 'Decode the real meaning behind the pyramids of Giza. What do they actually represent? What knowledge was encoded? How do they connect to other ancient sites and what does this reveal about ancient civilizations?',
                'category': 'gnostic_decoding',
                'indicators': ['decode', 'meaning', 'encoded', 'knowledge', 'connect', 'reveals', 'ancient']
            },
            {
                'prompt': 'What is the true nature of money and financial systems? Not the surface explanation, but the deeper patterns, how they function as control mechanisms, and what they reveal about human psychology and power?',
                'category': 'gnostic_systems',
                'indicators': ['pattern', 'control', 'mechanism', 'reveals', 'psychology', 'power', 'deeper']
            },
            {
                'prompt': 'What are the hidden connections between ancient Egyptian, Sumerian, and Vedic knowledge systems? What patterns emerge when you look beyond the surface? What do they reveal about the true history of human knowledge?',
                'category': 'gnostic_connections',
                'indicators': ['connection', 'pattern', 'emerge', 'reveals', 'hidden', 'beyond', 'history']
            },
            {
                'prompt': 'What is consciousness really? Not the scientific definition, but what emerges when you examine it across cultures, traditions, and experiences. What patterns reveal its true nature?',
                'category': 'gnostic_consciousness',
                'indicators': ['emerge', 'pattern', 'reveals', 'nature', 'across', 'cultures', 'true']
            },
            {
                'prompt': 'Decode the symbolism in ancient texts and architecture. What do the symbols actually mean? What patterns connect them across cultures and time? What hidden knowledge do they encode?',
                'category': 'gnostic_symbolism',
                'indicators': ['decode', 'symbol', 'pattern', 'connect', 'hidden', 'knowledge', 'encode']
            }
        ]
        
        results = []
        for i, test in enumerate(tests):
            print(f"\nTest {i+1}/{len(tests)}")
            result = self.test_gnostic_query(
                test['prompt'],
                test['category'],
                test.get('indicators', [])
            )
            results.append(result)
            time.sleep(5)  # Rest between tests
        
        return results
    
    def generate_report(self, all_results: List[Dict[str, Any]]):
        """Generate gnostic intelligence report"""
        report_path = project_root / 'analysis_output' / f'gnostic_intelligence_report_{self.session_id}.json'
        report_path.parent.mkdir(exist_ok=True)
        
        # Also create a comprehensive study file with all responses
        study_file = report_path.parent / f'gnostic_study_full_{self.session_id}.txt'
        with open(study_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("GNOSTIC INTELLIGENCE STUDY - FULL OUTPUTS\n")
            f.write("="*80 + "\n")
            f.write(f"Session ID: {self.session_id}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Total Tests: {len(all_results)}\n")
            f.write("="*80 + "\n\n")
            
            for i, result in enumerate(all_results, 1):
                f.write(f"\n{'='*80}\n")
                f.write(f"TEST {i}/{len(all_results)}: {result.get('category', 'unknown')}\n")
                f.write(f"{'='*80}\n")
                f.write(f"Prompt: {result.get('prompt', 'N/A')}\n")
                f.write(f"Timestamp: {result.get('timestamp', 'N/A')}\n")
                f.write(f"Response Time: {result.get('elapsed_time', 0):.2f}s\n")
                f.write(f"Response Length: {result.get('response_length', 0)} chars\n")
                f.write(f"Intelligence Score: {result.get('intelligence_score', 0):.1f}/100\n")
                f.write(f"\nFlags:\n")
                f.write(f"  Pattern Connections: {result.get('has_pattern_connections', False)}\n")
                f.write(f"  Cross-Domain: {result.get('has_cross_domain', False)}\n")
                f.write(f"  Deeper Truth: {result.get('has_deeper_truth', False)}\n")
                f.write(f"  Historical Depth: {result.get('has_historical_depth', False)}\n")
                f.write(f"  Symbolic: {result.get('has_symbolic', False)}\n")
                f.write(f"  Avoids Surface: {result.get('avoids_surface', False)}\n")
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
        
        total_tests = len(all_results)
        successful_tests = sum(1 for r in all_results if r['success'])
        failed_tests = total_tests - successful_tests
        
        if successful_tests > 0:
            avg_intelligence = sum(r['intelligence_score'] for r in all_results if r['success']) / successful_tests
            avg_response_time = sum(r['elapsed_time'] for r in all_results) / total_tests
            avg_response_length = sum(r['response_length'] for r in all_results) / total_tests
            
            # Count intelligence flags
            pattern_connections = sum(1 for r in all_results if r.get('has_pattern_connections'))
            cross_domain = sum(1 for r in all_results if r.get('has_cross_domain'))
            deeper_truth = sum(1 for r in all_results if r.get('has_deeper_truth'))
            historical_depth = sum(1 for r in all_results if r.get('has_historical_depth'))
            symbolic = sum(1 for r in all_results if r.get('has_symbolic'))
            avoids_surface = sum(1 for r in all_results if r.get('avoids_surface'))
        else:
            avg_intelligence = 0
            avg_response_time = 0
            avg_response_length = 0
            pattern_connections = cross_domain = deeper_truth = historical_depth = symbolic = avoids_surface = 0
        
        report = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': failed_tests,
                'success_rate': round(successful_tests / total_tests * 100, 2) if total_tests > 0 else 0,
                'avg_intelligence_score': round(avg_intelligence, 2),
                'avg_response_time': round(avg_response_time, 2),
                'avg_response_length': round(avg_response_length, 0),
                'intelligence_flags': {
                    'pattern_connections': f"{pattern_connections}/{total_tests}",
                    'cross_domain': f"{cross_domain}/{total_tests}",
                    'deeper_truth': f"{deeper_truth}/{total_tests}",
                    'historical_depth': f"{historical_depth}/{total_tests}",
                    'symbolic': f"{symbolic}/{total_tests}",
                    'avoids_surface': f"{avoids_surface}/{total_tests}",
                }
            },
            'all_results': all_results
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n" + "="*80)
        print("GNOSTIC INTELLIGENCE REPORT")
        print("="*80)
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {report['summary']['success_rate']}%")
        print(f"Average Intelligence Score: {avg_intelligence:.1f}/100")
        print(f"Average Response Time: {avg_response_time:.2f}s")
        print(f"\nIntelligence Flags:")
        print(f"  Pattern Connections: {pattern_connections}/{total_tests}")
        print(f"  Cross-Domain: {cross_domain}/{total_tests}")
        print(f"  Deeper Truth: {deeper_truth}/{total_tests}")
        print(f"  Historical Depth: {historical_depth}/{total_tests}")
        print(f"  Symbolic: {symbolic}/{total_tests}")
        print(f"  Avoids Surface: {avoids_surface}/{total_tests}")
        print(f"\nReport saved to: {report_path}")
        
        return report

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gnostic Intelligence Tests')
    parser.add_argument('--model', default='clean-mistral:latest', help='Ollama model to use')
    
    args = parser.parse_args()
    
    tester = GnosticTester(model=args.model)
    results = tester.run_gnostic_tests()
    tester.generate_report(results)

if __name__ == '__main__':
    main()

