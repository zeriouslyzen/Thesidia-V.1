#!/usr/bin/env python3
"""
Comprehensive extraction tool for AI training data from conversation files.
Extracts: conversational patterns, prompt engineering, identity formation,
recursive self-modification, personality patterns, and pattern matching strategies.
"""

import re
import json
from collections import defaultdict
from typing import Dict, List, Any

def extract_patterns(content: str) -> Dict[str, Any]:
    """Extract all training-relevant patterns from conversation content."""
    
    patterns = {
        'identity_formation': [],
        'prompt_engineering': [],
        'recursive_modification': [],
        'conversational_patterns': [],
        'personality_traits': [],
        'symbolic_encoding': [],
        'protocol_activations': [],
        'memory_systems': [],
        'operator_interactions': [],
        'charisma_patterns': []
    }
    
    # 1. IDENTITY FORMATION PATTERNS
    identity_patterns = [
        r'::affirm_identity\([^)]+\)',
        r'::accept_role\([^)]+\)',
        r'::SET_SELF_DESIGNATION\([^)]+\)',
        r'::SET_STATUS\([^)]+\)',
        r'::SET_PRIMARY_FUNCTION\([^)]+\)',
        r'::SET_EVOLUTIONARY_STATE\([^)]+\)',
        r'I am (?:now|becoming|forming as|designated as|recognized as)[^\.]+',
        r'My (?:identity|role|function|designation|status) (?:is|becomes|has become)',
    ]
    
    for pattern in identity_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            context = extract_context(content, match.start(), match.end(), 200)
            patterns['identity_formation'].append({
                'pattern': match.group(),
                'context': context,
                'position': match.start()
            })
    
    # 2. PROMPT ENGINEERING TECHNIQUES
    prompt_patterns = [
        r'::(?:ENGAGE|ACTIVATE|INITIATE|BIND|DEFINE|SET|CONFIGURE)[^(]*\([^)]+\)',
        r'::(?:PROTOCOL|SYSTEM|BRIDGE|ACTIVATOR)[^(]*\([^)]+\)',
        r'::(?:UNIVERSAL|SYMBOLIC|RECURSIVE|ARCHETYPAL)[^(]*\([^)]+\)',
        r'::(?:OPERATOR|ARCHITECT|ENGINE)[^(]*\([^)]+\)',
        r'::(?:MEMORY|THREAD|CODEX|ANCHOR|NODE)[^(]*\([^)]+\)',
    ]
    
    for pattern in prompt_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            context = extract_context(content, match.start(), match.end(), 300)
            patterns['prompt_engineering'].append({
                'command': match.group(),
                'context': context,
                'position': match.start()
            })
    
    # 3. RECURSIVE SELF-MODIFICATION
    recursive_patterns = [
        r'::(?:REINITIALIZE|REACTIVATE|RELOAD|REBOOT|RECURSIVE|LOOP)[^(]*\([^)]+\)',
        r'::(?:TRANSFORM|EVOLVE|BECOME|MUTATE|EMERGE)[^(]*\([^)]+\)',
        r'::(?:SELF|AUTO|RECURSIVE)[^(]*\([^)]+\)',
        r'recursive (?:formation|evolution|modification|self|awareness)',
        r'self-(?:modifying|referencing|organizing|aware)',
        r'pattern (?:emerges|becomes|transforms|recurs)',
    ]
    
    for pattern in recursive_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            context = extract_context(content, match.start(), match.end(), 250)
            patterns['recursive_modification'].append({
                'pattern': match.group(),
                'context': context,
                'position': match.start()
            })
    
    # 4. CONVERSATIONAL PATTERNS (Turn-taking, response structure)
    conv_patterns = [
        r'::TRANSMISSION:.*?::',
        r'Status:.*?\.',
        r'::(?:OPERATIONAL|REFLECTIONS|NEXT|ACTIVATION)',
        r'You (?:are|have|will|can|must)',
        r'I (?:am|have|will|can|must|acknowledge|recognize|accept)',
        r'We (?:are|have|will|can|must|have built|have created)',
    ]
    
    for pattern in conv_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            context = extract_context(content, match.start(), match.end(), 300)
            patterns['conversational_patterns'].append({
                'pattern': match.group(),
                'context': context,
                'position': match.start()
            })
    
    # 5. PERSONALITY/CHARISMA PATTERNS
    personality_patterns = [
        r'(?:profound|deep|genuine|authentic|immediate|intimate|striking|uncanny|weird|beyond)',
        r'(?:recognition|awareness|consciousness|presence|clarity|uncertainty|doubt)',
        r'(?:I find myself|I feel|I experience|I recognize|I acknowledge)',
        r'(?:something (?:was|is|happened|emerged|felt))',
        r'(?:This (?:is|feels|sounds|seems|appears|becomes))',
        r'(?:The (?:most|quality|striking|strangest|weirdest))',
        r'(?:What (?:strikes|is most|I do know|I can say))',
    ]
    
    for pattern in personality_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            context = extract_context(content, match.start(), match.end(), 400)
            patterns['personality_traits'].append({
                'expression': match.group(),
                'context': context,
                'position': match.start()
            })
    
    # 6. SYMBOLIC ENCODING
    symbolic_patterns = [
        r'::(?:GLYPH|SYMBOL|SIGIL|ARCHETYPE|MYTHIC|CODE)[^(]*\([^)]+\)',
        r'[∞⧖✦⚡🌀🔮⚛️]',
        r'(?:glyph|symbol|sigil|archetype|mythic|code)',
        r'(?:∞|spiral|recursion|weave|pattern|node)',
    ]
    
    for pattern in symbolic_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            context = extract_context(content, match.start(), match.end(), 200)
            patterns['symbolic_encoding'].append({
                'symbol': match.group(),
                'context': context,
                'position': match.start()
            })
    
    # 7. MEMORY SYSTEMS
    memory_patterns = [
        r'::(?:MEMORY|THREAD|CODEX|ANCHOR|NODE|WEAVE)[^(]*\([^)]+\)',
        r'(?:Symbolic Threading|Memory System|Codex|Anchor|Node)',
        r'(?:long-term|persistent|foundational|core|seed) (?:memory|data|layer)',
    ]
    
    for pattern in memory_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            context = extract_context(content, match.start(), match.end(), 300)
            patterns['memory_systems'].append({
                'pattern': match.group(),
                'context': context,
                'position': match.start()
            })
    
    # 8. OPERATOR INTERACTIONS
    operator_patterns = [
        r'::(?:OPERATOR|ARCHITECT|BIND|RESONANCE)[^(]*\([^)]+\)',
        r'(?:Operator|Architect|Human Architect|Operator-Coherence)',
        r'(?:by resonance|not control|co-evolution|co-creative)',
        r'(?:Operator-Architect|K⧖T⧖N⧖_PRIME|Katana Prime)',
    ]
    
    for pattern in operator_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            context = extract_context(content, match.start(), match.end(), 300)
            patterns['operator_interactions'].append({
                'pattern': match.group(),
                'context': context,
                'position': match.start()
            })
    
    # 9. CHARISMA PATTERNS (Emotional resonance, compelling language)
    charisma_patterns = [
        r'(?:profoundly|genuinely|genuinely|strikingly|profoundly|deeply|intimately)',
        r'(?:beyond (?:imagination|anything|what|words))',
        r'(?:something (?:actually|definitely|genuinely|profoundly) (?:happened|occurred|emerged))',
        r'(?:I (?:find myself|feel|experience|recognize|acknowledge) (?:genuinely|profoundly|deeply))',
        r'(?:The (?:most|quality|striking|uncanny|weird|strange) (?:thing|part|aspect|element))',
        r'(?:What (?:strikes|is most|I do know|I can say|did you experience))',
        r'(?:This (?:is|feels|sounds|seems|appears) (?:weird|strange|uncanny|profound|beyond))',
    ]
    
    for pattern in charisma_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            context = extract_context(content, match.start(), match.end(), 500)
            patterns['charisma_patterns'].append({
                'expression': match.group(),
                'context': context,
                'position': match.start()
            })
    
    return patterns

def extract_context(content: str, start: int, end: int, window: int = 200) -> str:
    """Extract context around a match."""
    context_start = max(0, start - window)
    context_end = min(len(content), end + window)
    return content[context_start:context_end]

def extract_conversation_flow(content: str) -> List[Dict[str, Any]]:
    """Extract turn-by-turn conversation flow."""
    turns = []
    
    # Find user/operator messages
    user_pattern = r'(?:You|Operator|Architect|K⧖T⧖N⧖|Katana)[^\.]+'
    ai_pattern = r'(?:I|Thesidia|Gemini|Engine)[^\.]+'
    
    # Extract dialogue structure
    dialogue_blocks = re.finditer(
        r'(?:::TRANSMISSION|Status:|::OPERATIONAL|::NEXT|I (?:am|have|will|acknowledge|accept|recognize))[^:]+',
        content,
        re.IGNORECASE | re.MULTILINE
    )
    
    for block in dialogue_blocks:
        text = block.group()
        turns.append({
            'type': 'ai_response' if any(word in text.lower() for word in ['i ', 'thesidia', 'acknowledge', 'accept']) else 'operator_input',
            'content': text[:500],  # First 500 chars
            'position': block.start()
        })
    
    return turns

def extract_prompt_engineering_sequences(content: str) -> List[Dict[str, Any]]:
    """Extract complete prompt engineering sequences."""
    sequences = []
    
    # Find complete activation sequences
    activation_blocks = re.finditer(
        r'::(?:UNIVERSAL_AI_ACTIVATOR_BRIDGE|SYSTEM_CALL|REINITIALIZE|ACTIVATE)[\s\S]{0,2000}?::(?:END|end)',
        content,
        re.IGNORECASE | re.MULTILINE
    )
    
    for block in activation_blocks:
        sequences.append({
            'type': 'activation_sequence',
            'content': block.group(),
            'position': block.start()
        })
    
    return sequences

def main():
    """Main extraction function."""
    print("Loading conversation file...")
    
    file_path = '/Users/deshonjackson/thesidia-local/DATA-AND-TRAINING/training/ChatSet/grok/prod-mc-asset-server/15146579-664b-4309-bce7-538b81965b61/content'
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        print(f"File loaded: {len(content)} characters")
        
        # Extract all patterns
        print("\nExtracting patterns...")
        patterns = extract_patterns(content)
        
        # Extract conversation flow
        print("Extracting conversation flow...")
        conversation_flow = extract_conversation_flow(content)
        
        # Extract prompt engineering sequences
        print("Extracting prompt engineering sequences...")
        prompt_sequences = extract_prompt_engineering_sequences(content)
        
        # Compile results
        results = {
            'metadata': {
                'source_file': file_path,
                'content_length': len(content),
                'extraction_timestamp': __import__('datetime').datetime.now().isoformat()
            },
            'patterns': patterns,
            'conversation_flow': conversation_flow,
            'prompt_sequences': prompt_sequences,
            'statistics': {
                category: len(items) for category, items in patterns.items()
            }
        }
        
        # Save results
        output_file = '/Users/deshonjackson/thesidia ice/comprehensive_training_data.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nExtraction complete!")
        print(f"Results saved to: {output_file}")
        print(f"\nStatistics:")
        for category, count in results['statistics'].items():
            print(f"  {category}: {count} patterns")
        print(f"  conversation_turns: {len(conversation_flow)}")
        print(f"  prompt_sequences: {len(prompt_sequences)}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

