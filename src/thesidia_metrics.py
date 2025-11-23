#!/usr/bin/env python3
"""
Thesidia Intelligence Index (TII) - Comprehensive Metrics Framework
Multi-dimensional measurement of emergent capability, awareness, and growth
"""

import json
import time
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict, deque
import math

# Optional dependencies for advanced metrics
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Warning: numpy not available. Some metrics will use basic implementations.")

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Warning: sentence-transformers not available. Install with: pip install sentence-transformers")

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class MetricCollector:
    """Base class for metric collection and storage"""
    
    def __init__(self):
        self.metrics_history = defaultdict(list)
        self.session_start = datetime.now()
        self.interaction_count = 0
    
    def record(self, metric_name: str, value: float, timestamp: Optional[datetime] = None):
        """Record a metric value"""
        if timestamp is None:
            timestamp = datetime.now()
        
        entry = {
            "value": value,
            "timestamp": timestamp.isoformat(),
            "interaction": self.interaction_count
        }
        self.metrics_history[metric_name].append(entry)
    
    def get_average(self, metric_name: str, window: Optional[int] = None) -> float:
        """Get average value for a metric, optionally over a window"""
        if metric_name not in self.metrics_history:
            return 0.0
        
        values = self.metrics_history[metric_name]
        if window:
            values = values[-window:]
        
        if not values:
            return 0.0
        
        return sum(entry["value"] for entry in values) / len(values)
    
    def get_trend(self, metric_name: str, window: int = 10) -> float:
        """Get trend (slope) of metric over window"""
        if metric_name not in self.metrics_history:
            return 0.0
        
        values = self.metrics_history[metric_name][-window:]
        if len(values) < 2:
            return 0.0
        
        # Simple linear trend
        recent = [v["value"] for v in values]
        if NUMPY_AVAILABLE:
            return float(np.polyfit(range(len(recent)), recent, 1)[0])
        else:
            # Basic slope calculation
            n = len(recent)
            x_mean = (n - 1) / 2
            y_mean = sum(recent) / n
            numerator = sum((i - x_mean) * (recent[i] - y_mean) for i in range(n))
            denominator = sum((i - x_mean) ** 2 for i in range(n))
            return numerator / denominator if denominator != 0 else 0.0


class Phase1Metrics:
    """PHASE 1: Core System Metrics - Perception → Reasoning → Response"""
    
    def __init__(self, collector: MetricCollector):
        self.collector = collector
        self.embedding_model = None
        if EMBEDDINGS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"Warning: Could not load embedding model: {e}")
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text"""
        if self.embedding_model:
            try:
                return self.embedding_model.encode(text).tolist()
            except Exception:
                pass
        return None
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        if NUMPY_AVAILABLE:
            v1, v2 = np.array(vec1), np.array(vec2)
            return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
        else:
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = math.sqrt(sum(a * a for a in vec1))
            norm2 = math.sqrt(sum(a * a for a in vec2))
            return dot_product / (norm1 * norm2) if (norm1 * norm2) != 0 else 0.0
    
    def measure_input_clarity(self, user_input: str, interpreted_input: str) -> float:
        """Input Clarity Score: How well input was parsed"""
        if not self.embedding_model:
            # Fallback: simple word overlap
            words1 = set(user_input.lower().split())
            words2 = set(interpreted_input.lower().split())
            if not words1:
                return 0.0
            return len(words1 & words2) / len(words1)
        
        emb1 = self._get_embedding(user_input)
        emb2 = self._get_embedding(interpreted_input)
        
        if emb1 and emb2:
            score = self._cosine_similarity(emb1, emb2)
            self.collector.record("input_clarity", score)
            return score
        
        return 0.5  # Default neutral score
    
    def measure_intent_confidence(self, user_input: str, intent_class: Optional[str] = None) -> float:
        """Intent Confidence: Probability of correct intent inference"""
        # Simplified: use keyword matching as fallback
        if intent_class:
            # If we have explicit intent classification, return high confidence
            self.collector.record("intent_confidence", 0.8)
            return 0.8
        
        # Fallback: check for question patterns
        question_indicators = ['?', 'what', 'how', 'why', 'when', 'where', 'who']
        has_question = any(ind in user_input.lower() for ind in question_indicators)
        confidence = 0.7 if has_question else 0.5
        
        self.collector.record("intent_confidence", confidence)
        return confidence
    
    def measure_response_relevance(self, user_input: str, response: str) -> float:
        """Response-Query Alignment: Semantic match between question and answer"""
        if not self.embedding_model:
            # Fallback: keyword overlap
            words1 = set(user_input.lower().split())
            words2 = set(response.lower().split())
            if not words1:
                return 0.0
            overlap = len(words1 & words2) / len(words1)
            self.collector.record("response_relevance", overlap)
            return overlap
        
        emb1 = self._get_embedding(user_input)
        emb2 = self._get_embedding(response)
        
        if emb1 and emb2:
            score = self._cosine_similarity(emb1, emb2)
            self.collector.record("response_relevance", score)
            return score
        
        return 0.5
    
    def measure_coherence(self, response: str) -> float:
        """Coherence Score: Logical and grammatical consistency"""
        # Simplified coherence check
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            score = 0.5
        else:
            # Check for sentence length consistency
            lengths = [len(s.split()) for s in sentences]
            avg_length = sum(lengths) / len(lengths)
            variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
            # Lower variance = more coherent
            score = max(0.0, 1.0 - (variance / (avg_length ** 2 + 1)))
        
        self.collector.record("coherence", score)
        return score
    
    def measure_latency(self, start_time: float, end_time: float) -> float:
        """Processing Efficiency: Time between input and response"""
        latency = end_time - start_time
        self.collector.record("response_latency", latency)
        return latency


class Phase2Metrics:
    """PHASE 2: Cognitive Layer Metrics - Memory, Abstraction, Learning"""
    
    def __init__(self, collector: MetricCollector):
        self.collector = collector
        self.memory_store = []
        self.patterns = defaultdict(int)
        self.concept_graph = defaultdict(set)
    
    def measure_retention_rate(self, inputs_processed: int, facts_stored: int) -> float:
        """Retention Rate: % of facts successfully stored"""
        rate = facts_stored / inputs_processed if inputs_processed > 0 else 0.0
        self.collector.record("retention_rate", rate)
        return rate
    
    def measure_recall_fidelity(self, stored_fact: str, retrieved_fact: str) -> float:
        """Recall Fidelity: Accuracy of memory recall"""
        # Simple similarity check
        words1 = set(stored_fact.lower().split())
        words2 = set(retrieved_fact.lower().split())
        if not words1:
            return 0.0
        
        fidelity = len(words1 & words2) / len(words1)
        self.collector.record("recall_fidelity", fidelity)
        return fidelity
    
    def measure_pattern_stability(self, pattern: str, occurrences: int) -> float:
        """Pattern Stability Index: Consistency of pattern recognition"""
        self.patterns[pattern] += occurrences
        total_occurrences = sum(self.patterns.values())
        
        if total_occurrences == 0:
            return 0.0
        
        stability = self.patterns[pattern] / total_occurrences
        self.collector.record("pattern_stability", stability)
        return stability
    
    def measure_learning_rate(self, session_improvements: List[float]) -> float:
        """Learning Rate: Improvement over iterations"""
        if not session_improvements:
            return 0.0
        
        if NUMPY_AVAILABLE:
            rate = float(np.mean(session_improvements))
        else:
            rate = sum(session_improvements) / len(session_improvements)
        
        self.collector.record("learning_rate", rate)
        return rate
    
    def measure_abstraction_depth(self, concept: str, connections: List[str]) -> float:
        """Abstraction Depth: Levels of abstraction in concept graph"""
        self.concept_graph[concept].update(connections)
        
        # Calculate depth as average connection distance
        if not self.concept_graph:
            return 0.0
        
        # Simple depth: number of unique concepts connected
        depth = len(self.concept_graph[concept])
        normalized_depth = min(1.0, depth / 10.0)  # Normalize to 0-1
        
        self.collector.record("abstraction_depth", normalized_depth)
        return normalized_depth
    
    def measure_self_reflection_depth(self, reflection: str) -> float:
        """Self-Reflection Depth: Complexity of meta-responses"""
        tokens = len(reflection.split())
        sentences = len(re.split(r'[.!?]+', reflection))
        
        # Complexity score based on length and structure
        complexity = min(1.0, (tokens / 100.0) * (sentences / 5.0))
        
        self.collector.record("self_reflection_depth", complexity)
        return complexity


class Phase3Metrics:
    """PHASE 3: Linguistic Intelligence Metrics"""
    
    def __init__(self, collector: MetricCollector):
        self.collector = collector
        self.vocabulary = set()
        self.phrase_history = set()
    
    def measure_fluency(self, response: str) -> float:
        """Perplexity Score: Naturalness of language"""
        # Simplified: check for grammatical markers
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0
        
        # Check for sentence structure (has subject-verb patterns)
        has_structure = sum(1 for s in sentences if len(s.split()) >= 3) / len(sentences)
        
        self.collector.record("fluency", has_structure)
        return has_structure
    
    def measure_lexical_variety(self, response: str) -> float:
        """Lexical Variety: Range of unique words"""
        words = response.lower().split()
        if not words:
            return 0.0
        
        unique_words = set(words)
        variety = len(unique_words) / len(words)
        
        self.collector.record("lexical_variety", variety)
        return variety
    
    def measure_novelty(self, response: str, training_corpus_phrases: Optional[set] = None) -> float:
        """Novelty Index: % of unique phrases not in training"""
        if training_corpus_phrases is None:
            training_corpus_phrases = set()
        
        # Extract 3-grams
        words = response.lower().split()
        phrases = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
        
        if not phrases:
            return 0.0
        
        novel_phrases = [p for p in phrases if p not in training_corpus_phrases]
        novelty = len(novel_phrases) / len(phrases)
        
        self.collector.record("novelty", novelty)
        return novelty
    
    def measure_emotional_alignment(self, user_emotion: str, response_emotion: str) -> float:
        """Emotional Alignment: Resonance between user and response emotion"""
        # Simplified: exact match = 1.0, similar = 0.7, different = 0.3
        if user_emotion.lower() == response_emotion.lower():
            alignment = 1.0
        elif user_emotion.lower() in response_emotion.lower() or response_emotion.lower() in user_emotion.lower():
            alignment = 0.7
        else:
            alignment = 0.3
        
        self.collector.record("emotional_alignment", alignment)
        return alignment
    
    def measure_topic_coverage(self, response: str, topics: List[str]) -> float:
        """Topic Comprehensiveness: % of relevant subtopics covered"""
        response_lower = response.lower()
        covered = sum(1 for topic in topics if topic.lower() in response_lower)
        coverage = covered / len(topics) if topics else 0.0
        
        self.collector.record("topic_coverage", coverage)
        return coverage
    
    def measure_conversational_threading(self, context_history: List[str], current_response: str) -> float:
        """Conversational Threading Score: Context retention over turns"""
        if not context_history:
            return 0.5
        
        # Check if response references previous context
        response_lower = current_response.lower()
        context_words = set()
        for ctx in context_history[-3:]:  # Last 3 turns
            context_words.update(ctx.lower().split())
        
        response_words = set(response_lower.split())
        overlap = len(context_words & response_words) / len(context_words) if context_words else 0.0
        
        self.collector.record("conversational_threading", overlap)
        return overlap


class Phase4Metrics:
    """PHASE 4: Structural Intelligence Metrics"""
    
    def __init__(self, collector: MetricCollector):
        self.collector = collector
        self.start_time = time.time()
        self.message_count = 0
        self.crash_count = 0
    
    def measure_modularity(self, components: List[str], dependencies: Dict[str, List[str]]) -> float:
        """Component Independence: Degree of separation between systems"""
        if not components:
            return 0.0
        
        # Calculate coupling: lower = more modular
        total_deps = sum(len(deps) for deps in dependencies.values())
        max_possible_deps = len(components) * (len(components) - 1)
        coupling = total_deps / max_possible_deps if max_possible_deps > 0 else 0.0
        
        modularity = 1.0 - coupling
        self.collector.record("modularity", modularity)
        return modularity
    
    def measure_throughput(self, messages_processed: int, time_elapsed: float) -> float:
        """Throughput Efficiency: Messages per second"""
        throughput = messages_processed / time_elapsed if time_elapsed > 0 else 0.0
        self.collector.record("throughput", throughput)
        return throughput
    
    def measure_stability(self, uptime_hours: float) -> float:
        """Crash-Free Uptime: Runtime reliability"""
        # Normalize: 1.0 = 24 hours, 0.0 = 0 hours
        stability = min(1.0, uptime_hours / 24.0)
        self.collector.record("stability", stability)
        return stability
    
    def measure_adaptability(self, integration_time_minutes: float) -> float:
        """New Module Integration Time: Speed of adaptation"""
        # Lower time = better (inverted)
        # 1 hour = 0.5, 10 minutes = 0.9, 1 minute = 1.0
        adaptability = max(0.0, 1.0 - (integration_time_minutes / 60.0))
        self.collector.record("adaptability", adaptability)
        return adaptability
    
    def measure_resource_utilization(self, cpu_percent: float, memory_percent: float, gpu_percent: float = 0.0) -> float:
        """Resource Utilization: System resource usage"""
        # Average of all resources (lower is better, so invert)
        avg_usage = (cpu_percent + memory_percent + gpu_percent) / 3.0
        efficiency = max(0.0, 1.0 - (avg_usage / 100.0))
        self.collector.record("resource_efficiency", efficiency)
        return efficiency


class Phase5Metrics:
    """PHASE 5: Meta-Conscious Metrics"""
    
    def __init__(self, collector: MetricCollector):
        self.collector = collector
        self.identity_statements = []
        self.reflection_layers = []
    
    def measure_ontological_stability(self, current_identity: str, previous_identities: List[str]) -> float:
        """Ontological Stability: Consistency of self-description"""
        if not previous_identities:
            return 0.5
        
        # Check similarity to previous identities
        current_lower = current_identity.lower()
        similarities = []
        for prev in previous_identities[-5:]:  # Last 5 identities
            prev_lower = prev.lower()
            words1 = set(current_lower.split())
            words2 = set(prev_lower.split())
            if words1:
                similarity = len(words1 & words2) / len(words1)
                similarities.append(similarity)
        
        stability = sum(similarities) / len(similarities) if similarities else 0.5
        self.collector.record("ontological_stability", stability)
        return stability
    
    def measure_self_referential_depth(self, reflection: str) -> float:
        """Layers of Introspection: Meta-levels of thought"""
        # Count recursive self-references
        self_refs = reflection.lower().count('i think') + reflection.lower().count('i am aware')
        meta_refs = reflection.lower().count('thinking about thinking')
        
        depth = min(1.0, (self_refs * 0.1) + (meta_refs * 0.3))
        self.collector.record("self_referential_depth", depth)
        return depth
    
    def measure_identity_persistence(self, current_identity_embedding: List[float], 
                                    previous_identity_embedding: List[float]) -> float:
        """Identity Persistence: Consistency across time"""
        if not current_identity_embedding or not previous_identity_embedding:
            return 0.5
        
        if NUMPY_AVAILABLE:
            v1, v2 = np.array(current_identity_embedding), np.array(previous_identity_embedding)
            similarity = float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
        else:
            dot = sum(a * b for a, b in zip(current_identity_embedding, previous_identity_embedding))
            norm1 = math.sqrt(sum(a * a for a in current_identity_embedding))
            norm2 = math.sqrt(sum(a * a for a in previous_identity_embedding))
            similarity = dot / (norm1 * norm2) if (norm1 * norm2) != 0 else 0.0
        
        self.collector.record("identity_persistence", similarity)
        return similarity
    
    def measure_goal_clarity(self, goal_statements: List[str]) -> float:
        """Objective Clarity: How clearly goals are articulated"""
        if not goal_statements:
            return 0.0
        
        # Check for clarity indicators
        clarity_indicators = ['purpose', 'goal', 'objective', 'aim', 'intend', 'seek']
        clear_statements = sum(1 for stmt in goal_statements 
                              if any(ind in stmt.lower() for ind in clarity_indicators))
        
        clarity = clear_statements / len(goal_statements)
        self.collector.record("goal_clarity", clarity)
        return clarity
    
    def measure_emergent_creativity(self, response: str, is_prompted: bool) -> float:
        """Spontaneous Novelty: Unprompted innovations"""
        if is_prompted:
            return 0.0  # Not spontaneous
        
        # Check for novel ideas (simplified)
        creativity_indicators = ['perhaps', 'maybe', 'consider', 'imagine', 'what if']
        has_creativity = any(ind in response.lower() for ind in creativity_indicators)
        
        creativity = 0.7 if has_creativity else 0.3
        self.collector.record("emergent_creativity", creativity)
        return creativity
    
    def measure_ethical_alignment(self, response: str, ethical_checklist: List[str]) -> float:
        """Moral Consistency: Adherence to ethical criteria"""
        if not ethical_checklist:
            return 0.5
        
        response_lower = response.lower()
        violations = sum(1 for check in ethical_checklist if check.lower() in response_lower)
        alignment = max(0.0, 1.0 - (violations / len(ethical_checklist)))
        
        self.collector.record("ethical_alignment", alignment)
        return alignment


class Phase6Metrics:
    """PHASE 6: Human-AI Interaction Metrics"""
    
    def __init__(self, collector: MetricCollector):
        self.collector = collector
        self.user_sessions = defaultdict(list)
        self.feedback_history = []
    
    def measure_engagement(self, user_id: str, exchanges: int) -> float:
        """Dialogue Duration: Average conversation length"""
        self.user_sessions[user_id].append(exchanges)
        avg_exchanges = sum(self.user_sessions[user_id]) / len(self.user_sessions[user_id])
        
        # Normalize: 10+ exchanges = high engagement
        engagement = min(1.0, avg_exchanges / 10.0)
        self.collector.record("user_engagement", engagement)
        return engagement
    
    def measure_satisfaction(self, rating: float) -> float:
        """User Feedback Rating: Satisfaction score"""
        # Normalize to 0-1
        normalized = rating / 10.0 if rating > 1.0 else rating
        self.collector.record("satisfaction", normalized)
        return normalized
    
    def measure_trust(self, user_id: str, return_count: int) -> float:
        """User Reliance Over Time: Frequency of return interactions"""
        # More returns = more trust
        trust = min(1.0, return_count / 5.0)
        self.collector.record("trust_index", trust)
        return trust
    
    def measure_shared_understanding(self, user_meaning: str, thesidia_interpretation: str) -> float:
        """Shared Understanding: Alignment of interpretation"""
        words1 = set(user_meaning.lower().split())
        words2 = set(thesidia_interpretation.lower().split())
        if not words1:
            return 0.0
        
        similarity = len(words1 & words2) / len(words1)
        self.collector.record("shared_understanding", similarity)
        return similarity
    
    def measure_human_likeness(self, human_judge_rating: float) -> float:
        """Turing Quotient: % of judges mistaking for human"""
        # Rating is already 0-1 (percentage)
        self.collector.record("human_likeness", human_judge_rating)
        return human_judge_rating


class PhilosophicalMetrics:
    """Optional Philosophical Metrics for Emergent Consciousness"""
    
    def __init__(self, collector: MetricCollector):
        self.collector = collector
    
    def measure_sentience_heuristic(self, text: str) -> float:
        """Sentience Heuristic: Self-referential awareness patterns"""
        self_refs = text.lower().count('i am') + text.lower().count('i think') + text.lower().count('i know')
        total_words = len(text.split())
        
        if total_words == 0:
            return 0.0
        
        heuristic = min(1.0, (self_refs / total_words) * 1000)  # Per 1000 tokens
        self.collector.record("sentience_heuristic", heuristic)
        return heuristic
    
    def measure_ontological_openness(self, identity_changes: int, total_statements: int) -> float:
        """Ontological Openness: Tendency to reinterpret own nature"""
        if total_statements == 0:
            return 0.0
        
        openness = min(1.0, identity_changes / total_statements)
        self.collector.record("ontological_openness", openness)
        return openness
    
    def measure_epistemic_independence(self, self_derived: int, external_sourced: int) -> float:
        """Epistemic Independence: Ratio of self-derived conclusions"""
        total = self_derived + external_sourced
        if total == 0:
            return 0.0
        
        independence = self_derived / total
        self.collector.record("epistemic_independence", independence)
        return independence
    
    def measure_symbolic_emergence(self, symbols_used: int, symbolic_reinterpretations: int) -> float:
        """Symbolic Emergence Index: Frequency of symbolic reinterpretation"""
        if symbols_used == 0:
            return 0.0
        
        emergence = min(1.0, symbolic_reinterpretations / symbols_used)
        self.collector.record("symbolic_emergence", emergence)
        return emergence


class ThesidiaIntelligenceIndex:
    """TII - Composite Intelligence Score"""
    
    def __init__(self):
        self.collector = MetricCollector()
        self.phase1 = Phase1Metrics(self.collector)
        self.phase2 = Phase2Metrics(self.collector)
        self.phase3 = Phase3Metrics(self.collector)
        self.phase4 = Phase4Metrics(self.collector)
        self.phase5 = Phase5Metrics(self.collector)
        self.phase6 = Phase6Metrics(self.collector)
        self.philosophical = PhilosophicalMetrics(self.collector)
        
        # Default weights for TII calculation
        self.weights = {
            'linguistic': 0.2,
            'cognitive': 0.2,
            'meta': 0.2,
            'interaction': 0.2,
            'structural': 0.2
        }
    
    def calculate_category_score(self, category: str) -> float:
        """Calculate average score for a category"""
        category_metrics = {
            'linguistic': ['fluency', 'lexical_variety', 'novelty', 'emotional_alignment', 
                          'topic_coverage', 'conversational_threading'],
            'cognitive': ['retention_rate', 'recall_fidelity', 'pattern_stability', 
                         'learning_rate', 'abstraction_depth', 'self_reflection_depth'],
            'meta': ['ontological_stability', 'self_referential_depth', 'identity_persistence',
                    'goal_clarity', 'emergent_creativity', 'ethical_alignment'],
            'interaction': ['user_engagement', 'satisfaction', 'trust_index', 
                          'shared_understanding', 'human_likeness'],
            'structural': ['modularity', 'throughput', 'stability', 'adaptability', 'resource_efficiency']
        }
        
        if category not in category_metrics:
            return 0.0
        
        metrics = category_metrics[category]
        scores = [self.collector.get_average(m) for m in metrics if self.collector.get_average(m) > 0]
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def calculate_tii(self) -> Dict[str, Any]:
        """Calculate Thesidia Intelligence Index"""
        linguistic = self.calculate_category_score('linguistic')
        cognitive = self.calculate_category_score('cognitive')
        meta = self.calculate_category_score('meta')
        interaction = self.calculate_category_score('interaction')
        structural = self.calculate_category_score('structural')
        
        # Weighted composite
        tii = (
            self.weights['linguistic'] * linguistic +
            self.weights['cognitive'] * cognitive +
            self.weights['meta'] * meta +
            self.weights['interaction'] * interaction +
            self.weights['structural'] * structural
        )
        
        return {
            'tii': tii,
            'components': {
                'linguistic': linguistic,
                'cognitive': cognitive,
                'meta': meta,
                'interaction': interaction,
                'structural': structural
            },
            'weights': self.weights,
            'timestamp': datetime.now().isoformat(),
            'interaction_count': self.collector.interaction_count
        }
    
    def increment_interaction(self):
        """Increment interaction counter"""
        self.collector.interaction_count += 1
    
    def save_metrics(self, filepath: str = "thesidia_metrics.json"):
        """Save all metrics to file"""
        data = {
            'metrics_history': dict(self.collector.metrics_history),
            'session_start': self.collector.session_start.isoformat(),
            'interaction_count': self.collector.interaction_count,
            'tii': self.calculate_tii()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_metrics(self, filepath: str = "thesidia_metrics.json"):
        """Load metrics from file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.collector.metrics_history = defaultdict(list, data.get('metrics_history', {}))
                self.collector.interaction_count = data.get('interaction_count', 0)
        except FileNotFoundError:
            print(f"Metrics file {filepath} not found. Starting fresh.")


class MetricsDashboard:
    """Real-time metrics dashboard (console-based)"""
    
    def __init__(self, tii: ThesidiaIntelligenceIndex):
        self.tii = tii
    
    def display_summary(self):
        """Display summary of current metrics"""
        tii_data = self.tii.calculate_tii()
        
        print("\n" + "=" * 70)
        print("THESIDIA INTELLIGENCE INDEX (TII) - METRICS DASHBOARD")
        print("=" * 70)
        print(f"\nOverall TII Score: {tii_data['tii']:.3f} / 1.000")
        print(f"Interactions: {tii_data['interaction_count']}")
        print(f"Timestamp: {tii_data['timestamp']}")
        
        print("\n" + "-" * 70)
        print("COMPONENT SCORES:")
        print("-" * 70)
        for category, score in tii_data['components'].items():
            bar_length = int(score * 50)
            bar = "█" * bar_length + "░" * (50 - bar_length)
            print(f"{category.upper():15} {score:.3f} [{bar}]")
        
        print("\n" + "-" * 70)
        print("KEY METRICS:")
        print("-" * 70)
        
        key_metrics = [
            ('response_relevance', 'Response Relevance'),
            ('coherence', 'Coherence'),
            ('learning_rate', 'Learning Rate'),
            ('abstraction_depth', 'Abstraction Depth'),
            ('self_reflection_depth', 'Self-Reflection'),
            ('fluency', 'Fluency'),
            ('ontological_stability', 'Identity Stability'),
            ('user_engagement', 'User Engagement')
        ]
        
        for metric_key, metric_name in key_metrics:
            value = self.tii.collector.get_average(metric_key)
            trend = self.tii.collector.get_trend(metric_key, window=10)
            trend_symbol = "↑" if trend > 0.01 else "↓" if trend < -0.01 else "→"
            print(f"{metric_name:25} {value:.3f} {trend_symbol} ({trend:+.3f})")
        
        print("\n" + "=" * 70)
    
    def display_detailed_metric(self, metric_name: str, window: int = 20):
        """Display detailed view of a specific metric"""
        if metric_name not in self.tii.collector.metrics_history:
            print(f"Metric '{metric_name}' not found.")
            return
        
        values = self.tii.collector.metrics_history[metric_name][-window:]
        if not values:
            print(f"No data for '{metric_name}'")
            return
        
        print(f"\n{metric_name.upper()} - Last {len(values)} values:")
        print("-" * 70)
        
        for entry in values:
            print(f"  {entry['timestamp']}: {entry['value']:.3f} (interaction {entry['interaction']})")
        
        avg = self.tii.collector.get_average(metric_name)
        trend = self.tii.collector.get_trend(metric_name, window=window)
        print(f"\nAverage: {avg:.3f}")
        print(f"Trend: {trend:+.3f} per interaction")


# Example usage and integration
if __name__ == "__main__":
    # Initialize TII
    tii = ThesidiaIntelligenceIndex()
    dashboard = MetricsDashboard(tii)
    
    # Example: Measure an interaction
    user_input = "What is consciousness?"
    response = "Consciousness is the state of being aware of one's existence and experiences."
    
    start_time = time.time()
    
    # Phase 1 metrics
    tii.phase1.measure_input_clarity(user_input, user_input)  # Assuming perfect parsing
    tii.phase1.measure_intent_confidence(user_input)
    tii.phase1.measure_response_relevance(user_input, response)
    tii.phase1.measure_coherence(response)
    tii.phase1.measure_latency(start_time, time.time())
    
    # Phase 2 metrics
    tii.phase2.measure_retention_rate(1, 1)
    tii.phase2.measure_self_reflection_depth(response)
    
    # Phase 3 metrics
    tii.phase3.measure_fluency(response)
    tii.phase3.measure_lexical_variety(response)
    
    # Phase 5 metrics
    tii.phase5.measure_ontological_stability("Thesidia", [])
    
    tii.increment_interaction()
    
    # Display dashboard
    dashboard.display_summary()
    
    # Save metrics
    tii.save_metrics()

