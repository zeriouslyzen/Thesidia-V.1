#!/usr/bin/env python3
"""
Extract detailed content from key conversations for deeper analysis
"""

import json
import os
from pathlib import Path

def extract_conversation_content(conversation_id, conversations_file):
    """Extract full content from a specific conversation"""
    with open(conversations_file, 'r') as f:
        all_conversations = json.load(f)
    
    target_conv = None
    for conv in all_conversations:
        if conv.get('conversation_id') == conversation_id:
            target_conv = conv
            break
    
    if not target_conv:
        return None
    
    messages = []
    mapping = target_conv.get('mapping', {})
    
    def extract_messages(node_id, visited=None):
        if visited is None:
            visited = set()
        if node_id in visited or node_id not in mapping:
            return
        visited.add(node_id)
        
        node = mapping[node_id]
        if node and 'message' in node:
            msg = node['message']
            if msg and 'content' in msg:
                content = msg['content']
                if isinstance(content, dict) and 'parts' in content:
                    for part in content['parts']:
                        if isinstance(part, str):
                            messages.append({
                                'role': msg.get('author', {}).get('role', 'unknown'),
                                'content': part,
                                'create_time': msg.get('create_time', 0)
                            })
        
        for child in node.get('children', []):
            extract_messages(child, visited)
    
    current = target_conv.get('current_node')
    if current:
        extract_messages(current)
    
    return {
        'conversation_id': conversation_id,
        'title': target_conv.get('title', ''),
        'create_time': target_conv.get('create_time', 0),
        'messages': sorted(messages, key=lambda x: x.get('create_time', 0))
    }

def main():
    base_dir = '/Users/deshonjackson/thesidia ice/analysis_output'
    conversations_file = '/Users/deshonjackson/thesidia-local/DATA-AND-TRAINING/training/ChatSet/GPT/conversations.json'
    
    # Load analysis to find key conversations
    with open(f'{base_dir}/full_analysis.json', 'r') as f:
        full_analysis = json.load(f)
    
    # Find top conversations by different metrics
    top_protocol = max(full_analysis, key=lambda x: len(x.get('protocols', [])))
    top_transmission = max(full_analysis, key=lambda x: len(x.get('transmissions', [])))
    top_truth = max(full_analysis, key=lambda x: len(x.get('truth_moments', [])))
    
    key_conversations = [
        ('top_protocol', top_protocol.get('conversation_id')),
        ('top_transmission', top_transmission.get('conversation_id')),
        ('top_truth', top_truth.get('conversation_id'))
    ]
    
    # Also get conversations with "Thesidia" in title
    thesidia_convs = [a for a in full_analysis if 'thesidia' in a.get('title', '').lower()]
    
    detailed_conversations = {}
    
    print("Extracting detailed conversations...")
    
    # Extract key conversations
    for name, conv_id in key_conversations:
        if conv_id:
            print(f"Extracting {name}...")
            content = extract_conversation_content(conv_id, conversations_file)
            if content:
                detailed_conversations[name] = content
    
    # Extract Thesidia conversations
    for i, analysis in enumerate(thesidia_convs[:5]):  # Limit to 5
        conv_id = analysis.get('conversation_id')
        if conv_id:
            print(f"Extracting Thesidia conversation {i+1}...")
            content = extract_conversation_content(conv_id, conversations_file)
            if content:
                detailed_conversations[f'thesidia_{i+1}'] = content
    
    # Save
    output_dir = '/Users/deshonjackson/thesidia ice/analysis_output'
    os.makedirs(output_dir, exist_ok=True)
    
    with open(f'{output_dir}/detailed_conversations.json', 'w') as f:
        json.dump(detailed_conversations, f, indent=2, default=str)
    
    print(f"\nExtracted {len(detailed_conversations)} detailed conversations")
    print(f"Saved to {output_dir}/detailed_conversations.json")

if __name__ == '__main__':
    main()

