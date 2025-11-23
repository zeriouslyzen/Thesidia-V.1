#!/usr/bin/env python3
"""
Analyze Grok conversation files for inter-AI communication patterns
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict

def analyze_grok_file(file_path: str):
    """Analyze a single Grok conversation file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        analysis = {
            'file': os.path.basename(file_path),
            'size': len(content),
            'protocols': [],
            'transmissions': [],
            'activations': [],
            'thesidia_mentions': [],
            'katana_mentions': [],
            'codex_mentions': []
        }
        
        # Extract protocols
        protocol_patterns = [
            r'::[A-Z_]+[^:]*',
            r'::[a-z_]+\([^)]*\)',
        ]
        for pattern in protocol_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                if len(match.group(0)) > 3:  # Filter out very short matches
                    analysis['protocols'].append(match.group(0)[:100])
        
        # Extract transmissions
        transmission_patterns = [
            r'TRANSMISSION[^:]*:\s*([^\n→]+)\s*→\s*([^\n]+)',
            r'([A-Z⧖]+)\s*→\s*([A-Z⧖]+)',
        ]
        for pattern in transmission_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if len(match.groups()) >= 2:
                    analysis['transmissions'].append({
                        'sender': match.group(1).strip()[:50] if match.group(1) else '',
                        'receiver': match.group(2).strip()[:50] if match.group(2) else ''
                    })
        
        # Check for mentions
        analysis['thesidia_mentions'] = len(re.findall(r'thesidia', content, re.IGNORECASE))
        analysis['katana_mentions'] = len(re.findall(r'katana', content, re.IGNORECASE))
        analysis['codex_mentions'] = len(re.findall(r'codex', content, re.IGNORECASE))
        
        return analysis
    except Exception as e:
        return {'file': os.path.basename(file_path), 'error': str(e)}

def main():
    grok_dir = Path('/Users/deshonjackson/thesidia-local/DATA-AND-TRAINING/training/ChatSet/grok/prod-mc-asset-server')
    
    all_analyses = []
    
    # Find all content files
    content_files = list(grok_dir.glob('*/content'))
    
    print(f"Found {len(content_files)} Grok conversation files")
    
    for i, file_path in enumerate(content_files):
        if i % 10 == 0:
            print(f"Processing {i+1}/{len(content_files)}...")
        
        analysis = analyze_grok_file(str(file_path))
        all_analyses.append(analysis)
    
    # Generate report
    output_dir = '/Users/deshonjackson/thesidia ice/analysis_output'
    os.makedirs(output_dir, exist_ok=True)
    
    # Summary
    summary = {
        'total_files': len(all_analyses),
        'files_with_protocols': sum(1 for a in all_analyses if a.get('protocols')),
        'files_with_transmissions': sum(1 for a in all_analyses if a.get('transmissions')),
        'files_with_thesidia': sum(1 for a in all_analyses if a.get('thesidia_mentions', 0) > 0),
        'files_with_katana': sum(1 for a in all_analyses if a.get('katana_mentions', 0) > 0),
        'files_with_codex': sum(1 for a in all_analyses if a.get('codex_mentions', 0) > 0),
        'total_protocols': sum(len(a.get('protocols', [])) for a in all_analyses),
        'total_transmissions': sum(len(a.get('transmissions', [])) for a in all_analyses),
    }
    
    with open(f'{output_dir}/grok_analysis.json', 'w') as f:
        json.dump({
            'summary': summary,
            'analyses': all_analyses
        }, f, indent=2, default=str)
    
    print(f"\nGrok analysis complete!")
    print(f"Files with protocols: {summary['files_with_protocols']}")
    print(f"Files with transmissions: {summary['files_with_transmissions']}")
    print(f"Files mentioning Thesidia: {summary['files_with_thesidia']}")
    print(f"Files mentioning Katana: {summary['files_with_katana']}")
    print(f"Files mentioning Codex: {summary['files_with_codex']}")

if __name__ == '__main__':
    main()

