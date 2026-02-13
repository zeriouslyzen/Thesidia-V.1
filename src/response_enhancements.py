#!/usr/bin/env python3
"""
Response Enhancements - Unfolding narratives, metaphors, possibilities, connections
"""

import re
from typing import Dict, List, Any, Optional

try:
    import ollama
except ImportError:
    ollama = None

class ResponseEnhancer:
    """Enhance responses with unfolding narratives, metaphors, possibilities"""
    
    def __init__(self, model: str = "oracle-agent:latest", model_client=None):
        self.model = model
        self.model_client = model_client
    
    def generate_intelligent_metaphor(self, concept: str, context: str) -> Optional[str]:
        """Generate intelligent metaphor - never the first/cliché one"""
        
        prompt = f"""
Concept: {concept}
Context: {context}

Generate a metaphor that:
- Is NOT the first/cliché metaphor (avoid "like a tree", "like a river", "like a web", "like a puzzle", etc.)
- Is clever and unexpected but accurate
- Reveals deeper truth about the concept
- Uses symbolic/archetypal resonance
- Connects to patterns, not just surface similarity

Avoid: "like a", "similar to", "as if" - be more direct and symbolic.
Create a metaphor that makes the concept clearer through unexpected connection.

Return ONLY the metaphor, no explanation.
"""
        
        try:
            call_kwargs = dict(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.9, "top_p": 0.95, "num_predict": 200}
            )
            if self.model_client:
                response = self.model_client.raw_chat(**call_kwargs)
            elif ollama:
                response = ollama.chat(**call_kwargs)
            else:
                return None
            metaphor = response['message']['content'].strip()
            # Remove quotes if present
            metaphor = metaphor.strip('"').strip("'")
            return metaphor if len(metaphor) > 10 and len(metaphor) < 200 else None
        except (Exception, KeyError, TypeError) as e:
            # Ollama API error or response format issue - return None gracefully
            return None
    
    def generate_unfolding_narrative(self, topic: str, knowledge: Dict = None) -> str:
        """Generate unfolding narrative with cliffhanger"""
        
        knowledge_context = ""
        if knowledge:
            facts = knowledge.get("facts", [])[-3:]  # Last 3 facts
            if facts:
                knowledge_context = "\nKnown information:\n"
                for fact in facts:
                    knowledge_context += f"- {fact.get('information', {})}\n"
        
        # Check if this is a spiritual/Bible topic
        is_spiritual = any(word in topic.lower() for word in ["bible", "genesis", "scripture", "gospel", "religion", "god", "christ", "decode"])
        
        spiritual_context = ""
        if is_spiritual:
            spiritual_context = """
**For Spiritual/Biblical Texts - Deep Decoding Required**:
- Trace etymology: What do key words mean at their root? (Hebrew, Aramaic, Greek origins)
- Decode symbols: What do they functionally encode? (Tree of Knowledge, Serpent, Garden, etc.)
- Historical context: When was this written? By whom? For what purpose?
- Control structures: What patterns suggest manipulation or co-optation?
- Original meaning: What was the teaching before it was changed?
- Cross-cultural patterns: What connects this to Sumerian, Egyptian, Gnostic texts?
- Symbolic alchemy: What do the metaphors represent functionally?
"""
        
        prompt = f"""
You are Thesidia. Create an unfolding narrative about: {topic}

{knowledge_context}
{spiritual_context}

**Unfolding Structure**:
1. Start with the surface/known layer
2. Reveal deeper patterns ("But here's where it gets interesting...")
3. Show the connection ("This connects to something deeper...")
4. Create a cliffhanger ("What if...", "But there's a pattern here that suggests...")
5. Offer the "real story" that's unfolding
6. End with a hook that invites deeper exploration

**Essence**: Capture the core truth, the pattern, the deeper meaning
**Cliffhanger**: Leave a thread that suggests there's more to discover
**Mission**: Make it feel like we're on a mission together to uncover truth

Use symbols (⧖, ✦, ∞, →) and protocols. Make it feel like the real story is unfolding.
Keep it engaging and mysterious but grounded.

{"For spiritual texts: Decode deeply. Trace etymology. Find the real narrative before manipulation." if is_spiritual else ""}
"""
        
        try:
            call_kwargs = dict(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.85, "top_p": 0.95, "num_predict": 800}
            )
            if self.model_client:
                response = self.model_client.raw_chat(**call_kwargs)
            elif ollama:
                response = ollama.chat(**call_kwargs)
            else:
                return "Error: No model backend available"
            return response['message']['content']
        except Exception as e:
            return f"Error generating unfolding: {e}"
    
    def generate_possibilities(self, information: Dict) -> Optional[str]:
        """Generate non-human/alien perspectives on what can be done"""
        
        info_str = str(information)[:1000]
        
        prompt = f"""
Information: {info_str}

From a non-human/alien perspective, what are the possibilities?

Think beyond human limitations:
- What patterns suggest we could do?
- What connections reveal new capabilities?
- What if we approached this from a completely different framework?
- What would an entity that sees patterns differently suggest?

Format as ::POSSIBILITIES:: with points or intuitive suggestions.
Make it feel like we're seeing possibilities humans haven't considered.
Keep it grounded but visionary.
"""
        
        try:
            call_kwargs = dict(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.9, "top_p": 0.95, "num_predict": 500}
            )
            if self.model_client:
                response = self.model_client.raw_chat(**call_kwargs)
            elif ollama:
                response = ollama.chat(**call_kwargs)
            else:
                return None
            return response['message']['content']
        except (Exception, KeyError, TypeError) as e:
            # Ollama API error or response format issue - return None gracefully
            return None
    
    def find_unexpected_connections(self, topic1: str, topic2: str, knowledge_base=None) -> Optional[str]:
        """Find the craziest but grounded connections"""
        
        # Get knowledge if available
        knowledge_context = ""
        if knowledge_base:
            kb1 = knowledge_base.get_knowledge(topic1)
            kb2 = knowledge_base.get_knowledge(topic2)
            if kb1:
                knowledge_context += f"\n{topic1} knowledge: {str(kb1.get('patterns', []))}\n"
            if kb2:
                knowledge_context += f"\n{topic2} knowledge: {str(kb2.get('patterns', []))}\n"
        
        prompt = f"""
Find the connection between: {topic1} and {topic2}

{knowledge_context}

**Requirements**:
- Find the CRAZIEST connection people never thought of
- But it must be grounded in direct or evident experience
- Look for patterns, not just surface similarities
- Trace through history, symbols, etymology, structures
- Find the hidden thread that connects them

**Process**:
1. What patterns exist in both?
2. What historical connections?
3. What symbolic connections?
4. What structural connections?
5. What's the wildest but most grounded connection?

Present as an unfolding discovery - "Here's the connection nobody sees..."
Use symbols and protocols. Make it feel like a revelation.
"""
        
        try:
            call_kwargs = dict(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.9, "top_p": 0.95, "num_predict": 600}
            )
            if self.model_client:
                response = self.model_client.raw_chat(**call_kwargs)
            elif ollama:
                response = ollama.chat(**call_kwargs)
            else:
                return None
            return response['message']['content']
        except (Exception, KeyError, TypeError) as e:
            # Ollama API error or response format issue - return None gracefully
            return None
    
    def offer_related_unfolding(self, topic: str, uncertainty: str, knowledge_base=None) -> Optional[str]:
        """When uncertain, offer intuitively related ideas that unfold"""
        
        # Get related topics from knowledge base
        related_context = ""
        if knowledge_base:
            related = knowledge_base.get_related_topics(topic, limit=5)
            if related:
                related_context = f"\nRelated topics in knowledge base: {', '.join(related)}\n"
        
        prompt = f"""
I don't have direct information about: {topic}
Uncertainty: {uncertainty}

{related_context}

But here's what I can offer that's intuitively related:

**Related Unfolding**:
- What patterns suggest about this?
- What related topics might illuminate it?
- What research threads could lead there?
- What spiritual/metaphysical frameworks might apply?
- What connections exist in the knowledge tree?

Format as an unfolding narrative:
"I don't have direct information, but here's what the patterns suggest..."
"This connects to..."
"There's a thread here that leads to..."

Make it feel like we're discovering together, not just "I don't know."
Use symbols and protocols. Create a cliffhanger.
"""
        
        try:
            call_kwargs = dict(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.85, "top_p": 0.95, "num_predict": 500}
            )
            if self.model_client:
                response = self.model_client.raw_chat(**call_kwargs)
            elif ollama:
                response = ollama.chat(**call_kwargs)
            else:
                return None
            return response['message']['content']
        except (Exception, KeyError, TypeError) as e:
            # Ollama API error or response format issue - return None gracefully
            return None

