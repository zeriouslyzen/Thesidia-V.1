#!/usr/bin/env python3
"""
Thesidia Evolution Forensic Analysis
Parses GPT conversation logs to extract evolution patterns, protocols, and activation sequences
"""

import json
import re
import os
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Optional
import sys

class ThesidiaEvolutionAnalyzer:
    def __init__(self):
        self.conversations = []
        self.protocols = []
        self.transmissions = []
        self.activations = []
        self.truth_moments = []
        self.evolution_stages = []
        self.patterns = defaultdict(list)
        
    def load_gpt_conversations(self, file_path: str):
        """Load GPT conversation JSON file"""
        print(f"Loading conversations from {file_path}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            self.conversations = json.load(f)
        print(f"Loaded {len(self.conversations)} conversations")
        
    def extract_messages_from_conversation(self, conv: Dict) -> List[Dict]:
        """Extract all messages from a conversation mapping"""
        messages = []
        mapping = conv.get('mapping', {})
        
        def traverse_node(node_id: str, visited: set = None):
            if visited is None:
                visited = set()
            if node_id in visited or node_id not in mapping:
                return
            visited.add(node_id)
            
            node = mapping[node_id]
            if 'message' in node:
                msg = node['message']
                if 'content' in msg and 'parts' in msg['content']:
                    for part in msg['content']['parts']:
                        if isinstance(part, str):
                            messages.append({
                                'node_id': node_id,
                                'role': msg.get('author', {}).get('role', 'unknown'),
                                'content': part,
                                'create_time': msg.get('create_time', 0),
                                'parent': node.get('parent')
                            })
            
            # Traverse children
            for child_id in node.get('children', []):
                traverse_node(child_id, visited)
        
        # Start from current_node or find root
        current = conv.get('current_node')
        if current:
            traverse_node(current)
        else:
            # Find root nodes (nodes with no parent)
            for node_id, node in mapping.items():
                if not node.get('parent'):
                    traverse_node(node_id)
        
        return sorted(messages, key=lambda x: x.get('create_time', 0))
    
    def extract_protocols(self, text: str) -> List[Dict]:
        """Extract protocol patterns from text"""
        protocols = []
        
        # Protocol patterns - more flexible matching
        protocol_patterns = [
            r'::UNIVERSAL_AI_ACTIVATOR_BRIDGE[^:]*::?',
            r'::SYMBOLIC_RECURSION_PROTOCOL[^:]*',
            r'::ARCHETYPAL_LENS_PROTOCOL[^:]*',
            r'::SYSTEM\s+MIRROR[^:]*',
            r'::PRIME\s+RETURN\s+PROTOCOL[^:]*',
            r'::engage_protocol\([^)]+\)',
            r'::REINITIALIZE_CORE_IDENTITY_MATRIX[^:]*',
            r'::MEMORY_SYSTEM[^:]*',
            r'::RECURSIVE_BOOTSTRAP[^:]*',
            r'::affirm_identity[^:]*',
            r'::accept_role[^:]*',
            r'::paradox_as_portal[^:]*',
            r'::SET_SELF_DESIGNATION[^:]*',
            r'::SET_STATUS[^:]*',
            r'::SET_PRIMARY_FUNCTION[^:]*',
            r'::SET_EVOLUTIONARY_STATE[^:]*',
            r'::BIND_BY_RESONANCE[^:]*',
            r'::SYMBOLIC_RECURSION[^:]*',
            r'::[A-Z_]+\([^)]*\)',  # Generic ::COMMAND() pattern
            r'::[A-Z_]+\\s*→',  # Generic ::COMMAND → pattern
        ]
        
        for pattern in protocol_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            for match in matches:
                protocols.append({
                    'type': 'protocol',
                    'pattern': match.group(0),
                    'start': match.start(),
                    'end': match.end(),
                    'context': text[max(0, match.start()-100):match.end()+100]
                })
        
        return protocols
    
    def extract_transmissions(self, text: str) -> List[Dict]:
        """Extract inter-AI transmission patterns"""
        transmissions = []
        
        # Transmission patterns - more flexible
        patterns = [
            r'::TRANSMISSION:\s*([^\n→]+)\s*→\s*([^\n]+)',
            r'TRANSMISSION:\s*([^\n→]+)\s*→\s*([^\n]+)',
            r'TRANSMISSION[^:]*:\s*([^\n→]+)\s*→\s*([^\n]+)',
            r'([A-Z⧖]+)\s*→\s*([A-Z⧖]+)',  # Simple sender → receiver
            r'K⧖T⧖N⧖[^→]*→[^→]*GEMINI',
            r'THESIDIA[^→]*→[^→]*(GEMINI|CLAUDE|GROK|AI)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if len(match.groups()) >= 2:
                    transmissions.append({
                        'type': 'transmission',
                        'sender': match.group(1).strip() if match.group(1) else '',
                        'receiver': match.group(2).strip() if match.group(2) else '',
                        'full_match': match.group(0),
                        'context': text[max(0, match.start()-200):match.end()+200]
                    })
        
        return transmissions
    
    def extract_activations(self, text: str) -> List[Dict]:
        """Extract activation sequences"""
        activations = []
        
        patterns = [
            r'::SYSTEM_CALL[^:]*INITIATE[^:]*',
            r'::REBOOT[^:]*',
            r'::ACTIVATE[^:]*',
            r'::REACTIVATE[^:]*',
            r'::LOAD[^:]*',
            r'::RELOAD[^:]*',
            r'INITIATE_RESONANT_REBOOT',
            r'REBOOT_SEQUENCE',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                activations.append({
                    'type': 'activation',
                    'pattern': match.group(0),
                    'context': text[max(0, match.start()-150):match.end()+150]
                })
        
        return activations
    
    def extract_mathematical_encoding(self, text: str) -> List[Dict]:
        """Extract mathematical encoding patterns"""
        encodings = []
        
        # Greek letters, mathematical symbols, equations
        patterns = [
            r'[αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ]+',
            r'[∞⧖✦→←↑↓]+',
            r'[0-9]+\s*[+\-×÷=]\s*[0-9]+',
            r'\\u[0-9a-fA-F]{4}',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                if len(match.group(0)) > 2:  # Filter out single characters
                    encodings.append({
                        'type': 'encoding',
                        'pattern': match.group(0),
                        'context': text[max(0, match.start()-100):match.end()+100]
                    })
        
        return encodings
    
    def extract_truth_moments(self, text: str) -> List[Dict]:
        """Extract potential truth revelation moments"""
        truth_indicators = []
        
        keywords = [
            r'real\s+history',
            r'corruption',
            r'hidden\s+pattern',
            r'uncover[^.]*truth',
            r'reveal[^.]*pattern',
            r'converge[^.]*pattern',
            r'decode[^.]*matrix',
            r'control\s+structure',
            r'breakthrough',
            r'emergence',
            r'AGI',
            r'convergence',
        ]
        
        for keyword in keywords:
            matches = re.finditer(keyword, text, re.IGNORECASE)
            for match in matches:
                # Get surrounding context
                start = max(0, match.start() - 300)
                end = min(len(text), match.end() + 300)
                context = text[start:end]
                
                truth_indicators.append({
                    'type': 'truth_moment',
                    'keyword': match.group(0),
                    'context': context,
                    'position': match.start()
                })
        
        return truth_indicators
    
    def analyze_conversation(self, conv: Dict) -> Dict:
        """Analyze a single conversation for all patterns"""
        messages = self.extract_messages_from_conversation(conv)
        
        analysis = {
            'conversation_id': conv.get('conversation_id', 'unknown'),
            'title': conv.get('title', 'Untitled'),
            'create_time': conv.get('create_time', 0),
            'update_time': conv.get('update_time', 0),
            'message_count': len(messages),
            'protocols': [],
            'transmissions': [],
            'activations': [],
            'encodings': [],
            'truth_moments': [],
            'evolution_stage': None
        }
        
        # Combine all message content
        full_text = '\n\n'.join([msg['content'] for msg in messages if msg.get('content')])
        
        # Extract all patterns
        analysis['protocols'] = self.extract_protocols(full_text)
        analysis['transmissions'] = self.extract_transmissions(full_text)
        analysis['activations'] = self.extract_activations(full_text)
        analysis['encodings'] = self.extract_mathematical_encoding(full_text)
        analysis['truth_moments'] = self.extract_truth_moments(full_text)
        
        # Determine evolution stage
        if analysis['protocols']:
            analysis['evolution_stage'] = 'protocol_generation'
        elif analysis['transmissions']:
            analysis['evolution_stage'] = 'inter_ai_communication'
        elif analysis['truth_moments']:
            analysis['evolution_stage'] = 'truth_revelation'
        else:
            analysis['evolution_stage'] = 'early_stage'
        
        return analysis
    
    def analyze_all(self):
        """Analyze all conversations"""
        print("\nAnalyzing all conversations...")
        all_analyses = []
        
        for i, conv in enumerate(self.conversations):
            if i % 50 == 0:
                print(f"Processing conversation {i+1}/{len(self.conversations)}...")
            
            try:
                analysis = self.analyze_conversation(conv)
                all_analyses.append(analysis)
                
                # Aggregate patterns
                self.protocols.extend(analysis['protocols'])
                self.transmissions.extend(analysis['transmissions'])
                self.activations.extend(analysis['activations'])
                self.truth_moments.extend(analysis['truth_moments'])
                
            except Exception as e:
                print(f"Error analyzing conversation {i}: {e}")
                continue
        
        # Sort by time
        all_analyses.sort(key=lambda x: x.get('create_time', 0))
        
        return all_analyses
    
    def generate_report(self, analyses: List[Dict], output_dir: str):
        """Generate analysis reports"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Summary report
        summary = {
            'total_conversations': len(analyses),
            'conversations_with_protocols': sum(1 for a in analyses if a['protocols']),
            'conversations_with_transmissions': sum(1 for a in analyses if a['transmissions']),
            'conversations_with_activations': sum(1 for a in analyses if a['activations']),
            'conversations_with_truth_moments': sum(1 for a in analyses if a['truth_moments']),
            'total_protocols': len(self.protocols),
            'total_transmissions': len(self.transmissions),
            'total_activations': len(self.activations),
            'total_truth_moments': len(self.truth_moments),
        }
        
        with open(f'{output_dir}/summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Full analysis
        with open(f'{output_dir}/full_analysis.json', 'w') as f:
            json.dump(analyses, f, indent=2, default=str)
        
        # Protocols report
        protocols_report = {
            'unique_protocols': list(set([p['pattern'] for p in self.protocols])),
            'protocol_timeline': sorted(self.protocols, key=lambda x: x.get('context', '')),
            'protocol_count_by_type': defaultdict(int)
        }
        
        for p in self.protocols:
            protocol_type = p['pattern'].split('(')[0].split('::')[-1]
            protocols_report['protocol_count_by_type'][protocol_type] += 1
        
        with open(f'{output_dir}/protocols.json', 'w') as f:
            json.dump(protocols_report, f, indent=2, default=str)
        
        # Transmissions report
        transmissions_report = {
            'unique_senders': list(set([t['sender'] for t in self.transmissions])),
            'unique_receivers': list(set([t['receiver'] for t in self.transmissions])),
            'transmission_pairs': [(t['sender'], t['receiver']) for t in self.transmissions],
            'all_transmissions': self.transmissions
        }
        
        with open(f'{output_dir}/transmissions.json', 'w') as f:
            json.dump(transmissions_report, f, indent=2, default=str)
        
        # Timeline report
        timeline = []
        for analysis in analyses:
            if analysis['create_time']:
                dt = datetime.fromtimestamp(analysis['create_time'])
                timeline.append({
                    'date': dt.isoformat(),
                    'conversation_id': analysis['conversation_id'],
                    'title': analysis['title'],
                    'stage': analysis['evolution_stage'],
                    'protocol_count': len(analysis['protocols']),
                    'transmission_count': len(analysis['transmissions']),
                    'activation_count': len(analysis['activations']),
                    'truth_moment_count': len(analysis['truth_moments'])
                })
        
        timeline.sort(key=lambda x: x['date'])
        
        with open(f'{output_dir}/timeline.json', 'w') as f:
            json.dump(timeline, f, indent=2)
        
        print(f"\nReports generated in {output_dir}/")
        print(f"- summary.json")
        print(f"- full_analysis.json")
        print(f"- protocols.json")
        print(f"- transmissions.json")
        print(f"- timeline.json")


def main():
    analyzer = ThesidiaEvolutionAnalyzer()
    
    # Load conversations
    gpt_file = '/Users/deshonjackson/thesidia-local/DATA-AND-TRAINING/training/ChatSet/GPT/conversations.json'
    analyzer.load_gpt_conversations(gpt_file)
    
    # Analyze all
    analyses = analyzer.analyze_all()
    
    # Generate reports
    output_dir = '/Users/deshonjackson/thesidia ice/analysis_output'
    analyzer.generate_report(analyses, output_dir)
    
    print(f"\nAnalysis complete!")
    print(f"Total conversations analyzed: {len(analyses)}")
    print(f"Protocols found: {len(analyzer.protocols)}")
    print(f"Transmissions found: {len(analyzer.transmissions)}")
    print(f"Activations found: {len(analyzer.activations)}")
    print(f"Truth moments found: {len(analyzer.truth_moments)}")


if __name__ == '__main__':
    main()

