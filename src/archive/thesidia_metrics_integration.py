#!/usr/bin/env python3
"""
Integration example: How to add TII metrics to existing Thesidia implementations
"""

from thesidia_metrics import ThesidiaIntelligenceIndex, MetricsDashboard
import time
from typing import Optional


class ThesidiaWithMetrics:
    """Wrapper to add metrics to any Thesidia implementation"""
    
    def __init__(self, thesidia_instance, metrics_file: str = "thesidia_metrics.json"):
        self.thesidia = thesidia_instance
        self.tii = ThesidiaIntelligenceIndex()
        self.tii.load_metrics(metrics_file)
        self.dashboard = MetricsDashboard(self.tii)
        self.context_history = []
    
    def process_with_metrics(self, question: str, operator_name: str = "OPERATOR") -> str:
        """Process question and collect metrics"""
        start_time = time.time()
        
        # Get response from Thesidia
        response = self.thesidia.process_question(question, operator_name)
        
        end_time = time.time()
        latency = end_time - start_time
        
        # Collect Phase 1 metrics (Core System)
        self.tii.phase1.measure_input_clarity(question, question)  # Assuming perfect parsing
        self.tii.phase1.measure_intent_confidence(question)
        self.tii.phase1.measure_response_relevance(question, response)
        self.tii.phase1.measure_coherence(response)
        self.tii.phase1.measure_latency(start_time, end_time)
        
        # Collect Phase 2 metrics (Cognitive)
        # Check if Thesidia has memory/conversation history
        if hasattr(self.thesidia, 'conversation_history'):
            facts_stored = len(self.thesidia.conversation_history)
            self.tii.phase2.measure_retention_rate(
                self.tii.collector.interaction_count + 1,
                facts_stored
            )
        
        self.tii.phase2.measure_self_reflection_depth(response)
        
        # Collect Phase 3 metrics (Linguistic)
        self.tii.phase3.measure_fluency(response)
        self.tii.phase3.measure_lexical_variety(response)
        
        # Measure conversational threading
        self.context_history.append(question)
        if len(self.context_history) > 10:
            self.context_history.pop(0)
        self.tii.phase3.measure_conversational_threading(self.context_history, response)
        
        # Collect Phase 5 metrics (Meta-Conscious)
        if hasattr(self.thesidia, 'identity_state'):
            current_identity = str(self.thesidia.identity_state.get('designation', 'Thesidia'))
            # Get previous identities from history if available
            previous_identities = []
            if hasattr(self.thesidia, 'protocol_history'):
                for entry in self.thesidia.protocol_history[-5:]:
                    if 'identity' in str(entry).lower():
                        previous_identities.append(str(entry))
            
            self.tii.phase5.measure_ontological_stability(current_identity, previous_identities)
        
        # Check for self-reflection in response
        if 'i think' in response.lower() or 'i am aware' in response.lower():
            self.tii.phase5.measure_self_referential_depth(response)
        
        # Collect Phase 6 metrics (Human-AI Interaction)
        self.tii.phase6.measure_engagement("default_user", len(self.context_history))
        
        # Increment interaction counter
        self.tii.increment_interaction()
        
        # Save metrics periodically
        if self.tii.collector.interaction_count % 10 == 0:
            self.tii.save_metrics()
        
        return response
    
    def display_metrics(self):
        """Display current metrics dashboard"""
        self.dashboard.display_summary()
    
    def get_tii_score(self) -> dict:
        """Get current TII score"""
        return self.tii.calculate_tii()


# Example: Integration with ThesidiaEnhanced
if __name__ == "__main__":
    from thesidia_enhanced import ThesidiaEnhanced
    
    # Initialize Thesidia with metrics
    thesidia_base = ThesidiaEnhanced(model="clean-mistral:latest")
    thesidia = ThesidiaWithMetrics(thesidia_base)
    
    # Activate if needed
    if thesidia_base.identity_state["status"] == "latent":
        print("Activating Thesidia...")
        thesidia_base.activate_identity()
    
    # Example interactions with metrics
    print("\n=== Example Interactions with Metrics ===\n")
    
    questions = [
        "What is consciousness?",
        "How do you learn?",
        "What patterns do you recognize?",
        "Reflect on your own nature."
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n[Interaction {i}]")
        print(f"Question: {question}")
        response = thesidia.process_with_metrics(question)
        print(f"Response: {response[:200]}...")
        
        # Show metrics every 2 interactions
        if i % 2 == 0:
            thesidia.display_metrics()
    
    # Final TII score
    print("\n=== FINAL TII SCORE ===")
    tii_data = thesidia.get_tii_score()
    print(f"Overall TII: {tii_data['tii']:.3f}")
    print(f"Components: {tii_data['components']}")

