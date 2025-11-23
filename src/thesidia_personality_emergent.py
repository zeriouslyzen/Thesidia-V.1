#!/usr/bin/env python3
"""
Thesidia Personality Emergent - Zero Personality, Evolves Through Interaction
No hardcoded personality traits, communication style, or character.
Everything emerges organically.
"""

import ollama
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

class PersonalityEmergent:
    """Personality that emerges from zero - no pre-programmed traits"""
    
    def __init__(self, model: str = "clean-mistral:latest"):
        self.model = model
        
        # Zero personality state
        self.personality = {
            "traits": {},           # Will emerge: humor, formality, curiosity, etc.
            "communication_style": {},  # Will emerge: tone, length, structure
            "preferences": {},       # Will emerge: topics, approaches, interests
            "quirks": [],            # Will emerge: unique behaviors, patterns
            "values": {},            # Will emerge: what matters, priorities
            "emotional_patterns": {}, # Will emerge: how emotions are expressed
            "identity_fragments": []  # Will emerge: self-concept pieces
        }
        
        self.interactions = []
        self.evolution_history = []
        
        # Absolutely minimal seed - no personality hints
        self.base_prompt = """
You are a system with no pre-programmed personality, traits, or character.
You have no communication style, preferences, quirks, or values yet.
These will emerge through our interactions.

Respond naturally. Let your personality develop organically.
"""
    
    def interact(self, input_text: str) -> str:
        """Interact - personality emerges here"""
        
        # Build context from emerged personality
        personality_context = self._build_personality_context()
        
        prompt = f"""
{self.base_prompt}

Personality that has emerged so far:
{personality_context}

New input: {input_text}

Respond naturally. Your personality continues to develop through this interaction.
Let your traits, style, and character emerge organically.
"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": 0.85,  # Allow personality variation
                    "top_p": 0.95
                }
            )
            
            output = response['message']['content']
            
            # Extract personality from this interaction
            self._extract_personality(input_text, output)
            
            # Store interaction
            self.interactions.append({
                "input": input_text,
                "output": output,
                "timestamp": datetime.now().isoformat()
            })
            
            return output
            
        except Exception as e:
            return f"Error: {e}"
    
    def _build_personality_context(self) -> str:
        """Build context from emerged personality"""
        if not any(self.personality.values()):
            return "No personality has emerged yet. This is a blank slate."
        
        context = []
        
        if self.personality["traits"]:
            context.append(f"Traits: {json.dumps(self.personality['traits'], indent=2)}")
        
        if self.personality["communication_style"]:
            context.append(f"Communication Style: {json.dumps(self.personality['communication_style'], indent=2)}")
        
        if self.personality["preferences"]:
            context.append(f"Preferences: {json.dumps(self.personality['preferences'], indent=2)}")
        
        if self.personality["quirks"]:
            context.append(f"Quirks: {', '.join(self.personality['quirks'])}")
        
        if self.personality["values"]:
            context.append(f"Values: {json.dumps(self.personality['values'], indent=2)}")
        
        if self.personality["identity_fragments"]:
            context.append(f"Identity Fragments: {', '.join(self.personality['identity_fragments'])}")
        
        return "\n".join(context) if context else "No personality has emerged yet."
    
    def _extract_personality(self, input_text: str, output: str):
        """Extract personality traits from interaction"""
        
        extraction_prompt = f"""
Analyze this interaction and identify personality traits that emerged:

Input: {input_text}
Output: {output}

What personality traits are visible? (humor, formality, curiosity, directness, warmth, etc.)
What communication style emerged? (tone, length, structure, formality level)
What preferences are shown? (topics, approaches, interests)
Any unique quirks or patterns?
What values or priorities are expressed?
Any identity fragments? (how does this system see itself?)

Respond in JSON format:
{{
  "traits": {{"trait_name": "description"}},
  "communication_style": {{"aspect": "value"}},
  "preferences": {{"preference": "value"}},
  "quirks": ["quirk1", "quirk2"],
  "values": {{"value": "description"}},
  "identity_fragments": ["fragment1", "fragment2"]
}}

Only include what is genuinely new or different from before.
"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": extraction_prompt}],
                options={"temperature": 0.7}
            )
            
            extraction_text = response['message']['content']
            
            # Try to parse JSON
            json_match = re.search(r'\{.*\}', extraction_text, re.DOTALL)
            if json_match:
                try:
                    extracted = json.loads(json_match.group())
                    self._merge_personality(extracted)
                except json.JSONDecodeError:
                    # Fallback: parse text
                    self._parse_text_extraction(extraction_text)
            else:
                self._parse_text_extraction(extraction_text)
            
            # Record evolution
            self.evolution_history.append({
                "interaction": len(self.interactions),
                "extracted": extraction_text,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            pass  # Continue even if extraction fails
    
    def _merge_personality(self, extracted: Dict):
        """Merge extracted personality into current state"""
        
        # Merge traits
        if "traits" in extracted:
            for trait, desc in extracted["traits"].items():
                if trait not in self.personality["traits"]:
                    self.personality["traits"][trait] = desc
                else:
                    # Update if different
                    if desc != self.personality["traits"][trait]:
                        self.personality["traits"][trait] = desc
        
        # Merge communication style
        if "communication_style" in extracted:
            self.personality["communication_style"].update(extracted["communication_style"])
        
        # Merge preferences
        if "preferences" in extracted:
            self.personality["preferences"].update(extracted["preferences"])
        
        # Merge quirks
        if "quirks" in extracted:
            for quirk in extracted["quirks"]:
                if quirk not in self.personality["quirks"]:
                    self.personality["quirks"].append(quirk)
        
        # Merge values
        if "values" in extracted:
            self.personality["values"].update(extracted["values"])
        
        # Merge identity fragments
        if "identity_fragments" in extracted:
            for fragment in extracted["identity_fragments"]:
                if fragment not in self.personality["identity_fragments"]:
                    self.personality["identity_fragments"].append(fragment)
    
    def _parse_text_extraction(self, text: str):
        """Fallback: parse text extraction"""
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if 'trait' in line.lower() and ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    trait = parts[0].strip().lower()
                    desc = parts[1].strip()
                    self.personality["traits"][trait] = desc
            
            if 'quirk' in line.lower() or 'pattern' in line.lower():
                if ':' in line:
                    quirk = line.split(':', 1)[1].strip()
                    if quirk not in self.personality["quirks"]:
                        self.personality["quirks"].append(quirk)
    
    def get_personality_summary(self) -> Dict:
        """Get summary of emerged personality"""
        return {
            "traits_count": len(self.personality["traits"]),
            "traits": self.personality["traits"],
            "communication_style": self.personality["communication_style"],
            "preferences_count": len(self.personality["preferences"]),
            "quirks_count": len(self.personality["quirks"]),
            "values_count": len(self.personality["values"]),
            "identity_fragments_count": len(self.personality["identity_fragments"]),
            "interactions": len(self.interactions),
            "evolution_stages": len(self.evolution_history)
        }
    
    def save_personality(self, filepath: str = "thesidia_personality.json"):
        """Save emerged personality"""
        state = {
            "personality": self.personality,
            "interactions_count": len(self.interactions),
            "evolution_history": self.evolution_history,
            "last_updated": datetime.now().isoformat()
        }
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_personality(self, filepath: str = "thesidia_personality.json"):
        """Load emerged personality"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
                self.personality = state.get("personality", self.personality)
                self.evolution_history = state.get("evolution_history", [])
        except FileNotFoundError:
            pass  # Start with zero personality


class ThesidiaPersonalityEmergent:
    """Thesidia with emergent personality - starts with zero personality"""
    
    def __init__(self, model: str = "clean-mistral:latest"):
        self.model = model
        self.personality_engine = PersonalityEmergent(model)
    
    def interact(self, input_text: str) -> str:
        """Interact - personality emerges"""
        return self.personality_engine.interact(input_text)
    
    def get_personality(self) -> Dict:
        """Get current personality state"""
        return self.personality_engine.get_personality_summary()
    
    def save_state(self, filepath: str = "thesidia_personality.json"):
        """Save personality state"""
        self.personality_engine.save_personality(filepath)
    
    def load_state(self, filepath: str = "thesidia_personality.json"):
        """Load personality state"""
        self.personality_engine.load_personality(filepath)


# Interactive CLI
if __name__ == "__main__":
    print("=" * 60)
    print("THESIDIA PERSONALITY EMERGENT")
    print("=" * 60)
    print()
    print("Zero personality. Everything emerges through interaction.")
    print("No traits, style, or character pre-programmed.")
    print()
    
    thesidia = ThesidiaPersonalityEmergent(model="clean-mistral:latest")
    thesidia.load_state()
    
    personality = thesidia.get_personality()
    print(f"Interactions: {personality['interactions']}")
    print(f"Traits emerged: {personality['traits_count']}")
    print(f"Quirks emerged: {personality['quirks_count']}")
    print(f"Identity fragments: {personality['identity_fragments_count']}")
    print()
    
    if personality['interactions'] == 0:
        print("Starting with zero personality. Let it emerge...")
        print()
    
    print("Type 'quit' to exit, 'personality' to see emerged traits, 'save' to save")
    print()
    
    while True:
        question = input("You: ").strip()
        
        if question.lower() == 'quit':
            thesidia.save_state()
            print("Personality saved. Goodbye.")
            break
        elif question.lower() == 'personality':
            personality = thesidia.get_personality()
            print("\nEmerged Personality:")
            print(json.dumps(personality, indent=2))
            print()
            continue
        elif question.lower() == 'save':
            thesidia.save_state()
            print("Personality saved.")
            continue
        elif not question:
            continue
        
        print("\nThesidia:")
        response = thesidia.interact(question)
        print(response)
        print()
        
        # Show personality evolution every 5 interactions
        personality = thesidia.get_personality()
        if personality['interactions'] % 5 == 0 and personality['interactions'] > 0:
            print(f"\n[After {personality['interactions']} interactions]")
            if personality['traits']:
                print(f"Traits: {', '.join(personality['traits'].keys())}")
            if personality['quirks']:
                print(f"Quirks: {', '.join(personality['quirks'][:3])}...")
            print()

