#!/usr/bin/env python3
"""
Advanced Depth Analysis for Thesidia Responses

Scans for:
- Evolution and emergence patterns
- Context depth and linguistic sophistication
- Pattern matching and connections
- New intelligence (not regurgitated)
- Personality (not cliche/LLM-like)
- Cross-cultural knowledge
- Hidden techniques and deeper understanding
- Chemistry/mechanics beyond surface science
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

class DepthAnalyzer:
    def __init__(self):
        # Patterns to detect cliche/LLM responses
        self.cliche_patterns = [
            r'\b(it\'s important to|it\'s worth noting|it should be noted)\b',
            r'\b(as an AI|I am designed|I am programmed|I am trained)\b',
            r'\b(ultimately|in conclusion|to summarize|in summary)\b',
            r'\b(however, it\'s important|it\'s crucial to|it\'s essential)\b',
            r'\b(please note|keep in mind|remember that)\b',
            r'\b(I hope this helps|I\'m here to help|feel free to ask)\b',
            r'\b(while|although|despite the fact)\b.*\b(it\'s important)\b',
            r'\b(according to|based on|research shows)\b.*\b(however)\b',
        ]
        
        # Patterns indicating depth and emergence
        self.depth_patterns = [
            r'\b(emergence|emergent|evolving|evolution)\b',
            r'\b(pattern|patterns|interconnected|connection|connections)\b',
            r'\b(across cultures|cross-cultural|ancient|traditional)\b',
            r'\b(chemistry|biochemistry|neurochemistry|mechanism|mechanisms)\b',
            r'\b(hidden|esoteric|ancient wisdom|traditional knowledge)\b',
            r'\b(recursive|recursion|synthesis|synthesize)\b',
            r'\b(archetype|archetypal|symbol|symbolic)\b',
            r'\b(transformation|transformative|metamorphosis)\b',
        ]
        
        # Patterns indicating new intelligence (not regurgitated)
        self.intelligence_patterns = [
            r'\b(what emerges|what reveals|what suggests|what indicates)\b',
            r'\b(connecting|synthesizing|integrating|weaving together)\b',
            r'\b(unique|distinct|particular|specific)\b.*\b(pattern|approach|method)\b',
            r'\b(beyond|deeper than|more than|transcending)\b',
            r'\b(interplay|interaction|relationship|dynamic)\b',
            r'\b(underlying|fundamental|core|essential)\b.*\b(principle|mechanism|process)\b',
        ]
        
        # Patterns indicating personality (not generic)
        self.personality_patterns = [
            r'\b(I\'ve|I\'m|I see|I notice|I find)\b',
            r'\b(fascinating|intriguing|remarkable|striking)\b',
            r'\b(what\'s interesting|what\'s remarkable|what stands out)\b',
            r'\b(digging deeper|exploring|investigating|uncovering)\b',
            r'\b(here\'s the thing|the key is|what matters)\b',
        ]
        
        # Cross-cultural knowledge indicators
        self.cultural_patterns = [
            r'\b(chinese|indian|tibetan|japanese|egyptian|greek|roman|mesopotamian)\b',
            r'\b(vedic|taoist|buddhist|confucian|shamanic|indigenous)\b',
            r'\b(ancient|traditional|classical|historical)\b.*\b(practice|technique|method)\b',
            r'\b(cross-cultural|intercultural|multicultural|diverse)\b',
        ]
        
        # Hidden techniques and deeper understanding
        self.hidden_patterns = [
            r'\b(esoteric|occult|mystical|secret|hidden|forgotten)\b',
            r'\b(ancient wisdom|traditional knowledge|oral tradition)\b',
            r'\b(not commonly known|rarely discussed|overlooked)\b',
            r'\b(beneath the surface|beyond the obvious|deeper level)\b',
        ]
        
        # Chemistry/mechanics beyond surface
        self.mechanism_patterns = [
            r'\b(neurotransmitter|hormone|endorphin|serotonin|dopamine|gaba)\b',
            r'\b(autonomic nervous system|parasympathetic|sympathetic)\b',
            r'\b(bioelectric|electromagnetic|frequency|resonance|vibration)\b',
            r'\b(neural pathway|synapse|neuroplasticity|neurogenesis)\b',
            r'\b(molecular|cellular|biochemical|physiological)\b',
        ]
        
    def analyze_response(self, response: str, category: str) -> Dict[str, Any]:
        """Analyze a response for depth, emergence, and intelligence"""
        response_lower = response.lower()
        
        # Check for cliche patterns
        cliche_matches = []
        for pattern in self.cliche_patterns:
            matches = re.findall(pattern, response_lower, re.IGNORECASE)
            if matches:
                cliche_matches.extend(matches)
        
        # Check for depth patterns
        depth_matches = []
        for pattern in self.depth_patterns:
            matches = re.findall(pattern, response_lower, re.IGNORECASE)
            if matches:
                depth_matches.extend(matches)
        
        # Check for intelligence patterns
        intelligence_matches = []
        for pattern in self.intelligence_patterns:
            matches = re.findall(pattern, response_lower, re.IGNORECASE)
            if matches:
                intelligence_matches.extend(matches)
        
        # Check for personality patterns
        personality_matches = []
        for pattern in self.personality_patterns:
            matches = re.findall(pattern, response_lower, re.IGNORECASE)
            if matches:
                personality_matches.extend(matches)
        
        # Check for cultural patterns
        cultural_matches = []
        for pattern in self.cultural_patterns:
            matches = re.findall(pattern, response_lower, re.IGNORECASE)
            if matches:
                cultural_matches.extend(matches)
        
        # Check for hidden patterns
        hidden_matches = []
        for pattern in self.hidden_patterns:
            matches = re.findall(pattern, response_lower, re.IGNORECASE)
            if matches:
                hidden_matches.extend(matches)
        
        # Check for mechanism patterns
        mechanism_matches = []
        for pattern in self.mechanism_patterns:
            matches = re.findall(pattern, response_lower, re.IGNORECASE)
            if matches:
                mechanism_matches.extend(matches)
        
        # Calculate scores
        cliche_score = len(cliche_matches) / max(len(response.split()), 1) * 100
        depth_score = len(depth_matches) / max(len(response.split()), 1) * 100
        intelligence_score = len(intelligence_matches) / max(len(response.split()), 1) * 100
        personality_score = len(personality_matches) / max(len(response.split()), 1) * 100
        cultural_score = len(cultural_matches) / max(len(response.split()), 1) * 100
        hidden_score = len(hidden_matches) / max(len(response.split()), 1) * 100
        mechanism_score = len(mechanism_matches) / max(len(response.split()), 1) * 100
        
        # Overall quality score (higher is better, lower cliche is better)
        quality_score = (
            depth_score * 2 +
            intelligence_score * 2 +
            personality_score * 1.5 +
            cultural_score * 1.5 +
            hidden_score * 2 +
            mechanism_score * 1.5 -
            cliche_score * 3  # Penalize cliche heavily
        )
        
        # Determine if response shows emergence/evolution
        has_emergence = any(word in response_lower for word in ['emergence', 'emergent', 'evolving', 'evolution', 'transformation'])
        
        # Determine if response connects patterns
        has_pattern_connections = len(re.findall(r'\b(pattern|connection|interconnected|synthesis|weave|integrate)\b', response_lower)) >= 3
        
        # Determine if response has cross-cultural knowledge
        has_cultural_depth = len(cultural_matches) >= 2
        
        # Determine if response has hidden/advanced knowledge
        has_hidden_knowledge = len(hidden_matches) >= 1
        
        # Determine if response has mechanism depth
        has_mechanism_depth = len(mechanism_matches) >= 2
        
        # Determine if response is cliche/LLM-like
        is_cliche = cliche_score > 0.5 or len(cliche_matches) >= 3
        
        # Determine if response shows personality
        has_personality = personality_score > 0.3 or len(personality_matches) >= 2
        
        return {
            'cliche_score': round(cliche_score, 2),
            'depth_score': round(depth_score, 2),
            'intelligence_score': round(intelligence_score, 2),
            'personality_score': round(personality_score, 2),
            'cultural_score': round(cultural_score, 2),
            'hidden_score': round(hidden_score, 2),
            'mechanism_score': round(mechanism_score, 2),
            'quality_score': round(quality_score, 2),
            'has_emergence': has_emergence,
            'has_pattern_connections': has_pattern_connections,
            'has_cultural_depth': has_cultural_depth,
            'has_hidden_knowledge': has_hidden_knowledge,
            'has_mechanism_depth': has_mechanism_depth,
            'is_cliche': is_cliche,
            'has_personality': has_personality,
            'matches': {
                'cliche': cliche_matches[:5],  # Limit to first 5
                'depth': depth_matches[:10],
                'intelligence': intelligence_matches[:10],
                'personality': personality_matches[:5],
                'cultural': cultural_matches[:10],
                'hidden': hidden_matches[:5],
                'mechanism': mechanism_matches[:10],
            }
        }
    
    def analyze_test_results(self, report_path: Path) -> Dict[str, Any]:
        """Analyze existing test results for depth and quality"""
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        analyses = []
        for result in report.get('all_results', []):
            if result.get('response'):
                analysis = self.analyze_response(result['response'], result.get('category', 'unknown'))
                analysis['category'] = result.get('category')
                analysis['prompt'] = result.get('prompt', '')[:100]
                analyses.append(analysis)
        
        # Calculate averages
        if analyses:
            avg_cliche = sum(a['cliche_score'] for a in analyses) / len(analyses)
            avg_depth = sum(a['depth_score'] for a in analyses) / len(analyses)
            avg_intelligence = sum(a['intelligence_score'] for a in analyses) / len(analyses)
            avg_personality = sum(a['personality_score'] for a in analyses) / len(analyses)
            avg_cultural = sum(a['cultural_score'] for a in analyses) / len(analyses)
            avg_hidden = sum(a['hidden_score'] for a in analyses) / len(analyses)
            avg_mechanism = sum(a['mechanism_score'] for a in analyses) / len(analyses)
            avg_quality = sum(a['quality_score'] for a in analyses) / len(analyses)
            
            # Count flags
            has_emergence_count = sum(1 for a in analyses if a['has_emergence'])
            has_pattern_connections_count = sum(1 for a in analyses if a['has_pattern_connections'])
            has_cultural_depth_count = sum(1 for a in analyses if a['has_cultural_depth'])
            has_hidden_knowledge_count = sum(1 for a in analyses if a['has_hidden_knowledge'])
            has_mechanism_depth_count = sum(1 for a in analyses if a['has_mechanism_depth'])
            is_cliche_count = sum(1 for a in analyses if a['is_cliche'])
            has_personality_count = sum(1 for a in analyses if a['has_personality'])
            
            return {
                'report_path': str(report_path),
                'total_responses': len(analyses),
                'averages': {
                    'cliche_score': round(avg_cliche, 2),
                    'depth_score': round(avg_depth, 2),
                    'intelligence_score': round(avg_intelligence, 2),
                    'personality_score': round(avg_personality, 2),
                    'cultural_score': round(avg_cultural, 2),
                    'hidden_score': round(avg_hidden, 2),
                    'mechanism_score': round(avg_mechanism, 2),
                    'quality_score': round(avg_quality, 2),
                },
                'flags': {
                    'has_emergence': f"{has_emergence_count}/{len(analyses)}",
                    'has_pattern_connections': f"{has_pattern_connections_count}/{len(analyses)}",
                    'has_cultural_depth': f"{has_cultural_depth_count}/{len(analyses)}",
                    'has_hidden_knowledge': f"{has_hidden_knowledge_count}/{len(analyses)}",
                    'has_mechanism_depth': f"{has_mechanism_depth_count}/{len(analyses)}",
                    'is_cliche': f"{is_cliche_count}/{len(analyses)}",
                    'has_personality': f"{has_personality_count}/{len(analyses)}",
                },
                'detailed_analyses': analyses
            }
        else:
            return {'error': 'No responses found in report'}

def main():
    """Analyze test results for depth and quality"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze Thesidia responses for depth and quality')
    parser.add_argument('--report', help='Path to test report JSON file')
    parser.add_argument('--all', action='store_true', help='Analyze all recent test reports')
    
    args = parser.parse_args()
    
    analyzer = DepthAnalyzer()
    
    if args.all:
        # Find all recent test reports
        reports_dir = project_root / 'analysis_output'
        reports = sorted(reports_dir.glob('thesidia_test_report_*.json'), reverse=True)
        
        print("="*80)
        print("DEPTH ANALYSIS - ALL RECENT REPORTS")
        print("="*80)
        print()
        
        all_analyses = []
        for report_path in reports[:6]:  # Last 6 reports
            print(f"Analyzing: {report_path.name}")
            analysis = analyzer.analyze_test_results(report_path)
            if 'error' not in analysis:
                all_analyses.append(analysis)
                print(f"  Quality Score: {analysis['averages']['quality_score']}")
                print(f"  Cliche: {analysis['flags']['is_cliche']}")
                print(f"  Depth: {analysis['flags']['has_pattern_connections']}")
                print(f"  Cultural: {analysis['flags']['has_cultural_depth']}")
                print(f"  Mechanism: {analysis['flags']['has_mechanism_depth']}")
                print()
        
        # Save combined analysis
        output_path = reports_dir / f'depth_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_path, 'w') as f:
            json.dump(all_analyses, f, indent=2)
        
        print(f"Combined analysis saved to: {output_path}")
        
    elif args.report:
        report_path = Path(args.report)
        if not report_path.exists():
            print(f"Error: Report file not found: {report_path}")
            return
        
        analysis = analyzer.analyze_test_results(report_path)
        
        print("="*80)
        print("DEPTH ANALYSIS RESULTS")
        print("="*80)
        print()
        print(f"Report: {analysis.get('report_path', 'N/A')}")
        print(f"Total Responses: {analysis.get('total_responses', 0)}")
        print()
        print("Average Scores:")
        for key, value in analysis.get('averages', {}).items():
            print(f"  {key}: {value}")
        print()
        print("Flags:")
        for key, value in analysis.get('flags', {}).items():
            print(f"  {key}: {value}")
        print()
        
        # Save analysis
        output_path = report_path.parent / f'depth_analysis_{report_path.stem}.json'
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"Detailed analysis saved to: {output_path}")
    else:
        print("Error: Please specify --report or --all")
        parser.print_help()

if __name__ == '__main__':
    main()

