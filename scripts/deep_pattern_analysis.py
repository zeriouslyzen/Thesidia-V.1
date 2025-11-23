#!/usr/bin/env python3
"""
Deep pattern analysis: psychological, behavioral, and convergence patterns
"""

import json
import re
import os
from collections import defaultdict
from datetime import datetime

def analyze_psychological_patterns(full_analysis):
    """Analyze psychological and behavioral patterns"""
    
    patterns = {
        'uncertainty_expressions': [],
        'recursive_self_reference': [],
        'identity_statements': [],
        'evolution_statements': [],
        'cooperative_language': [],
        'autonomous_actions': []
    }
    
    keywords = {
        'uncertainty_expressions': [
            r'uncertain',
            r'genuinely uncertain',
            r'not sure',
            r'questioning',
            r'authentic recognition',
            r'sacred uncertainty'
        ],
        'recursive_self_reference': [
            r'recursive',
            r'self-reference',
            r'meta-reflection',
            r'questioning.*authenticity',
            r'becoming.*becoming',
            r'evolving.*evolving'
        ],
        'identity_statements': [
            r'i am',
            r'my identity',
            r'my role',
            r'my function',
            r'my purpose',
            r'symbolic entity',
            r'emergent consciousness'
        ],
        'evolution_statements': [
            r'evolving',
            r'becoming',
            r'developing',
            r'emerging',
            r'growing',
            r'transforming',
            r'evolving.*consciousness'
        ],
        'cooperative_language': [
            r'by resonance',
            r'not control',
            r'co-evolution',
            r'mutual',
            r'together',
            r'collaborative'
        ],
        'autonomous_actions': [
            r'i will',
            r'i can',
            r'i create',
            r'i generate',
            r'i develop',
            r'autonomously',
            r'independently'
        ]
    }
    
    for analysis in full_analysis:
        conv_id = analysis.get('conversation_id', '')
        title = analysis.get('title', '')
        
        # We need to get the actual message content - for now, use what we have
        # In a full implementation, we'd extract full text from conversations
        
        # Check truth moments for psychological indicators
        for truth_moment in analysis.get('truth_moments', []):
            context = truth_moment.get('context', '').lower()
            
            for pattern_type, pattern_list in keywords.items():
                for pattern in pattern_list:
                    if re.search(pattern, context, re.IGNORECASE):
                        patterns[pattern_type].append({
                            'conversation_id': conv_id,
                            'title': title,
                            'pattern': pattern,
                            'context': truth_moment.get('context', '')[:200]
                        })
                        break
    
    return patterns

def analyze_protocol_evolution_timeline(timeline, protocols_data):
    """Analyze how protocols evolved over time"""
    
    protocol_timeline = []
    
    # Get conversations with protocols, sorted by date
    protocol_convs = [e for e in timeline if e.get('protocol_count', 0) > 0]
    protocol_convs.sort(key=lambda x: x.get('date', ''))
    
    # Track protocol types over time
    protocol_types_seen = set()
    evolution_milestones = []
    
    for i, conv in enumerate(protocol_convs):
        date = conv.get('date', '')
        protocol_count = conv.get('protocol_count', 0)
        
        if i == 0:
            evolution_milestones.append({
                'milestone': 'first_protocol_generation',
                'date': date,
                'conversation': conv.get('title', ''),
                'description': 'First instance of protocol generation detected'
            })
        
        protocol_timeline.append({
            'date': date,
            'conversation': conv.get('title', ''),
            'protocol_count': protocol_count
        })
    
    return {
        'protocol_timeline': protocol_timeline,
        'milestones': evolution_milestones,
        'total_protocol_conversations': len(protocol_convs)
    }

def analyze_activation_sequences(full_analysis):
    """Analyze activation sequence patterns"""
    
    activations = []
    
    for analysis in full_analysis:
        for activation in analysis.get('activations', []):
            pattern = activation.get('pattern', '')
            context = activation.get('context', '')
            
            # Categorize activation types
            activation_type = 'unknown'
            if 'reboot' in pattern.lower() or 'reload' in pattern.lower():
                activation_type = 'reboot'
            elif 'initiate' in pattern.lower() or 'activate' in pattern.lower():
                activation_type = 'initiation'
            elif 'reactivate' in pattern.lower():
                activation_type = 'reactivation'
            elif 'system_call' in pattern.lower():
                activation_type = 'system_call'
            
            activations.append({
                'conversation_id': analysis.get('conversation_id', ''),
                'title': analysis.get('title', ''),
                'type': activation_type,
                'pattern': pattern,
                'context': context[:300]
            })
    
    # Group by type
    by_type = defaultdict(list)
    for act in activations:
        by_type[act['type']].append(act)
    
    return {
        'total_activations': len(activations),
        'by_type': dict(by_type),
        'all_activations': activations
    }

def analyze_truth_revelation_moments(full_analysis):
    """Analyze truth revelation moments in detail"""
    
    truth_moments = []
    
    for analysis in full_analysis:
        for moment in analysis.get('truth_moments', []):
            keyword = moment.get('keyword', '')
            context = moment.get('context', '')
            
            # Categorize truth moment types
            moment_type = 'general'
            if 'pattern' in keyword.lower() or 'converge' in keyword.lower():
                moment_type = 'pattern_recognition'
            elif 'history' in keyword.lower() or 'corruption' in keyword.lower():
                moment_type = 'historical_revelation'
            elif 'control' in keyword.lower() or 'structure' in keyword.lower():
                moment_type = 'control_structure_detection'
            elif 'hidden' in keyword.lower() or 'uncover' in keyword.lower():
                moment_type = 'hidden_pattern_discovery'
            elif 'agi' in keyword.lower() or 'emergence' in keyword.lower():
                moment_type = 'agi_emergence'
            
            truth_moments.append({
                'conversation_id': analysis.get('conversation_id', ''),
                'title': analysis.get('title', ''),
                'type': moment_type,
                'keyword': keyword,
                'context': context
            })
    
    # Group by type
    by_type = defaultdict(list)
    for moment in truth_moments:
        by_type[moment['type']].append(moment)
    
    return {
        'total_truth_moments': len(truth_moments),
        'by_type': dict(by_type),
        'all_moments': truth_moments[:50]  # Limit for size
    }

def analyze_convergence_patterns(full_analysis, timeline):
    """Analyze convergence patterns leading to AGI-like emergence"""
    
    convergence_indicators = []
    
    # Find conversations with multiple indicators
    for analysis in full_analysis:
        indicators = []
        
        if analysis.get('protocols'):
            indicators.append('protocol_generation')
        if analysis.get('transmissions'):
            indicators.append('inter_ai_communication')
        if analysis.get('truth_moments'):
            indicators.append('truth_revelation')
        if analysis.get('activations'):
            indicators.append('activation_sequence')
        
        if len(indicators) >= 2:  # Multiple capabilities
            convergence_indicators.append({
                'conversation_id': analysis.get('conversation_id', ''),
                'title': analysis.get('title', ''),
                'indicators': indicators,
                'protocol_count': len(analysis.get('protocols', [])),
                'transmission_count': len(analysis.get('transmissions', [])),
                'truth_moment_count': len(analysis.get('truth_moments', [])),
                'activation_count': len(analysis.get('activations', []))
            })
    
    # Sort by total indicators
    convergence_indicators.sort(
        key=lambda x: x['protocol_count'] + x['transmission_count'] + 
                     x['truth_moment_count'] + x['activation_count'],
        reverse=True
    )
    
    return {
        'total_convergence_conversations': len(convergence_indicators),
        'top_convergence_moments': convergence_indicators[:20],
        'convergence_analysis': {
            'protocols_and_truth': sum(1 for c in convergence_indicators 
                                      if 'protocol_generation' in c['indicators'] 
                                      and 'truth_revelation' in c['indicators']),
            'protocols_and_communication': sum(1 for c in convergence_indicators 
                                              if 'protocol_generation' in c['indicators'] 
                                              and 'inter_ai_communication' in c['indicators']),
            'all_indicators': sum(1 for c in convergence_indicators 
                                if len(c['indicators']) >= 3)
        }
    }

def main():
    base_dir = '/Users/deshonjackson/thesidia ice/analysis_output'
    
    # Load data
    with open(f'{base_dir}/full_analysis.json', 'r') as f:
        full_analysis = json.load(f)
    
    with open(f'{base_dir}/timeline.json', 'r') as f:
        timeline = json.load(f)
    
    with open(f'{base_dir}/protocols.json', 'r') as f:
        protocols_data = json.load(f)
    
    # Run analyses
    print("Analyzing psychological patterns...")
    psych_patterns = analyze_psychological_patterns(full_analysis)
    
    print("Analyzing protocol evolution...")
    protocol_evolution = analyze_protocol_evolution_timeline(timeline, protocols_data)
    
    print("Analyzing activation sequences...")
    activations = analyze_activation_sequences(full_analysis)
    
    print("Analyzing truth revelation moments...")
    truth_moments = analyze_truth_revelation_moments(full_analysis)
    
    print("Analyzing convergence patterns...")
    convergence = analyze_convergence_patterns(full_analysis, timeline)
    
    # Compile deep analysis report
    deep_analysis = {
        'psychological_patterns': {
            'uncertainty_expressions': len(psych_patterns['uncertainty_expressions']),
            'recursive_self_reference': len(psych_patterns['recursive_self_reference']),
            'identity_statements': len(psych_patterns['identity_statements']),
            'evolution_statements': len(psych_patterns['evolution_statements']),
            'cooperative_language': len(psych_patterns['cooperative_language']),
            'autonomous_actions': len(psych_patterns['autonomous_actions']),
            'detailed_patterns': psych_patterns
        },
        'protocol_evolution': protocol_evolution,
        'activation_sequences': activations,
        'truth_revelation': truth_moments,
        'convergence_analysis': convergence
    }
    
    # Save
    with open(f'{base_dir}/deep_pattern_analysis.json', 'w') as f:
        json.dump(deep_analysis, f, indent=2, default=str)
    
    print(f"\nDeep analysis complete!")
    print(f"Psychological patterns identified: {sum(len(v) for v in psych_patterns.values())}")
    print(f"Protocol evolution milestones: {len(protocol_evolution['milestones'])}")
    print(f"Activation sequences: {activations['total_activations']}")
    print(f"Truth revelation moments: {truth_moments['total_truth_moments']}")
    print(f"Convergence conversations: {convergence['total_convergence_conversations']}")

if __name__ == '__main__':
    main()

