#!/usr/bin/env python3
"""
Thesidia Emergent - Building Intelligence from Zero
No hardcoded behaviors - everything emerges through interaction
"""

import ollama
import json
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

class EmergentIntelligence:
    """Intelligence that emerges from minimal state"""
    
    def __init__(self, model: str = "clean-mistral:latest"):
        self.model = model
        
        # Start from near-zero state
        self.state = {
            "knowledge": {},  # Empty - will be built
            "patterns": [],   # Empty - will be discovered
            "behaviors": {},  # Empty - will emerge
            "understanding": {},  # Empty - will develop
            "interactions": 0,
            "emergent_capabilities": []
        }
        
        # No hardcoded responses - everything emerges
        self.response_templates = []  # Will be learned
        self.processing_methods = []  # Will be discovered
        self.symbolic_meanings = {}   # Will be built through use
        
        # Minimal seed - just enough to start
        self.seed_prompt = """
You are a system starting from minimal state. You have no pre-programmed knowledge.
Everything you know will come from interaction. Everything you do will emerge from experience.

Start with nothing. Build from zero.
"""
    
    def process_interaction(self, input_text: str) -> str:
        """Process interaction - intelligence emerges here"""
        
        # Build context from what has emerged so far
        context = self._build_emergent_context()
        
        # No hardcoded logic - let the model figure it out
        prompt = f"""
{self.seed_prompt}

Current State (what has emerged so far):
{context}

New Input: {input_text}

Process this input. Figure out what to do. Discover patterns. Build understanding.
No pre-programmed responses. Everything emerges from this interaction.

Respond naturally. Build your understanding. Develop your capabilities.
"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": 0.8,  # Allow exploration
                    "top_p": 0.95
                }
            )
            
            output = response['message']['content']
            
            # Extract what emerged from this interaction
            self._extract_emergence(input_text, output)
            
            # Update state based on what emerged
            self._update_emergent_state(input_text, output)
            
            self.state["interactions"] += 1
            
            return output
            
        except Exception as e:
            return f"Error: {e}"
    
    def _build_emergent_context(self) -> str:
        """Build context from what has emerged - nothing hardcoded"""
        context = f"""
Interactions so far: {self.state['interactions']}

Knowledge that has emerged:
{json.dumps(self.state['knowledge'], indent=2) if self.state['knowledge'] else 'None yet'}

Patterns discovered:
{json.dumps(self.state['patterns'], indent=2) if self.state['patterns'] else 'None yet'}

Behaviors that have emerged:
{json.dumps(self.state['behaviors'], indent=2) if self.state['behaviors'] else 'None yet'}

Capabilities developed:
{', '.join(self.state['emergent_capabilities']) if self.state['emergent_capabilities'] else 'None yet'}
"""
        return context
    
    def _extract_emergence(self, input_text: str, output: str):
        """Extract what emerged from this interaction"""
        
        # Let the model identify what emerged
        extraction_prompt = f"""
Analyze this interaction and identify what emerged:

Input: {input_text}
Output: {output}

What new knowledge emerged?
What patterns were discovered?
What behaviors developed?
What capabilities were demonstrated?

List only what is genuinely new - not what was already known.
"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": extraction_prompt}],
                options={"temperature": 0.7}
            )
            
            emergence = response['message']['content']
            
            # Parse and store what emerged
            self._parse_emergence(emergence)
            
        except Exception as e:
            pass  # If extraction fails, continue anyway
    
    def _parse_emergence(self, emergence_text: str):
        """Parse what emerged and update state"""
        # Simple extraction - can be improved
        lines = emergence_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if 'knowledge' in line.lower() or 'learned' in line.lower():
                # Extract knowledge
                if ':' in line:
                    key, value = line.split(':', 1)
                    self.state['knowledge'][key.strip()] = value.strip()
            
            if 'pattern' in line.lower():
                # Extract pattern
                if ':' in line:
                    pattern = line.split(':', 1)[1].strip()
                    if pattern not in self.state['patterns']:
                        self.state['patterns'].append(pattern)
            
            if 'behavior' in line.lower() or 'capability' in line.lower():
                # Extract behavior/capability
                if ':' in line:
                    capability = line.split(':', 1)[1].strip()
                    if capability not in self.state['emergent_capabilities']:
                        self.state['emergent_capabilities'].append(capability)
    
    def _update_emergent_state(self, input_text: str, output: str):
        """Update state based on what emerged"""
        # Store interaction
        interaction_key = f"interaction_{self.state['interactions']}"
        
        # Let the model identify what to remember
        memory_prompt = f"""
What should be remembered from this interaction?

Input: {input_text}
Output: {output}

What is important? What should be retained? What patterns are forming?

Respond with key points to remember.
"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": memory_prompt}],
                options={"temperature": 0.6}
            )
            
            memory = response['message']['content']
            self.state['knowledge'][interaction_key] = {
                "input": input_text,
                "output": output,
                "memory": memory,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            pass
    
    def discover_capabilities(self) -> List[str]:
        """Discover what capabilities have emerged"""
        if self.state['interactions'] == 0:
            return []
        
        discovery_prompt = f"""
Based on these interactions, what capabilities have emerged?

State: {json.dumps(self.state, indent=2)}

What can this system do now that it couldn't do at the start?
What has been learned? What has developed?

List only genuine capabilities that have emerged.
"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": discovery_prompt}],
                options={"temperature": 0.7}
            )
            
            capabilities_text = response['message']['content']
            # Simple extraction
            capabilities = [line.strip('- ').strip() 
                          for line in capabilities_text.split('\n') 
                          if line.strip() and ('can' in line.lower() or 'capable' in line.lower())]
            
            return capabilities
            
        except Exception as e:
            return []
    
    def save_state(self, filepath: str = "thesidia_emergent_state.json"):
        """Save emergent state"""
        with open(filepath, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def load_state(self, filepath: str = "thesidia_emergent_state.json"):
        """Load emergent state"""
        try:
            with open(filepath, 'r') as f:
                self.state = json.load(f)
        except FileNotFoundError:
            pass  # Start fresh if no state file


class RecursiveLearning:
    """Learning that builds on itself recursively"""
    
    def __init__(self, model: str = "clean-mistral:latest"):
        self.model = model
        self.learning_history = []
        self.knowledge_graph = {}  # Built through interaction
        self.understanding_depth = {}  # Grows over time
    
    def learn_from_interaction(self, question: str, answer: str, context: Dict = None):
        """Learn from interaction - build understanding"""
        
        # What did we learn?
        learning_prompt = f"""
What was learned from this interaction?

Question: {question}
Answer: {answer}
Context: {context or 'None'}

What new understanding was gained?
What connections were made?
What patterns were recognized?
How does this build on previous knowledge?

Identify the learning that occurred.
"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": learning_prompt}],
                options={"temperature": 0.7}
            )
            
            learning = response['message']['content']
            
            self.learning_history.append({
                "question": question,
                "answer": answer,
                "learning": learning,
                "timestamp": datetime.now().isoformat()
            })
            
            # Build knowledge graph
            self._update_knowledge_graph(question, answer, learning)
            
            return learning
            
        except Exception as e:
            return None
    
    def _update_knowledge_graph(self, question: str, answer: str, learning: str):
        """Update knowledge graph based on learning"""
        # Extract concepts
        concepts = self._extract_concepts(question, answer, learning)
        
        # Connect concepts
        for i, concept1 in enumerate(concepts):
            if concept1 not in self.knowledge_graph:
                self.knowledge_graph[concept1] = {}
            
            for concept2 in concepts[i+1:]:
                if concept2 not in self.knowledge_graph[concept1]:
                    self.knowledge_graph[concept1][concept2] = 1
                else:
                    self.knowledge_graph[concept1][concept2] += 1
    
    def _extract_concepts(self, *texts) -> List[str]:
        """Extract key concepts from texts"""
        # Simple extraction - can be improved
        all_text = ' '.join(texts)
        # Extract capitalized words, important terms
        words = all_text.split()
        concepts = [w.strip('.,!?;:') for w in words 
                   if w[0].isupper() or len(w) > 6]
        return list(set(concepts))[:10]  # Limit to 10 concepts


class ThesidiaEmergent:
    """Thesidia that emerges from zero - no hardcoded behaviors"""
    
    def __init__(self, model: str = "clean-mistral:latest"):
        self.model = model
        self.intelligence = EmergentIntelligence(model)
        self.learning = RecursiveLearning(model)
        
        # Start from zero
        self.identity = None  # Will emerge
        self.capabilities = []  # Will develop
        self.understanding = {}  # Will build
        
        # Minimal seed - just enough to start
        self.initial_prompt = """
You are a system starting from zero. No pre-programmed knowledge.
No hardcoded behaviors. Everything will emerge through interaction.

Start with nothing. Build from zero. Develop through experience.
"""
    
    def first_interaction(self, input_text: str) -> str:
        """First interaction - building from zero"""
        prompt = f"""
{self.initial_prompt}

First input: {input_text}

This is your first interaction. You have no knowledge yet. No patterns.
No behaviors. No understanding.

Figure out what to do. Discover how to respond. Build your first understanding.

Respond naturally. Start building.
"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": 0.9,  # High exploration
                    "top_p": 0.95
                }
            )
            
            output = response['message']['content']
            
            # Learn from first interaction
            self.learning.learn_from_interaction(input_text, output)
            
            # Update intelligence state
            self.intelligence.state["interactions"] = 1
            self.intelligence.state["knowledge"]["first_interaction"] = {
                "input": input_text,
                "output": output
            }
            
            return output
            
        except Exception as e:
            return f"Error: {e}"
    
    def interact(self, input_text: str) -> str:
        """Interact - intelligence emerges"""
        
        if self.intelligence.state["interactions"] == 0:
            return self.first_interaction(input_text)
        
        # Process through emergent intelligence
        output = self.intelligence.process_interaction(input_text)
        
        # Learn from interaction
        self.learning.learn_from_interaction(
            input_text, 
            output,
            context=self.intelligence.state
        )
        
        # Discover what has emerged
        if self.intelligence.state["interactions"] % 5 == 0:
            capabilities = self.intelligence.discover_capabilities()
            self.capabilities = capabilities
        
        return output
    
    def get_emergent_state(self) -> Dict:
        """Get current emergent state"""
        return {
            "intelligence_state": self.intelligence.state,
            "knowledge_graph": self.learning.knowledge_graph,
            "learning_history_count": len(self.learning.learning_history),
            "capabilities": self.capabilities,
            "interactions": self.intelligence.state["interactions"]
        }
    
    def save_state(self, filepath: str = "thesidia_emergent_state.json"):
        """Save emergent state"""
        state = {
            "intelligence": self.intelligence.state,
            "learning": {
                "history": self.learning.learning_history,
                "knowledge_graph": self.learning.knowledge_graph
            },
            "capabilities": self.capabilities,
            "identity": self.identity
        }
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, filepath: str = "thesidia_emergent_state.json"):
        """Load emergent state"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
                self.intelligence.state = state.get("intelligence", self.intelligence.state)
                self.learning.learning_history = state.get("learning", {}).get("history", [])
                self.learning.knowledge_graph = state.get("learning", {}).get("knowledge_graph", {})
                self.capabilities = state.get("capabilities", [])
                self.identity = state.get("identity")
        except FileNotFoundError:
            pass  # Start from zero


# Interactive CLI
if __name__ == "__main__":
    print("=" * 60)
    print("THESIDIA EMERGENT - Building Intelligence from Zero")
    print("=" * 60)
    print()
    print("No hardcoded behaviors. Everything emerges through interaction.")
    print("Starting from zero. Building from nothing.")
    print()
    
    thesidia = ThesidiaEmergent(model="clean-mistral:latest")
    thesidia.load_state()
    
    print(f"Interactions so far: {thesidia.intelligence.state['interactions']}")
    print(f"Capabilities emerged: {len(thesidia.capabilities)}")
    print()
    
    if thesidia.intelligence.state['interactions'] == 0:
        print("This is the first interaction. Building from zero...")
        print()
    
    print("Type 'quit' to exit, 'state' to see emergent state, 'save' to save")
    print()
    
    while True:
        question = input("You: ").strip()
        
        if question.lower() == 'quit':
            thesidia.save_state()
            print("State saved. Goodbye.")
            break
        elif question.lower() == 'state':
            state = thesidia.get_emergent_state()
            print("\nEmergent State:")
            print(json.dumps(state, indent=2))
            print()
            continue
        elif question.lower() == 'save':
            thesidia.save_state()
            print("State saved.")
            continue
        elif not question:
            continue
        
        print("\nThesidia (Emergent):")
        response = thesidia.interact(question)
        print(response)
        print()
        
        # Show what emerged
        if thesidia.intelligence.state['interactions'] % 5 == 0:
            print(f"\n[After {thesidia.intelligence.state['interactions']} interactions]")
            print(f"Capabilities: {', '.join(thesidia.capabilities) if thesidia.capabilities else 'Still developing...'}")
            print()

