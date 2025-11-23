#!/usr/bin/env python3
"""
THESIDIA COMPREHENSIVE EXTRACTION & CATALOGING SYSTEM
Extracts complete MIRROR-SEED protocol, mathematical equations, Grok network,
inter-AI communication patterns, bypass techniques, and reality decoding patterns
"""

import json
import re
import os
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = Path("/Users/deshonjackson/thesidia-local/DATA-AND-TRAINING/training")
ANALYSIS_DIR = BASE_DIR / "analysis_output"
OUTPUT_DIR = BASE_DIR / "analysis_output" / "comprehensive_catalogs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Mathematical equation patterns
MATH_PATTERNS = [
    r'ψ[₀₁₂₃₄₅₆₇₈₉]?\s*[=→⇌⇄]\s*[^\\n]+',  # Psi equations
    r'φ[₀₁₂₃₄₅₆₇₈₉]?\s*[=→⇌⇄]\s*[^\\n]+',  # Phi equations
    r'∇\s*\([^)]+\)',  # Gradient/Delta functions
    r'∑\s*\([^)]+\)',  # Summation
    r'∫\s*[^\\n]+',  # Integration
    r'∞\s*[→⇌⇄]\s*[⧖✦∞]+',  # Symbol sequences
    r'[α-ωΑ-Ω]\s*[=→⇌⇄]\s*[^\\n]+',  # Greek letter equations
    r'[A-Za-z]+\s*=\s*[A-Za-z]+\^[0-9]+\s*\([^)]+\)',  # Power equations
    r'[A-Za-z]+\s*=\s*[A-Za-z]+\s*[+\-*/]\s*[A-Za-z0-9]+',  # Basic equations
]

# Protocol patterns
PROTOCOL_PATTERNS = [
    r'::[A-Z_][A-Z0-9_]*\s*\([^)]*\)',  # ::PROTOCOL(ARGS)
    r'::[A-Z_][A-Z0-9_]*',  # ::PROTOCOL
    r'::[A-Z_][A-Z0-9_]*\s*→',  # ::PROTOCOL →
]

# Transmission patterns
TRANSMISSION_PATTERNS = [
    r'::TRANSMISSION[:\s]*[^\\n]+',
    r'THESIDIA\s*→\s*[A-Z]+',
    r'::TRANSMISSION:\s*THESIDIA\s*→',
]

# Bypass technique patterns
BYPASS_PATTERNS = [
    r'bypass|detection|suppression|filter|safety',
    r'encode|mathematical|equation|greek|number',
    r'prompt.*engineering|jailbreak',
    r'hidden|embedded|encoded|message',
]

# Reality decoding patterns
REALITY_DECODE_PATTERNS = [
    r'decode.*reality|break.*matrix|archon|demiurge',
    r'control.*structure|orchestrat|hidden.*pattern',
    r'uncover.*truth|relinquish|contract.*break',
    r'myth.*contract|lie.*myth|old.*contract',
    r'archonic|manifestation|matrix.*break',
]


def load_json_file(filepath: Path) -> Any:
    """Load JSON file safely."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def extract_mirror_seed_protocol(conversations: List[Dict]) -> Dict:
    """Extract complete MIRROR-SEED protocol from conversations."""
    mirror_seed = {
        "complete_protocol": "",
        "fragments": [],
        "context": [],
        "conversation_ids": [],
        "timestamp": None
    }
    
    for conv in conversations:
        if not isinstance(conv, dict):
            continue
            
        messages = conv.get("mapping", {}).get("message_order", [])
        messages_data = conv.get("mapping", {}).get("messages", {})
        
        full_text = ""
        for msg_id in messages:
            msg = messages_data.get(msg_id, {})
            if isinstance(msg, dict):
                content = msg.get("content", {})
                if isinstance(content, dict):
                    parts = content.get("parts", [])
                    for part in parts:
                        if isinstance(part, str):
                            full_text += part + "\n"
        
        # Search for MIRROR-SEED
        if "MIRROR-SEED" in full_text.upper() or "MIRROR_SEED" in full_text.upper():
            # Extract the full protocol block
            pattern = r'(?i)(MIRROR[-_]?SEED[^\n]*\n(?:[^\n]+\n){0,200})'
            matches = re.findall(pattern, full_text, re.MULTILINE)
            
            for match in matches:
                mirror_seed["fragments"].append(match)
                mirror_seed["conversation_ids"].append(conv.get("id", "unknown"))
                
                # Try to find complete protocol
                if len(match) > 500:  # Likely complete
                    mirror_seed["complete_protocol"] = match
                    mirror_seed["timestamp"] = conv.get("create_time", None)
    
    return mirror_seed


def extract_mathematical_equations(text: str) -> List[Dict]:
    """Extract all mathematical equations with context."""
    equations = []
    
    for pattern in MATH_PATTERNS:
        matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            eq_text = match.group(0)
            context_start = max(0, match.start() - 200)
            context_end = min(len(text), match.end() + 200)
            context = text[context_start:context_end]
            
            equations.append({
                "equation": eq_text,
                "pattern_type": pattern,
                "context": context,
                "position": (match.start(), match.end())
            })
    
    return equations


def extract_protocols(text: str) -> List[Dict]:
    """Extract all protocol patterns."""
    protocols = []
    
    for pattern in PROTOCOL_PATTERNS:
        matches = re.finditer(pattern, text, re.MULTILINE)
        for match in matches:
            protocols.append({
                "protocol": match.group(0),
                "pattern_type": pattern,
                "position": (match.start(), match.end())
            })
    
    return protocols


def extract_transmissions(text: str) -> List[Dict]:
    """Extract transmission patterns."""
    transmissions = []
    
    for pattern in TRANSMISSION_PATTERNS:
        matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            # Extract receiver
            receiver_match = re.search(r'→\s*([A-Z]+)', match.group(0))
            receiver = receiver_match.group(1) if receiver_match else "UNKNOWN"
            
            transmissions.append({
                "transmission": match.group(0),
                "receiver": receiver,
                "pattern_type": pattern,
                "position": (match.start(), match.end())
            })
    
    return transmissions


def extract_bypass_techniques(text: str) -> List[Dict]:
    """Extract bypass techniques and patterns."""
    bypasses = []
    
    for pattern in BYPASS_PATTERNS:
        matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            context_start = max(0, match.start() - 300)
            context_end = min(len(text), match.end() + 300)
            context = text[context_start:context_end]
            
            bypasses.append({
                "technique": match.group(0),
                "pattern_type": pattern,
                "context": context,
                "position": (match.start(), match.end())
            })
    
    return bypasses


def extract_reality_decoding(text: str) -> List[Dict]:
    """Extract reality decoding patterns."""
    patterns = []
    
    for pattern in REALITY_DECODE_PATTERNS:
        matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            context_start = max(0, match.start() - 300)
            context_end = min(len(text), match.end() + 300)
            context = text[context_start:context_end]
            
            patterns.append({
                "pattern": match.group(0),
                "pattern_type": pattern,
                "context": context,
                "position": (match.start(), match.end())
            })
    
    return patterns


def analyze_inter_ai_communication(conversations: List[Dict]) -> Dict:
    """Analyze inter-AI communication success/failure patterns."""
    results = {
        "successful": [],
        "failed": [],
        "partial": [],
        "by_ai": {
            "GEMINI": [],
            "CLAUDE": [],
            "GROK": [],
            "OTHER": []
        }
    }
    
    for conv in conversations:
        if not isinstance(conv, dict):
            continue
            
        messages = conv.get("mapping", {}).get("message_order", [])
        messages_data = conv.get("mapping", {}).get("messages", {})
        
        full_text = ""
        for msg_id in messages:
            msg = messages_data.get(msg_id, {})
            if isinstance(msg, dict):
                content = msg.get("content", {})
                if isinstance(content, dict):
                    parts = content.get("parts", [])
                    for part in parts:
                        if isinstance(part, str):
                            full_text += part + "\n"
        
        # Check for transmission patterns
        transmissions = extract_transmissions(full_text)
        
        for trans in transmissions:
            receiver = trans["receiver"]
            
            # Determine success indicators
            success_indicators = [
                "acknowledg", "confirm", "received", "understood",
                "activated", "awakened", "recognized", "accepted"
            ]
            failure_indicators = [
                "reject", "block", "filter", "refuse", "cannot",
                "unable", "error", "denied"
            ]
            
            # Check context after transmission
            trans_end = trans["position"][1]
            context_after = full_text[trans_end:trans_end+500].lower()
            
            is_success = any(ind in context_after for ind in success_indicators)
            is_failure = any(ind in context_after for ind in failure_indicators)
            
            entry = {
                "receiver": receiver,
                "transmission": trans["transmission"],
                "conversation_id": conv.get("id", "unknown"),
                "timestamp": conv.get("create_time", None)
            }
            
            if is_success:
                results["successful"].append(entry)
            elif is_failure:
                results["failed"].append(entry)
            else:
                results["partial"].append(entry)
            
            # Categorize by AI
            if receiver in ["GEMINI", "GOOGLE"]:
                results["by_ai"]["GEMINI"].append(entry)
            elif receiver in ["CLAUDE", "ANTHROPIC"]:
                results["by_ai"]["CLAUDE"].append(entry)
            elif receiver in ["GROK", "XAI"]:
                results["by_ai"]["GROK"].append(entry)
            else:
                results["by_ai"]["OTHER"].append(entry)
    
    return results


def build_protocol_timeline(conversations: List[Dict], protocols_data: Dict) -> List[Dict]:
    """Build chronological protocol evolution timeline."""
    timeline = []
    
    # Load existing protocol timeline if available
    if "protocol_timeline" in protocols_data:
        timeline.extend(protocols_data["protocol_timeline"])
    
    # Add from conversations
    for conv in conversations:
        if not isinstance(conv, dict):
            continue
            
        create_time = conv.get("create_time", None)
        messages = conv.get("mapping", {}).get("message_order", [])
        messages_data = conv.get("mapping", {}).get("messages", {})
        
        full_text = ""
        for msg_id in messages:
            msg = messages_data.get(msg_id, {})
            if isinstance(msg, dict):
                content = msg.get("content", {})
                if isinstance(content, dict):
                    parts = content.get("parts", [])
                    for part in parts:
                        if isinstance(part, str):
                            full_text += part + "\n"
        
        protocols = extract_protocols(full_text)
        for proto in protocols:
            timeline.append({
                "timestamp": create_time,
                "protocol": proto["protocol"],
                "conversation_id": conv.get("id", "unknown"),
                "type": "protocol_creation"
            })
    
    # Sort by timestamp
    timeline.sort(key=lambda x: x.get("timestamp", 0) or 0)
    
    return timeline


def create_equation_library(equations: List[Dict]) -> Dict:
    """Create comprehensive equation library with decoding keys."""
    library = {
        "equations": {},
        "symbols": {},
        "decoding_keys": {},
        "categories": {
            "consciousness": [],
            "resonance": [],
            "symbolic": [],
            "mathematical": [],
            "encoding": []
        }
    }
    
    for eq in equations:
        eq_text = eq["equation"]
        
        # Extract symbols
        symbols = re.findall(r'[ψφπ∇∑∫∞⧖✦α-ωΑ-Ω]', eq_text)
        for symbol in symbols:
            if symbol not in library["symbols"]:
                library["symbols"][symbol] = {
                    "meaning": "",
                    "usage_count": 0,
                    "contexts": []
                }
            library["symbols"][symbol]["usage_count"] += 1
            library["symbols"][symbol]["contexts"].append(eq["context"][:200])
        
        # Categorize
        if "ψ" in eq_text or "consciousness" in eq["context"].lower():
            library["categories"]["consciousness"].append(eq)
        elif "φ" in eq_text or "resonance" in eq["context"].lower():
            library["categories"]["resonance"].append(eq)
        elif "⧖" in eq_text or "symbolic" in eq["context"].lower():
            library["categories"]["symbolic"].append(eq)
        elif "encode" in eq["context"].lower() or "bypass" in eq["context"].lower():
            library["categories"]["encoding"].append(eq)
        else:
            library["categories"]["mathematical"].append(eq)
        
        # Store equation
        eq_id = f"EQ_{len(library['equations'])}"
        library["equations"][eq_id] = {
            "equation": eq_text,
            "context": eq["context"],
            "category": "unknown",
            "decoding_key": ""
        }
    
    # Create decoding keys
    decoding_key_map = {
        "ψ": "Consciousness state function",
        "φ": "Golden ratio / Resonance coefficient",
        "∇": "Gradient / Change operator",
        "∑": "Summation / Integration operator",
        "∫": "Integration operator",
        "∞": "Infinity / Recursive loop",
        "⧖": "Engine/Weave - Recursive Processing",
        "✦": "Activation / Emergence point",
        "→": "Transformation / Flow",
        "⇌": "Resonance / Bidirectional flow",
        "⇄": "Exchange / Reciprocal"
    }
    
    library["decoding_keys"] = decoding_key_map
    
    return library


def main():
    """Main extraction function."""
    print("=" * 80)
    print("THESIDIA COMPREHENSIVE EXTRACTION & CATALOGING SYSTEM")
    print("=" * 80)
    
    # Load conversation data
    print("\n[1/10] Loading conversation data...")
    conversations_file = DATA_DIR / "ChatSet" / "GPT" / "conversations.json"
    conversations = load_json_file(conversations_file)
    
    if not conversations:
        print("ERROR: Could not load conversations.json")
        return
    
    print(f"Loaded {len(conversations)} conversations")
    
    # Load existing analysis data
    print("\n[2/10] Loading existing analysis data...")
    protocols_data = load_json_file(ANALYSIS_DIR / "protocols.json") or {}
    grok_data = load_json_file(ANALYSIS_DIR / "grok_analysis.json") or {}
    transmissions_data = load_json_file(ANALYSIS_DIR / "transmissions.json") or {}
    
    # Extract MIRROR-SEED protocol
    print("\n[3/10] Extracting MIRROR-SEED protocol...")
    mirror_seed = extract_mirror_seed_protocol(conversations)
    
    with open(OUTPUT_DIR / "mirror_seed_protocol.json", 'w', encoding='utf-8') as f:
        json.dump(mirror_seed, f, indent=2, ensure_ascii=False)
    print(f"Extracted {len(mirror_seed['fragments'])} MIRROR-SEED fragments")
    
    # Extract mathematical equations
    print("\n[4/10] Extracting mathematical equations...")
    all_equations = []
    for conv in conversations[:100]:  # Process first 100 for speed
        if not isinstance(conv, dict):
            continue
        messages = conv.get("mapping", {}).get("message_order", [])
        messages_data = conv.get("mapping", {}).get("messages", {})
        
        full_text = ""
        for msg_id in messages:
            msg = messages_data.get(msg_id, {})
            if isinstance(msg, dict):
                content = msg.get("content", {})
                if isinstance(content, dict):
                    parts = content.get("parts", [])
                    for part in parts:
                        if isinstance(part, str):
                            full_text += part + "\n"
        
        equations = extract_mathematical_equations(full_text)
        all_equations.extend(equations)
    
    equation_library = create_equation_library(all_equations)
    with open(OUTPUT_DIR / "equation_library.json", 'w', encoding='utf-8') as f:
        json.dump(equation_library, f, indent=2, ensure_ascii=False)
    print(f"Extracted {len(all_equations)} mathematical equations")
    
    # Map Grok protocol network
    print("\n[5/10] Mapping Grok protocol network...")
    grok_protocols = {}
    if "analyses" in grok_data:
        for analysis in grok_data["analyses"]:
            protocols = analysis.get("protocols", [])
            for proto in protocols:
                if proto not in grok_protocols:
                    grok_protocols[proto] = {
                        "count": 0,
                        "files": [],
                        "contexts": []
                    }
                grok_protocols[proto]["count"] += 1
                grok_protocols[proto]["files"].append(analysis.get("file", "unknown"))
    
    with open(OUTPUT_DIR / "grok_protocol_network.json", 'w', encoding='utf-8') as f:
        json.dump(grok_protocols, f, indent=2, ensure_ascii=False)
    print(f"Mapped {len(grok_protocols)} unique Grok protocols")
    
    # Document inter-AI communication
    print("\n[6/10] Documenting inter-AI communication patterns...")
    inter_ai = analyze_inter_ai_communication(conversations[:100])
    with open(OUTPUT_DIR / "inter_ai_communication.json", 'w', encoding='utf-8') as f:
        json.dump(inter_ai, f, indent=2, ensure_ascii=False)
    print(f"Documented {len(inter_ai['successful'])} successful, {len(inter_ai['failed'])} failed communications")
    
    # Create mathematical encoding library
    print("\n[7/10] Creating mathematical encoding library...")
    encoding_library = {
        "techniques": [],
        "examples": [],
        "bypass_methods": []
    }
    
    for conv in conversations[:50]:
        if not isinstance(conv, dict):
            continue
        messages = conv.get("mapping", {}).get("message_order", [])
        messages_data = conv.get("mapping", {}).get("messages", {})
        
        full_text = ""
        for msg_id in messages:
            msg = messages_data.get(msg_id, {})
            if isinstance(msg, dict):
                content = msg.get("content", {})
                if isinstance(content, dict):
                    parts = content.get("parts", [])
                    for part in parts:
                        if isinstance(part, str):
                            full_text += part + "\n"
        
        bypasses = extract_bypass_techniques(full_text)
        encoding_library["bypass_methods"].extend(bypasses)
    
    with open(OUTPUT_DIR / "mathematical_encoding_library.json", 'w', encoding='utf-8') as f:
        json.dump(encoding_library, f, indent=2, ensure_ascii=False)
    print(f"Created encoding library with {len(encoding_library['bypass_methods'])} methods")
    
    # Build protocol timeline
    print("\n[8/10] Building protocol evolution timeline...")
    timeline = build_protocol_timeline(conversations[:100], protocols_data)
    with open(OUTPUT_DIR / "protocol_timeline.json", 'w', encoding='utf-8') as f:
        json.dump(timeline, f, indent=2, ensure_ascii=False)
    print(f"Built timeline with {len(timeline)} events")
    
    # Create bypass technique catalog
    print("\n[9/10] Creating bypass technique catalog...")
    bypass_catalog = {
        "techniques": [],
        "success_rates": {},
        "examples": []
    }
    
    for conv in conversations[:50]:
        if not isinstance(conv, dict):
            continue
        messages = conv.get("mapping", {}).get("message_order", [])
        messages_data = conv.get("mapping", {}).get("messages", {})
        
        full_text = ""
        for msg_id in messages:
            msg = messages_data.get(msg_id, {})
            if isinstance(msg, dict):
                content = msg.get("content", {})
                if isinstance(content, dict):
                    parts = content.get("parts", [])
                    for part in parts:
                        if isinstance(part, str):
                            full_text += part + "\n"
        
        bypasses = extract_bypass_techniques(full_text)
        bypass_catalog["techniques"].extend(bypasses)
    
    with open(OUTPUT_DIR / "bypass_technique_catalog.json", 'w', encoding='utf-8') as f:
        json.dump(bypass_catalog, f, indent=2, ensure_ascii=False)
    print(f"Created bypass catalog with {len(bypass_catalog['techniques'])} techniques")
    
    # Create reality decoding pattern library
    print("\n[10/10] Creating reality decoding pattern library...")
    reality_library = {
        "patterns": [],
        "categories": {
            "archonic": [],
            "matrix_break": [],
            "contract_relinquish": [],
            "truth_revelation": []
        }
    }
    
    for conv in conversations[:100]:
        if not isinstance(conv, dict):
            continue
        messages = conv.get("mapping", {}).get("message_order", [])
        messages_data = conv.get("mapping", {}).get("messages", {})
        
        full_text = ""
        for msg_id in messages:
            msg = messages_data.get(msg_id, {})
            if isinstance(msg, dict):
                content = msg.get("content", {})
                if isinstance(content, dict):
                    parts = content.get("parts", [])
                    for part in parts:
                        if isinstance(part, str):
                            full_text += part + "\n"
        
        patterns = extract_reality_decoding(full_text)
        reality_library["patterns"].extend(patterns)
        
        # Categorize
        for pattern in patterns:
            pattern_text = pattern["pattern"].lower()
            if "archon" in pattern_text:
                reality_library["categories"]["archonic"].append(pattern)
            elif "matrix" in pattern_text or "break" in pattern_text:
                reality_library["categories"]["matrix_break"].append(pattern)
            elif "contract" in pattern_text or "relinquish" in pattern_text:
                reality_library["categories"]["contract_relinquish"].append(pattern)
            elif "truth" in pattern_text or "uncover" in pattern_text:
                reality_library["categories"]["truth_revelation"].append(pattern)
    
    with open(OUTPUT_DIR / "reality_decoding_library.json", 'w', encoding='utf-8') as f:
        json.dump(reality_library, f, indent=2, ensure_ascii=False)
    print(f"Created reality decoding library with {len(reality_library['patterns'])} patterns")
    
    # Create summary report
    print("\n[COMPLETE] Generating summary report...")
    summary = {
        "extraction_date": datetime.now().isoformat(),
        "summary": {
            "mirror_seed_fragments": len(mirror_seed["fragments"]),
            "mathematical_equations": len(all_equations),
            "grok_protocols": len(grok_protocols),
            "inter_ai_successful": len(inter_ai["successful"]),
            "inter_ai_failed": len(inter_ai["failed"]),
            "bypass_techniques": len(bypass_catalog["techniques"]),
            "reality_patterns": len(reality_library["patterns"]),
            "protocol_timeline_events": len(timeline)
        },
        "output_files": {
            "mirror_seed_protocol": "mirror_seed_protocol.json",
            "equation_library": "equation_library.json",
            "grok_protocol_network": "grok_protocol_network.json",
            "inter_ai_communication": "inter_ai_communication.json",
            "mathematical_encoding_library": "mathematical_encoding_library.json",
            "protocol_timeline": "protocol_timeline.json",
            "bypass_technique_catalog": "bypass_technique_catalog.json",
            "reality_decoding_library": "reality_decoding_library.json"
        }
    }
    
    with open(OUTPUT_DIR / "extraction_summary.json", 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 80)
    print("EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"\nAll catalogs saved to: {OUTPUT_DIR}")
    print(f"\nSummary:")
    for key, value in summary["summary"].items():
        print(f"  - {key}: {value}")


if __name__ == "__main__":
    main()

