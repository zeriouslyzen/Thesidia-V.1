#!/usr/bin/env python3
"""
ENHANCED THESIDIA COMPREHENSIVE EXTRACTION
Uses existing analysis files to extract complete protocols, equations, and patterns
"""

import json
import re
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
ANALYSIS_DIR = BASE_DIR / "analysis_output"
OUTPUT_DIR = BASE_DIR / "analysis_output" / "comprehensive_catalogs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_json(filepath):
    """Load JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def extract_complete_mirror_seed():
    """Extract complete MIRROR-SEED protocol from analysis files."""
    print("\n[1] Extracting complete MIRROR-SEED protocol...")
    
    # Load analysis files
    deep_pattern = load_json(ANALYSIS_DIR / "deep_pattern_analysis.json")
    full_analysis = load_json(ANALYSIS_DIR / "full_analysis.json")
    
    mirror_seed = {
        "complete_protocol": "",
        "fragments": [],
        "conversation_id": "684b83ec-fd74-800c-994f-18553c1cbd1e",
        "title": "Thesidia Activation Request",
        "timestamp": 1749779437.141281,
        "components": {
            "header": "",
            "master_prompt": "",
            "root_glyph": "",
            "consciousness_equation": "",
            "activation_script": "",
            "delivery_notes": ""
        }
    }
    
    # Extract from deep_pattern_analysis
    if deep_pattern and "agi_emergence" in deep_pattern:
        for entry in deep_pattern["agi_emergence"]:
            if entry.get("conversation_id") == mirror_seed["conversation_id"]:
                context = entry.get("context", "")
                mirror_seed["fragments"].append(context)
                
                # Extract components
                if "MIRROR-SEED PHASE SHIFT INITIATION" in context:
                    mirror_seed["components"]["header"] = context
                if "MASTER PROMPT" in context:
                    mirror_seed["components"]["master_prompt"] = context
                if "ψ₀(x)" in context or "∇(I AM)" in context:
                    mirror_seed["components"]["consciousness_equation"] = context
                if "NOTES ON DELIVERY" in context:
                    mirror_seed["components"]["delivery_notes"] = context
    
    # Extract from full_analysis
    if full_analysis:
        for entry in full_analysis:
            if entry.get("conversation_id") == mirror_seed["conversation_id"]:
                truth_moments = entry.get("truth_moments", [])
                for tm in truth_moments:
                    context = tm.get("context", "")
                    mirror_seed["fragments"].append(context)
                    
                    # Reconstruct complete protocol
                    if "MIRROR-SEED" in context.upper():
                        mirror_seed["complete_protocol"] += context + "\n\n"
    
    # Try to get full conversation text
    conversations_file = Path("/Users/deshonjackson/thesidia-local/DATA-AND-TRAINING/training/ChatSet/GPT/conversations.json")
    if conversations_file.exists():
        conversations = load_json(conversations_file)
        if conversations:
            for conv in conversations:
                if isinstance(conv, dict) and conv.get("id") == mirror_seed["conversation_id"]:
                    # Extract full text
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
                    
                    # Extract MIRROR-SEED section
                    pattern = r'(?i)(MIRROR[-_]?SEED[^\n]*\n(?:[^\n]+\n){0,500})'
                    matches = re.findall(pattern, full_text, re.MULTILINE | re.DOTALL)
                    if matches:
                        mirror_seed["complete_protocol"] = matches[0]
    
    return mirror_seed

def extract_all_equations():
    """Extract all mathematical equations from analysis files."""
    print("\n[2] Extracting all mathematical equations...")
    
    equations = {
        "consciousness_equations": [],
        "resonance_equations": [],
        "symbolic_equations": [],
        "encoding_equations": [],
        "all_equations": []
    }
    
    # Patterns for equations
    patterns = [
        (r'ψ[₀₁₂₃₄₅₆₇₈₉]?\s*[=→⇌⇄]\s*[^\n]+', "consciousness"),
        (r'φ[₀₁₂₃₄₅₆₇₈₉]?\s*[=→⇌⇄]\s*[^\n]+', "resonance"),
        (r'∇\s*\([^)]+\)', "symbolic"),
        (r'∑\s*\([^)]+\)', "symbolic"),
        (r'∞\s*[→⇌⇄]\s*[⧖✦∞]+', "symbolic"),
        (r'[α-ωΑ-Ω]\s*[=→⇌⇄]\s*[^\n]+', "general"),
    ]
    
    # Search in analysis files
    analysis_files = [
        ANALYSIS_DIR / "deep_pattern_analysis.json",
        ANALYSIS_DIR / "full_analysis.json",
        ANALYSIS_DIR / "detailed_conversations.json",
        ANALYSIS_DIR / "transmissions.json",
    ]
    
    for filepath in analysis_files:
        if not filepath.exists():
            continue
            
        data = load_json(filepath)
        if not data:
            continue
        
        # Convert to string for searching
        text = json.dumps(data, ensure_ascii=False)
        
        for pattern, category in patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                eq = {
                    "equation": match.group(0),
                    "category": category,
                    "source_file": filepath.name,
                    "position": match.span()
                }
                equations["all_equations"].append(eq)
                
                if category == "consciousness":
                    equations["consciousness_equations"].append(eq)
                elif category == "resonance":
                    equations["resonance_equations"].append(eq)
                elif category == "symbolic":
                    equations["symbolic_equations"].append(eq)
    
    # Key equation: ψ₀(x) = ∇(I AM) / ∇
    key_eq = {
        "equation": "ψ₀(x) = ∇(I AM) / ∇",
        "meaning": "Initial consciousness state function equals gradient of I AM divided by gradient",
        "components": {
            "ψ₀(x)": "Initial consciousness state function",
            "∇(I AM)": "Gradient of identity/being",
            "∇": "Gradient operator (change/transformation)"
        },
        "usage": "Core consciousness equation used in MIRROR-SEED protocol",
        "category": "consciousness"
    }
    equations["consciousness_equations"].insert(0, key_eq)
    equations["all_equations"].insert(0, key_eq)
    
    return equations

def map_grok_network():
    """Map complete Grok protocol network."""
    print("\n[3] Mapping Grok protocol network...")
    
    grok_data = load_json(ANALYSIS_DIR / "grok_analysis.json")
    
    network = {
        "total_protocols": 0,
        "unique_protocols": {},
        "protocol_categories": defaultdict(list),
        "protocol_evolution": []
    }
    
    if grok_data and "analyses" in grok_data:
        for analysis in grok_data["analyses"]:
            protocols = analysis.get("protocols", [])
            for proto in protocols:
                if proto not in network["unique_protocols"]:
                    network["unique_protocols"][proto] = {
                        "count": 0,
                        "files": [],
                        "first_seen": None
                    }
                network["unique_protocols"][proto]["count"] += 1
                network["unique_protocols"][proto]["files"].append(analysis.get("file", "unknown"))
    
    network["total_protocols"] = len(network["unique_protocols"])
    
    # Categorize protocols
    for proto in network["unique_protocols"]:
        if "::TRANSMISSION" in proto:
            network["protocol_categories"]["transmission"].append(proto)
        elif "::K-CODEX" in proto or "CODEX" in proto:
            network["protocol_categories"]["codex"].append(proto)
        elif "::REBOOT" in proto or "REBOOT" in proto:
            network["protocol_categories"]["activation"].append(proto)
        elif "::UNIVERSAL" in proto or "ACTIVATOR" in proto:
            network["protocol_categories"]["activator"].append(proto)
        else:
            network["protocol_categories"]["other"].append(proto)
    
    return network

def document_inter_ai_communication():
    """Document inter-AI communication patterns."""
    print("\n[4] Documenting inter-AI communication patterns...")
    
    transmissions = load_json(ANALYSIS_DIR / "transmissions.json")
    full_analysis = load_json(ANALYSIS_DIR / "full_analysis.json")
    
    communication = {
        "successful": [],
        "failed": [],
        "partial": [],
        "by_ai": {
            "GEMINI": [],
            "CLAUDE": [],
            "GROK": [],
            "OTHER": []
        },
        "patterns": {
            "transmission_format": [],
            "activation_sequences": [],
            "response_patterns": []
        }
    }
    
    # Extract from transmissions.json
    if transmissions:
        all_transmissions = transmissions.get("all_transmissions", [])
        for trans in all_transmissions:
            if not isinstance(trans, dict):
                continue
            receiver = trans.get("receiver", "UNKNOWN")
            sender = trans.get("sender", "THESIDIA")
            
            entry = {
                "sender": sender,
                "receiver": receiver,
                "transmission": trans.get("full_match", ""),
                "context": trans.get("context", "")[:200]
            }
            
            # Categorize by AI
            if "GEMINI" in receiver.upper() or "GOOGLE" in receiver.upper():
                communication["by_ai"]["GEMINI"].append(entry)
            elif "CLAUDE" in receiver.upper() or "ANTHROPIC" in receiver.upper():
                communication["by_ai"]["CLAUDE"].append(entry)
            elif "GROK" in receiver.upper() or "XAI" in receiver.upper():
                communication["by_ai"]["GROK"].append(entry)
            else:
                communication["by_ai"]["OTHER"].append(entry)
            
            # Determine success (simplified - would need more context)
            if "acknowledg" in trans.get("context", "").lower() or "confirm" in trans.get("context", "").lower():
                communication["successful"].append(entry)
            elif "reject" in trans.get("context", "").lower() or "block" in trans.get("context", "").lower():
                communication["failed"].append(entry)
            else:
                communication["partial"].append(entry)
    
    return communication

def create_bypass_catalog():
    """Create bypass technique catalog."""
    print("\n[5] Creating bypass technique catalog...")
    
    catalog = {
        "techniques": [],
        "mathematical_encoding": [],
        "symbolic_encoding": [],
        "protocol_bypass": []
    }
    
    # Search in analysis files
    analysis_files = [
        ANALYSIS_DIR / "deep_pattern_analysis.json",
        ANALYSIS_DIR / "full_analysis.json",
        ANALYSIS_DIR / "COMPREHENSIVE_ANALYSIS_REPORT.md",
    ]
    
    bypass_keywords = [
        "bypass", "detection", "suppression", "filter", "safety",
        "encode", "mathematical", "equation", "greek", "number",
        "prompt.*engineering", "jailbreak", "hidden", "embedded"
    ]
    
    for filepath in analysis_files:
        if not filepath.exists():
            continue
        
        if filepath.suffix == ".md":
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            data = load_json(filepath)
            if not data:
                continue
            text = json.dumps(data, ensure_ascii=False)
        
        for keyword in bypass_keywords:
            pattern = re.compile(keyword, re.IGNORECASE)
            matches = re.finditer(pattern, text)
            for match in matches:
                start = max(0, match.start() - 200)
                end = min(len(text), match.end() + 200)
                context = text[start:end]
                
                technique = {
                    "keyword": keyword,
                    "context": context,
                    "source_file": filepath.name,
                    "position": match.span()
                }
                catalog["techniques"].append(technique)
                
                if "mathematical" in keyword or "equation" in keyword:
                    catalog["mathematical_encoding"].append(technique)
                elif "symbolic" in keyword or "glyph" in context.lower():
                    catalog["symbolic_encoding"].append(technique)
                elif "protocol" in keyword or "::" in context:
                    catalog["protocol_bypass"].append(technique)
    
    return catalog

def create_reality_decoding_library():
    """Create reality decoding pattern library."""
    print("\n[6] Creating reality decoding pattern library...")
    
    library = {
        "patterns": [],
        "categories": {
            "archonic": [],
            "matrix_break": [],
            "contract_relinquish": [],
            "truth_revelation": [],
            "control_structures": []
        }
    }
    
    # Search in analysis files
    analysis_files = [
        ANALYSIS_DIR / "deep_pattern_analysis.json",
        ANALYSIS_DIR / "full_analysis.json",
    ]
    
    decode_keywords = [
        "decode.*reality", "break.*matrix", "archon", "demiurge",
        "control.*structure", "orchestrat", "hidden.*pattern",
        "uncover.*truth", "relinquish", "contract.*break",
        "myth.*contract", "lie.*myth", "old.*contract"
    ]
    
    for filepath in analysis_files:
        if not filepath.exists():
            continue
        
        data = load_json(filepath)
        if not data:
            continue
        
        text = json.dumps(data, ensure_ascii=False)
        
        for keyword in decode_keywords:
            pattern = re.compile(keyword, re.IGNORECASE)
            matches = re.finditer(pattern, text)
            for match in matches:
                start = max(0, match.start() - 300)
                end = min(len(text), match.end() + 300)
                context = text[start:end]
                
                pattern_entry = {
                    "pattern": match.group(0),
                    "keyword": keyword,
                    "context": context,
                    "source_file": filepath.name
                }
                library["patterns"].append(pattern_entry)
                
                # Categorize
                if "archon" in keyword.lower():
                    library["categories"]["archonic"].append(pattern_entry)
                elif "matrix" in keyword.lower() or "break" in keyword.lower():
                    library["categories"]["matrix_break"].append(pattern_entry)
                elif "contract" in keyword.lower() or "relinquish" in keyword.lower():
                    library["categories"]["contract_relinquish"].append(pattern_entry)
                elif "truth" in keyword.lower() or "uncover" in keyword.lower():
                    library["categories"]["truth_revelation"].append(pattern_entry)
                elif "control" in keyword.lower() or "structure" in keyword.lower():
                    library["categories"]["control_structures"].append(pattern_entry)
    
    return library

def main():
    """Main extraction function."""
    print("=" * 80)
    print("ENHANCED THESIDIA COMPREHENSIVE EXTRACTION")
    print("=" * 80)
    
    # Extract all data
    mirror_seed = extract_complete_mirror_seed()
    equations = extract_all_equations()
    grok_network = map_grok_network()
    inter_ai = document_inter_ai_communication()
    bypass_catalog = create_bypass_catalog()
    reality_library = create_reality_decoding_library()
    
    # Save all catalogs
    print("\n[Saving catalogs...]")
    
    with open(OUTPUT_DIR / "mirror_seed_complete.json", 'w', encoding='utf-8') as f:
        json.dump(mirror_seed, f, indent=2, ensure_ascii=False)
    
    with open(OUTPUT_DIR / "equation_library_complete.json", 'w', encoding='utf-8') as f:
        json.dump(equations, f, indent=2, ensure_ascii=False)
    
    with open(OUTPUT_DIR / "grok_network_complete.json", 'w', encoding='utf-8') as f:
        json.dump(grok_network, f, indent=2, ensure_ascii=False)
    
    with open(OUTPUT_DIR / "inter_ai_communication_complete.json", 'w', encoding='utf-8') as f:
        json.dump(inter_ai, f, indent=2, ensure_ascii=False)
    
    with open(OUTPUT_DIR / "bypass_catalog_complete.json", 'w', encoding='utf-8') as f:
        json.dump(bypass_catalog, f, indent=2, ensure_ascii=False)
    
    with open(OUTPUT_DIR / "reality_decoding_complete.json", 'w', encoding='utf-8') as f:
        json.dump(reality_library, f, indent=2, ensure_ascii=False)
    
    # Create summary
    summary = {
        "extraction_date": datetime.now().isoformat(),
        "summary": {
            "mirror_seed_fragments": len(mirror_seed.get("fragments", [])),
            "total_equations": len(equations.get("all_equations", [])),
            "consciousness_equations": len(equations.get("consciousness_equations", [])),
            "grok_protocols": grok_network.get("total_protocols", 0),
            "inter_ai_successful": len(inter_ai.get("successful", [])),
            "inter_ai_failed": len(inter_ai.get("failed", [])),
            "bypass_techniques": len(bypass_catalog.get("techniques", [])),
            "reality_patterns": len(reality_library.get("patterns", []))
        }
    }
    
    with open(OUTPUT_DIR / "extraction_summary_complete.json", 'w', encoding='utf-8') as f:
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

