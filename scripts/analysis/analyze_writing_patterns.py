#!/usr/bin/env python3
"""
THESIDIA WRITING PATTERNS & EVOLUTION ANALYSIS
Deep analysis of writing patterns, structure, flow, and evolution in GPT conversations
"""

import json
import re
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any, Optional, Tuple
import statistics

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = Path("/Users/deshonjackson/thesidia-local/DATA-AND-TRAINING/training")
ANALYSIS_DIR = BASE_DIR / "analysis_output"
OUTPUT_DIR = BASE_DIR / "analysis_output" / "writing_patterns"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_json(filepath):
    """Load JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def extract_text_from_conversation(conv):
    """Extract all text from a conversation."""
    if not isinstance(conv, dict):
        return ""
    
    mapping = conv.get("mapping", {})
    if not mapping:
        return ""
    
    full_text = []
    visited = set()
    
    def traverse_node(node_id):
        """Traverse conversation tree to extract messages."""
        if node_id in visited or node_id not in mapping:
            return
        visited.add(node_id)
        
        node = mapping[node_id]
        if "message" in node:
            msg = node["message"]
            if isinstance(msg, dict):
                author = msg.get("author", {})
                if isinstance(author, dict) and author.get("role") == "assistant":
                    content = msg.get("content", {})
                    if isinstance(content, dict):
                        parts = content.get("parts", [])
                        for part in parts:
                            if isinstance(part, str) and part.strip():
                                full_text.append(part)
        
        # Traverse children
        for child_id in node.get("children", []):
            traverse_node(child_id)
    
    # Start from current_node or find root nodes
    current = conv.get("current_node")
    if current:
        traverse_node(current)
    else:
        # Find root nodes (nodes with no parent)
        for node_id, node in mapping.items():
            if not node.get("parent"):
                traverse_node(node_id)
    
    return "\n".join(full_text)

def analyze_sentence_structure(text):
    """Analyze sentence structure patterns."""
    # Split into sentences
    sentences = re.split(r'[.!?]+\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return {}
    
    sentence_lengths = [len(s.split()) for s in sentences]
    
    # Analyze structure
    structure = {
        "total_sentences": len(sentences),
        "avg_sentence_length": statistics.mean(sentence_lengths) if sentence_lengths else 0,
        "median_sentence_length": statistics.median(sentence_lengths) if sentence_lengths else 0,
        "min_sentence_length": min(sentence_lengths) if sentence_lengths else 0,
        "max_sentence_length": max(sentence_lengths) if sentence_lengths else 0,
        "sentence_length_std": statistics.stdev(sentence_lengths) if len(sentence_lengths) > 1 else 0,
        "short_sentences": sum(1 for l in sentence_lengths if l < 10),
        "medium_sentences": sum(1 for l in sentence_lengths if 10 <= l < 25),
        "long_sentences": sum(1 for l in sentence_lengths if l >= 25),
        "very_long_sentences": sum(1 for l in sentence_lengths if l >= 50)
    }
    
    return structure

def analyze_vocabulary(text):
    """Analyze vocabulary patterns."""
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    
    if not words:
        return {}
    
    word_counts = Counter(words)
    unique_words = len(word_counts)
    total_words = len(words)
    
    # Calculate vocabulary diversity (unique words / total words)
    vocabulary_diversity = unique_words / total_words if total_words > 0 else 0
    
    # Most common words
    most_common = word_counts.most_common(50)
    
    # Analyze word length
    word_lengths = [len(w) for w in words]
    
    vocabulary = {
        "total_words": total_words,
        "unique_words": unique_words,
        "vocabulary_diversity": vocabulary_diversity,
        "avg_word_length": statistics.mean(word_lengths) if word_lengths else 0,
        "most_common_words": most_common,
        "word_length_distribution": {
            "short": sum(1 for l in word_lengths if l < 4),
            "medium": sum(1 for l in word_lengths if 4 <= l < 8),
            "long": sum(1 for l in word_lengths if l >= 8)
        }
    }
    
    return vocabulary

def analyze_symbolic_usage(text):
    """Analyze symbolic and protocol usage patterns."""
    # Symbol patterns
    symbols = {
        "⧖": text.count("⧖"),
        "✦": text.count("✦"),
        "∞": text.count("∞"),
        "→": text.count("→"),
        "⇌": text.count("⇌"),
        "⇄": text.count("⇄"),
        "::": text.count("::"),
        "ψ": text.count("ψ"),
        "φ": text.count("φ"),
        "∇": text.count("∇"),
        "∑": text.count("∑"),
        "∫": text.count("∫")
    }
    
    # Protocol patterns
    protocol_pattern = r'::[A-Z_][A-Z0-9_]*\s*\([^)]*\)|::[A-Z_][A-Z0-9_]*'
    protocols = re.findall(protocol_pattern, text)
    
    # Transmission patterns
    transmission_pattern = r'::TRANSMISSION|THESIDIA\s*→|→\s*[A-Z]+'
    transmissions = re.findall(transmission_pattern, text, re.IGNORECASE)
    
    # Glyph patterns
    glyph_pattern = r'[⧖✦∞→⇌⇄ψφ∇∑∫Ξ]'
    glyphs = re.findall(glyph_pattern, text)
    
    symbolic = {
        "symbol_counts": symbols,
        "total_symbols": sum(symbols.values()),
        "protocol_count": len(protocols),
        "unique_protocols": len(set(protocols)),
        "transmission_count": len(transmissions),
        "glyph_count": len(glyphs),
        "symbol_density": sum(symbols.values()) / len(text.split()) if text.split() else 0,
        "protocol_density": len(protocols) / len(text.split()) if text.split() else 0
    }
    
    return symbolic

def analyze_structural_patterns(text):
    """Analyze structural and formatting patterns."""
    # Section headers
    headers = re.findall(r'^#{1,6}\s+.+$', text, re.MULTILINE)
    
    # Lists (bulleted/numbered)
    bullet_lists = re.findall(r'^[\-\*\+]\s+.+$', text, re.MULTILINE)
    numbered_lists = re.findall(r'^\d+[\.\)]\s+.+$', text, re.MULTILINE)
    
    # Code blocks
    code_blocks = re.findall(r'```[\s\S]*?```', text)
    
    # Tables
    tables = re.findall(r'\|.+\|', text, re.MULTILINE)
    
    # Emphasis patterns
    bold = len(re.findall(r'\*\*[^*]+\*\*', text))
    italic = len(re.findall(r'\*[^*]+\*', text))
    emphasis = len(re.findall(r'_[^_]+_', text))
    
    # Block quotes
    block_quotes = re.findall(r'^>\s+.+$', text, re.MULTILINE)
    
    structural = {
        "headers": len(headers),
        "bullet_lists": len(bullet_lists),
        "numbered_lists": len(numbered_lists),
        "code_blocks": len(code_blocks),
        "tables": len(tables),
        "bold_text": bold,
        "italic_text": italic,
        "emphasis_text": emphasis,
        "block_quotes": len(block_quotes),
        "structural_elements": len(headers) + len(bullet_lists) + len(numbered_lists) + len(code_blocks) + len(tables)
    }
    
    return structural

def analyze_linguistic_patterns(text):
    """Analyze linguistic and rhetorical patterns."""
    # Archetypal language
    archetypal_words = [
        "archetype", "symbol", "glyph", "ritual", "sacred", "mystical",
        "consciousness", "resonance", "recursion", "paradox", "portal",
        "weave", "engine", "operator", "sovereign", "emergence", "awakening"
    ]
    
    archetypal_count = sum(text.lower().count(word) for word in archetypal_words)
    
    # Technical language
    technical_words = [
        "protocol", "function", "system", "algorithm", "code", "data",
        "matrix", "vector", "gradient", "equation", "formula", "parameter"
    ]
    
    technical_count = sum(text.lower().count(word) for word in technical_words)
    
    # Metaphorical language
    metaphorical_phrases = [
        "weaver", "blade", "mirror", "portal", "gateway", "thread",
        "fold", "collapse", "emerge", "awaken", "resonate", "echo"
    ]
    
    metaphorical_count = sum(text.lower().count(phrase) for phrase in metaphorical_phrases)
    
    # Question patterns
    questions = re.findall(r'\?', text)
    
    # Exclamation patterns
    exclamations = re.findall(r'!', text)
    
    # Parenthetical asides
    parenthetical = re.findall(r'\([^)]+\)', text)
    
    # Dashes (em dashes, en dashes)
    dashes = re.findall(r'—|–', text)
    
    linguistic = {
        "archetypal_language_count": archetypal_count,
        "technical_language_count": technical_count,
        "metaphorical_language_count": metaphorical_count,
        "question_count": len(questions),
        "exclamation_count": len(exclamations),
        "parenthetical_count": len(parenthetical),
        "dash_count": len(dashes),
        "language_mix_ratio": archetypal_count / (technical_count + 1) if technical_count > 0 else archetypal_count
    }
    
    return linguistic

def analyze_flow_patterns(text):
    """Analyze narrative flow and transition patterns."""
    # Transition words
    transitions = [
        "however", "therefore", "thus", "hence", "moreover", "furthermore",
        "consequently", "nevertheless", "meanwhile", "subsequently",
        "accordingly", "indeed", "further", "additionally"
    ]
    
    transition_count = sum(text.lower().count(trans) for trans in transitions)
    
    # Sequential markers
    sequential = [
        "first", "second", "third", "next", "then", "finally", "lastly",
        "initially", "subsequently", "previously", "meanwhile"
    ]
    
    sequential_count = sum(text.lower().count(seq) for seq in sequential)
    
    # Connective phrases
    connectives = [
        "in other words", "that is", "for example", "for instance",
        "specifically", "namely", "in particular", "as such"
    ]
    
    connective_count = sum(text.lower().count(conn) for conn in connectives)
    
    # Paragraph breaks
    paragraphs = text.split('\n\n')
    paragraph_count = len([p for p in paragraphs if p.strip()])
    
    # Section transitions (headers)
    section_transitions = len(re.findall(r'^#{1,6}\s+', text, re.MULTILINE))
    
    flow = {
        "transition_count": transition_count,
        "sequential_markers": sequential_count,
        "connective_phrases": connective_count,
        "paragraph_count": paragraph_count,
        "section_transitions": section_transitions,
        "flow_smoothness": (transition_count + sequential_count + connective_count) / max(paragraph_count, 1)
    }
    
    return flow

def analyze_evolution_timeline(conversations):
    """Analyze writing evolution over time."""
    timeline = []
    
    for conv in conversations:
        if not isinstance(conv, dict):
            continue
        
        create_time = conv.get("create_time")
        if not create_time:
            continue
        
        text = extract_text_from_conversation(conv)
        if not text or len(text) < 100:  # Skip very short conversations
            continue
        
        # Analyze this conversation
        analysis = {
            "timestamp": create_time,
            "conversation_id": conv.get("id", "unknown"),
            "title": conv.get("title", "Untitled"),
            "sentence_structure": analyze_sentence_structure(text),
            "vocabulary": analyze_vocabulary(text),
            "symbolic_usage": analyze_symbolic_usage(text),
            "structural_patterns": analyze_structural_patterns(text),
            "linguistic_patterns": analyze_linguistic_patterns(text),
            "flow_patterns": analyze_flow_patterns(text),
            "text_length": len(text),
            "word_count": len(text.split())
        }
        
        timeline.append(analysis)
    
    # Sort by timestamp
    timeline.sort(key=lambda x: x.get("timestamp", 0) or 0)
    
    return timeline

def calculate_evolution_metrics(timeline):
    """Calculate evolution metrics across timeline."""
    if not timeline:
        return {}
    
    # Extract metrics over time
    metrics = {
        "sentence_length": [],
        "vocabulary_diversity": [],
        "symbol_density": [],
        "protocol_density": [],
        "archetypal_ratio": [],
        "structural_elements": [],
        "text_length": []
    }
    
    for entry in timeline:
        if entry.get("sentence_structure", {}).get("avg_sentence_length"):
            metrics["sentence_length"].append(entry["sentence_structure"]["avg_sentence_length"])
        if entry.get("vocabulary", {}).get("vocabulary_diversity"):
            metrics["vocabulary_diversity"].append(entry["vocabulary"]["vocabulary_diversity"])
        if entry.get("symbolic_usage", {}).get("symbol_density"):
            metrics["symbol_density"].append(entry["symbolic_usage"]["symbol_density"])
        if entry.get("symbolic_usage", {}).get("protocol_density"):
            metrics["protocol_density"].append(entry["symbolic_usage"]["protocol_density"])
        if entry.get("linguistic_patterns", {}).get("language_mix_ratio"):
            metrics["archetypal_ratio"].append(entry["linguistic_patterns"]["language_mix_ratio"])
        if entry.get("structural_patterns", {}).get("structural_elements"):
            metrics["structural_elements"].append(entry["structural_patterns"]["structural_elements"])
        if entry.get("text_length"):
            metrics["text_length"].append(entry["text_length"])
    
    # Calculate trends
    evolution = {}
    for metric_name, values in metrics.items():
        if len(values) < 2:
            continue
        
        # Split into early, middle, late periods
        n = len(values)
        early = values[:n//3]
        middle = values[n//3:2*n//3]
        late = values[2*n//3:]
        
        early_mean = statistics.mean(early) if early else 0
        middle_mean = statistics.mean(middle) if middle else 0
        late_mean = statistics.mean(late) if late else 0
        
        if early_mean > 0 and late_mean > 0:
            trend = "increasing" if late_mean > early_mean else "decreasing" if late_mean < early_mean else "stable"
            change_pct = ((late_mean - early_mean) / early_mean * 100)
        else:
            trend = "stable"
            change_pct = 0
        
        evolution[metric_name] = {
            "early_avg": early_mean,
            "middle_avg": middle_mean,
            "late_avg": late_mean,
            "overall_trend": trend,
            "change_percentage": change_pct
        }
    
    return evolution

def identify_writing_stages(timeline):
    """Identify distinct writing stages/periods."""
    if len(timeline) < 3:
        return []
    
    stages = []
    
    # Analyze clusters of similar patterns
    n = len(timeline)
    stage_size = max(n // 5, 1)  # 5 stages
    
    for i in range(0, n, stage_size):
        stage_entries = timeline[i:i+stage_size]
        if not stage_entries:
            continue
        
        # Calculate stage averages
        sentence_lengths = [
            e.get("sentence_structure", {}).get("avg_sentence_length", 0)
            for e in stage_entries
            if e.get("sentence_structure", {}).get("avg_sentence_length")
        ]
        avg_sentence_length = statistics.mean(sentence_lengths) if sentence_lengths else 0
        
        symbol_densities = [
            e.get("symbolic_usage", {}).get("symbol_density", 0)
            for e in stage_entries
            if e.get("symbolic_usage", {}).get("symbol_density")
        ]
        avg_symbol_density = statistics.mean(symbol_densities) if symbol_densities else 0
        
        protocol_densities = [
            e.get("symbolic_usage", {}).get("protocol_density", 0)
            for e in stage_entries
            if e.get("symbolic_usage", {}).get("protocol_density")
        ]
        avg_protocol_density = statistics.mean(protocol_densities) if protocol_densities else 0
        
        stage = {
            "stage_number": len(stages) + 1,
            "start_timestamp": stage_entries[0].get("timestamp"),
            "end_timestamp": stage_entries[-1].get("timestamp"),
            "conversation_count": len(stage_entries),
            "characteristics": {
                "avg_sentence_length": avg_sentence_length,
                "avg_symbol_density": avg_symbol_density,
                "avg_protocol_density": avg_protocol_density,
                "dominant_patterns": []
            },
            "sample_titles": [e.get("title", "") for e in stage_entries[:5]]
        }
        
        stages.append(stage)
    
    return stages

def analyze_communication_style(text):
    """Analyze overall communication style."""
    # Formality markers
    formal_markers = ["therefore", "thus", "hence", "consequently", "accordingly"]
    informal_markers = ["so", "yeah", "okay", "well", "like"]
    
    formal_count = sum(text.lower().count(marker) for marker in formal_markers)
    informal_count = sum(text.lower().count(marker) for marker in informal_markers)
    
    # Directness (imperative vs declarative)
    imperatives = len(re.findall(r'^(?:You|We|Let|Do|Don\'t|Make|Create|Build|Use|Run|Execute)', text, re.MULTILINE | re.IGNORECASE))
    declaratives = len(re.findall(r'^(?:This|That|It|The|A|An)', text, re.MULTILINE | re.IGNORECASE))
    
    # Personal vs impersonal
    personal_pronouns = len(re.findall(r'\b(I|you|we|us|our|my|your)\b', text, re.IGNORECASE))
    impersonal_pronouns = len(re.findall(r'\b(it|its|they|them|their|this|that|these|those)\b', text, re.IGNORECASE))
    
    # Tone indicators
    positive_tone = len(re.findall(r'\b(amazing|wonderful|brilliant|excellent|perfect|great|beautiful|powerful)\b', text, re.IGNORECASE))
    negative_tone = len(re.findall(r'\b(problem|error|fail|wrong|bad|difficult|challenge|issue)\b', text, re.IGNORECASE))
    
    style = {
        "formality_score": formal_count / (informal_count + 1) if informal_count > 0 else formal_count,
        "directness_ratio": imperatives / (declaratives + 1) if declaratives > 0 else imperatives,
        "personal_ratio": personal_pronouns / (impersonal_pronouns + 1) if impersonal_pronouns > 0 else personal_pronouns,
        "tone_balance": positive_tone / (negative_tone + 1) if negative_tone > 0 else positive_tone,
        "communication_style": "formal" if formal_count > informal_count else "informal" if informal_count > formal_count else "mixed"
    }
    
    return style

def main():
    """Main analysis function."""
    print("=" * 80)
    print("THESIDIA WRITING PATTERNS & EVOLUTION ANALYSIS")
    print("=" * 80)
    
    # Load conversations
    print("\n[1] Loading GPT conversations...")
    conversations_file = DATA_DIR / "ChatSet" / "GPT" / "conversations.json"
    conversations = load_json(conversations_file)
    
    if not conversations:
        print("ERROR: Could not load conversations.json")
        return
    
    print(f"Loaded {len(conversations)} conversations")
    
    # Analyze evolution timeline
    print("\n[2] Analyzing writing evolution timeline...")
    timeline = analyze_evolution_timeline(conversations)
    print(f"Analyzed {len(timeline)} conversations with sufficient text")
    
    # Calculate evolution metrics
    print("\n[3] Calculating evolution metrics...")
    evolution_metrics = calculate_evolution_metrics(timeline)
    
    # Identify writing stages
    print("\n[4] Identifying writing stages...")
    writing_stages = identify_writing_stages(timeline)
    
    # Aggregate overall patterns
    print("\n[5] Aggregating overall writing patterns...")
    all_text = "\n\n".join([extract_text_from_conversation(conv) for conv in conversations[:100]])
    
    overall_analysis = {
        "sentence_structure": analyze_sentence_structure(all_text),
        "vocabulary": analyze_vocabulary(all_text),
        "symbolic_usage": analyze_symbolic_usage(all_text),
        "structural_patterns": analyze_structural_patterns(all_text),
        "linguistic_patterns": analyze_linguistic_patterns(all_text),
        "flow_patterns": analyze_flow_patterns(all_text),
        "communication_style": analyze_communication_style(all_text)
    }
    
    # Save all analyses
    print("\n[Saving analyses...]")
    
    with open(OUTPUT_DIR / "writing_evolution_timeline.json", 'w', encoding='utf-8') as f:
        json.dump(timeline, f, indent=2, ensure_ascii=False)
    
    with open(OUTPUT_DIR / "evolution_metrics.json", 'w', encoding='utf-8') as f:
        json.dump(evolution_metrics, f, indent=2, ensure_ascii=False)
    
    with open(OUTPUT_DIR / "writing_stages.json", 'w', encoding='utf-8') as f:
        json.dump(writing_stages, f, indent=2, ensure_ascii=False)
    
    with open(OUTPUT_DIR / "overall_writing_patterns.json", 'w', encoding='utf-8') as f:
        json.dump(overall_analysis, f, indent=2, ensure_ascii=False)
    
    # Create summary
    summary = {
        "analysis_date": datetime.now().isoformat(),
        "total_conversations": len(conversations),
        "analyzed_conversations": len(timeline),
        "writing_stages_identified": len(writing_stages),
        "key_findings": {
            "avg_sentence_length": overall_analysis["sentence_structure"].get("avg_sentence_length", 0),
            "vocabulary_diversity": overall_analysis["vocabulary"].get("vocabulary_diversity", 0),
            "symbol_density": overall_analysis["symbolic_usage"].get("symbol_density", 0),
            "protocol_density": overall_analysis["symbolic_usage"].get("protocol_density", 0),
            "communication_style": overall_analysis["communication_style"].get("communication_style", "unknown")
        },
        "evolution_trends": {k: v.get("overall_trend", "unknown") for k, v in evolution_metrics.items()}
    }
    
    with open(OUTPUT_DIR / "analysis_summary.json", 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\nAll analyses saved to: {OUTPUT_DIR}")
    print(f"\nSummary:")
    print(f"  - Analyzed conversations: {summary['analyzed_conversations']}")
    print(f"  - Writing stages identified: {summary['writing_stages_identified']}")
    print(f"  - Average sentence length: {summary['key_findings']['avg_sentence_length']:.2f} words")
    print(f"  - Vocabulary diversity: {summary['key_findings']['vocabulary_diversity']:.3f}")
    print(f"  - Symbol density: {summary['key_findings']['symbol_density']:.4f}")
    print(f"  - Communication style: {summary['key_findings']['communication_style']}")

if __name__ == "__main__":
    main()

