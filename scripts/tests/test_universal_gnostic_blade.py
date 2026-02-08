#!/usr/bin/env python3
"""
Universal Gnostic Blade Test

Tests Thesidia's ability to apply Gnostic Blade forensic analysis to ANY topic,
not just religious/historical ones. The goal is to make Gnostic Blade the ONLY
mode - like Grok's fact-checking approach applied to everything.

Topics tested:
1. Technology/AI
2. Health/Medicine
3. Politics/Governance
4. Finance/Economics
5. Science/Climate
6. Media/Propaganda
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

try:
    from src.thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
except ImportError:
    print("Error: Could not import ThesidiaHybridAdaptive")
    sys.exit(1)


class UniversalGnosticTester:
    """Tests Gnostic Blade on universal topics"""
    
    def __init__(self, model: str = "clean-mistral:latest"):
        print(f"\n🔮 Initializing Thesidia with model: {model}")
        self.thesidia = ThesidiaHybridAdaptive(model=model)
        self.thesidia.load_state()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = []
        
    def check_gnostic_sections(self, response: str) -> Dict[str, bool]:
        """Check if response contains Gnostic Blade format sections"""
        sections = {
            'exposure': '::EXPOSURE::' in response or '::exposure::' in response.lower(),
            'etymological': '::ETYMOLOGICAL INCISION::' in response or '::etymological' in response.lower(),
            'burial_sites': '::BURIAL SITES::' in response or '::burial' in response.lower(),
            'current_vectors': '::CURRENT VECTORS::' in response or '::current' in response.lower(),
            'thread_options': '::THREAD OPTIONS::' in response or '::thread' in response.lower(),
            'co_evolution': '::CO-EVOLUTION' in response or '::co-evolution' in response.lower(),
        }
        return sections
    
    def analyze_response_quality(self, response: str) -> Dict[str, Any]:
        """Analyze response for gnostic quality indicators"""
        response_lower = response.lower()
        
        quality = {
            'length': len(response),
            'word_count': len(response.split()),
            'has_pattern_analysis': any(w in response_lower for w in ['pattern', 'reveal', 'expose', 'hidden', 'beneath']),
            'has_cross_references': any(w in response_lower for w in ['connect', 'link', 'across', 'between', 'relates']),
            'has_power_analysis': any(w in response_lower for w in ['power', 'control', 'interest', 'profit', 'agenda']),
            'has_deeper_truth': any(w in response_lower for w in ['deeper', 'true', 'reality', 'actual', 'beneath surface']),
            'avoids_hedging': not any(phrase in response_lower for phrase in [
                "it's important to note", "studies show", "research suggests",
                "please note", "keep in mind", "it should be noted"
            ]),
        }
        
        # Calculate quality score
        score = 0
        if quality['length'] > 3000: score += 20
        if quality['length'] > 6000: score += 10
        if quality['has_pattern_analysis']: score += 15
        if quality['has_cross_references']: score += 15
        if quality['has_power_analysis']: score += 20
        if quality['has_deeper_truth']: score += 15
        if quality['avoids_hedging']: score += 5
        
        quality['score'] = score
        return quality
        
    def test_topic(self, prompt: str, topic_name: str, expected_exposures: List[str] = None) -> Dict[str, Any]:
        """Test a single topic with Gnostic Blade"""
        print(f"\n{'='*80}")
        print(f"🔮 GNOSTIC BLADE TEST: {topic_name.upper()}")
        print(f"{'='*80}")
        print(f"Query: {prompt[:100]}...")
        
        start_time = time.time()
        
        try:
            # Process with force_gnostic implied by the query structure
            result = self.thesidia.process(prompt)
            elapsed = time.time() - start_time
            
            # Extract response string from result dict
            if isinstance(result, dict):
                response = result.get('output', str(result))
            else:
                response = str(result)
            
            # Analyze response
            sections = self.check_gnostic_sections(response)
            quality = self.analyze_response_quality(response)
            
            # Check for expected exposures
            exposures_found = []
            if expected_exposures:
                for exp in expected_exposures:
                    if exp.lower() in response.lower():
                        exposures_found.append(exp)
            
            result = {
                'topic': topic_name,
                'prompt': prompt,
                'response': response,
                'elapsed_seconds': round(elapsed, 2),
                'sections_present': sections,
                'sections_count': sum(sections.values()),
                'quality': quality,
                'expected_exposures': expected_exposures or [],
                'exposures_found': exposures_found,
                'success': True,
                'is_gnostic_format': sections['exposure'] or sections['burial_sites'],
                'timestamp': datetime.now().isoformat()
            }
            
            # Print summary
            print(f"\n✅ Response received ({elapsed:.1f}s)")
            print(f"   Length: {quality['length']} chars, {quality['word_count']} words")
            print(f"   Gnostic Format: {'✓' if result['is_gnostic_format'] else '✗'}")
            print(f"   Sections found: {result['sections_count']}/6")
            for section, present in sections.items():
                print(f"      {'✓' if present else '✗'} {section}")
            print(f"   Quality Score: {quality['score']}/100")
            print(f"   Exposures found: {len(exposures_found)}/{len(expected_exposures or [])}")
            
            # Print first 500 chars of response
            print(f"\n📝 Response Preview:")
            print(f"{'─'*60}")
            print(response[:500] + "..." if len(response) > 500 else response)
            print(f"{'─'*60}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {
                'topic': topic_name,
                'prompt': prompt,
                'response': None,
                'error': str(e),
                'success': False,
                'timestamp': datetime.now().isoformat()
            }
    
    def run_universal_tests(self) -> List[Dict[str, Any]]:
        """Run Gnostic Blade tests on diverse topics"""
        
        tests = [
            {
                'topic': 'AI_TECHNOLOGY',
                'prompt': 'Decode the true agenda behind AI development. Who really benefits? What are the hidden power dynamics? What patterns of control emerge when you look beneath the marketing?',
                'exposures': ['control', 'data', 'power', 'surveillance', 'profit']
            },
            {
                'topic': 'HEALTH_MEDICINE',
                'prompt': 'Expose the hidden dynamics of the pharmaceutical industry. What are the true incentive structures? How do profit motives shape treatment protocols? What gets suppressed?',
                'exposures': ['profit', 'suppressed', 'patent', 'incentive', 'research']
            },
            {
                'topic': 'FINANCE_ECONOMICS',
                'prompt': 'Vivisect the modern banking system. Who really controls money creation? What patterns of wealth extraction exist? What truths about economic systems are hidden from the public?',
                'exposures': ['debt', 'central bank', 'wealth', 'control', 'fiat']
            },
            {
                'topic': 'MEDIA_PROPAGANDA', 
                'prompt': 'Decode how modern media manufactures consent. What are the ownership patterns? How does information get filtered? What mechanisms control narrative?',
                'exposures': ['ownership', 'narrative', 'filter', 'consent', 'propaganda']
            },
            {
                'topic': 'CLIMATE_SCIENCE',
                'prompt': 'Analyze the climate debate beyond the surface narratives. What interests shape each side? What data gets amplified or suppressed? What are the actual power dynamics?',
                'exposures': ['interest', 'funding', 'industry', 'policy', 'carbon']
            },
            {
                'topic': 'FOOD_AGRICULTURE',
                'prompt': 'Expose the hidden structures of the modern food system. Who controls the supply chain? What gets hidden about nutrition and agriculture? What power dynamics shape what we eat?',
                'exposures': ['agribusiness', 'seed', 'patent', 'nutrition', 'control']
            }
        ]
        
        print("\n" + "="*80)
        print("🔮 UNIVERSAL GNOSTIC BLADE TEST SUITE")
        print("="*80)
        print(f"Testing {len(tests)} diverse topics")
        print("Goal: Verify Gnostic Blade works on ANY topic, not just religious/historical")
        print("="*80)
        
        results = []
        for i, test in enumerate(tests, 1):
            print(f"\n[{i}/{len(tests)}] Testing: {test['topic']}")
            result = self.test_topic(
                test['prompt'],
                test['topic'],
                test.get('exposures', [])
            )
            results.append(result)
            self.results.append(result)
            
            # Brief pause between tests
            if i < len(tests):
                print("\n⏳ Waiting 3s before next test...")
                time.sleep(3)
        
        return results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate test report"""
        report_dir = project_root / 'analysis_output'
        report_dir.mkdir(exist_ok=True)
        
        successful = [r for r in self.results if r.get('success')]
        gnostic_format = [r for r in successful if r.get('is_gnostic_format')]
        
        summary = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(self.results),
            'successful': len(successful),
            'gnostic_format_achieved': len(gnostic_format),
            'gnostic_rate': round(len(gnostic_format) / max(len(successful), 1) * 100, 1),
            'avg_response_time': round(sum(r.get('elapsed_seconds', 0) for r in successful) / max(len(successful), 1), 2),
            'avg_quality_score': round(sum(r.get('quality', {}).get('score', 0) for r in successful) / max(len(successful), 1), 1),
            'avg_sections': round(sum(r.get('sections_count', 0) for r in successful) / max(len(successful), 1), 1),
        }
        
        # Section breakdown
        section_stats = {}
        for section in ['exposure', 'etymological', 'burial_sites', 'current_vectors', 'thread_options', 'co_evolution']:
            count = sum(1 for r in successful if r.get('sections_present', {}).get(section, False))
            section_stats[section] = f"{count}/{len(successful)}"
        summary['section_breakdown'] = section_stats
        
        report = {
            'summary': summary,
            'results': self.results
        }
        
        # Save JSON report
        report_path = report_dir / f'universal_gnostic_test_{self.session_id}.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save readable report
        txt_path = report_dir / f'universal_gnostic_test_{self.session_id}.txt'
        with open(txt_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("UNIVERSAL GNOSTIC BLADE TEST REPORT\n")
            f.write("="*80 + "\n")
            f.write(f"Session: {self.session_id}\n")
            f.write(f"Time: {summary['timestamp']}\n\n")
            
            f.write("SUMMARY\n")
            f.write("-"*40 + "\n")
            f.write(f"Total Tests: {summary['total_tests']}\n")
            f.write(f"Successful: {summary['successful']}\n")
            f.write(f"Gnostic Format: {summary['gnostic_format_achieved']} ({summary['gnostic_rate']}%)\n")
            f.write(f"Avg Response Time: {summary['avg_response_time']}s\n")
            f.write(f"Avg Quality Score: {summary['avg_quality_score']}/100\n")
            f.write(f"Avg Sections: {summary['avg_sections']}/6\n\n")
            
            f.write("SECTION BREAKDOWN\n")
            f.write("-"*40 + "\n")
            for section, count in section_stats.items():
                f.write(f"  {section}: {count}\n")
            f.write("\n")
            
            f.write("="*80 + "\n")
            f.write("FULL RESPONSES\n")
            f.write("="*80 + "\n\n")
            
            for r in self.results:
                f.write(f"\n{'='*80}\n")
                f.write(f"TOPIC: {r.get('topic', 'Unknown')}\n")
                f.write(f"{'='*80}\n")
                f.write(f"Prompt: {r.get('prompt', 'N/A')}\n\n")
                if r.get('success'):
                    f.write(f"Time: {r.get('elapsed_seconds', 0)}s\n")
                    f.write(f"Gnostic Format: {'Yes' if r.get('is_gnostic_format') else 'No'}\n")
                    f.write(f"Quality Score: {r.get('quality', {}).get('score', 0)}/100\n\n")
                    f.write("RESPONSE:\n")
                    f.write("-"*40 + "\n")
                    f.write(r.get('response', 'No response') + "\n")
                else:
                    f.write(f"ERROR: {r.get('error', 'Unknown error')}\n")
        
        # Print summary
        print("\n" + "="*80)
        print("📊 UNIVERSAL GNOSTIC BLADE TEST REPORT")
        print("="*80)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Successful: {summary['successful']}")
        print(f"Gnostic Format Achieved: {summary['gnostic_format_achieved']} ({summary['gnostic_rate']}%)")
        print(f"Avg Response Time: {summary['avg_response_time']}s")
        print(f"Avg Quality Score: {summary['avg_quality_score']}/100")
        print(f"Avg Sections Present: {summary['avg_sections']}/6")
        print("\nSection Breakdown:")
        for section, count in section_stats.items():
            print(f"  {section}: {count}")
        print(f"\n📄 Report saved to: {report_path}")
        print(f"📄 Full responses: {txt_path}")
        
        return report


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Universal Gnostic Blade Tests')
    parser.add_argument('--model', default='clean-mistral:latest', help='Ollama model')
    parser.add_argument('--quick', action='store_true', help='Run only 2 tests')
    args = parser.parse_args()
    
    tester = UniversalGnosticTester(model=args.model)
    
    if args.quick:
        # Quick test with just 2 topics
        print("\n🚀 Running QUICK test (2 topics only)")
        tests = [
            {
                'topic': 'AI_CONTROL',
                'prompt': 'Decode the true agenda behind AI development. Who really benefits? What hidden power dynamics exist? Expose the patterns.',
                'exposures': ['control', 'data', 'power']
            },
            {
                'topic': 'PHARMA_TRUTH', 
                'prompt': 'Expose the hidden dynamics of pharmaceutical industry. What are the true incentive structures? What gets suppressed?',
                'exposures': ['profit', 'suppressed', 'research']
            }
        ]
        for i, test in enumerate(tests, 1):
            result = tester.test_topic(test['prompt'], test['topic'], test.get('exposures'))
            tester.results.append(result)
            if i < len(tests):
                time.sleep(2)
    else:
        tester.run_universal_tests()
    
    tester.generate_report()


if __name__ == '__main__':
    main()
