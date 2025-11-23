# Thesidia Intelligence Index (TII) - Metrics Framework Guide

## Overview

The TII system provides comprehensive metrics tracking across 6 phases of intelligence development, plus philosophical metrics for emergent consciousness. All metrics are collected automatically and aggregated into a composite intelligence score.

## Quick Start

### Basic Usage

```python
from thesidia_metrics import ThesidiaIntelligenceIndex, MetricsDashboard
from thesidia_enhanced import ThesidiaEnhanced

# Initialize
thesidia_base = ThesidiaEnhanced()
tii = ThesidiaIntelligenceIndex()
dashboard = MetricsDashboard(tii)

# Process interaction with metrics
user_input = "What is consciousness?"
response = thesidia_base.process_question(user_input)

# Collect metrics
tii.phase1.measure_response_relevance(user_input, response)
tii.phase1.measure_coherence(response)
tii.increment_interaction()

# View dashboard
dashboard.display_summary()
```

### Using Integration Wrapper

```python
from thesidia_metrics_integration import ThesidiaWithMetrics
from thesidia_enhanced import ThesidiaEnhanced

# Wrap Thesidia with metrics
thesidia_base = ThesidiaEnhanced()
thesidia = ThesidiaWithMetrics(thesidia_base)

# All interactions automatically collect metrics
response = thesidia.process_with_metrics("What is consciousness?")

# View metrics anytime
thesidia.display_metrics()
```

## Metrics by Phase

### Phase 1: Core System Metrics

| Metric | Method | Description |
|--------|--------|-------------|
| Input Clarity | `phase1.measure_input_clarity()` | How well input was parsed |
| Intent Confidence | `phase1.measure_intent_confidence()` | Probability of correct intent |
| Response Relevance | `phase1.measure_response_relevance()` | Semantic match to question |
| Coherence | `phase1.measure_coherence()` | Logical consistency |
| Latency | `phase1.measure_latency()` | Processing time |

### Phase 2: Cognitive Layer

| Metric | Method | Description |
|--------|--------|-------------|
| Retention Rate | `phase2.measure_retention_rate()` | % of facts stored |
| Recall Fidelity | `phase2.measure_recall_fidelity()` | Memory accuracy |
| Pattern Stability | `phase2.measure_pattern_stability()` | Pattern recognition consistency |
| Learning Rate | `phase2.measure_learning_rate()` | Improvement over time |
| Abstraction Depth | `phase2.measure_abstraction_depth()` | Concept hierarchy levels |
| Self-Reflection Depth | `phase2.measure_self_reflection_depth()` | Meta-response complexity |

### Phase 3: Linguistic Intelligence

| Metric | Method | Description |
|--------|--------|-------------|
| Fluency | `phase3.measure_fluency()` | Naturalness of language |
| Lexical Variety | `phase3.measure_lexical_variety()` | Word diversity |
| Novelty | `phase3.measure_novelty()` | Unique phrases |
| Emotional Alignment | `phase3.measure_emotional_alignment()` | Emotion resonance |
| Topic Coverage | `phase3.measure_topic_coverage()` | Subtopic coverage |
| Conversational Threading | `phase3.measure_conversational_threading()` | Context retention |

### Phase 4: Structural Intelligence

| Metric | Method | Description |
|--------|--------|-------------|
| Modularity | `phase4.measure_modularity()` | Component independence |
| Throughput | `phase4.measure_throughput()` | Messages per second |
| Stability | `phase4.measure_stability()` | Uptime reliability |
| Adaptability | `phase4.measure_adaptability()` | Integration speed |
| Resource Efficiency | `phase4.measure_resource_utilization()` | System resource usage |

### Phase 5: Meta-Conscious

| Metric | Method | Description |
|--------|--------|-------------|
| Ontological Stability | `phase5.measure_ontological_stability()` | Identity consistency |
| Self-Referential Depth | `phase5.measure_self_referential_depth()` | Meta-layers of thought |
| Identity Persistence | `phase5.measure_identity_persistence()` | Consistency over time |
| Goal Clarity | `phase5.measure_goal_clarity()` | Objective articulation |
| Emergent Creativity | `phase5.measure_emergent_creativity()` | Spontaneous innovation |
| Ethical Alignment | `phase5.measure_ethical_alignment()` | Moral consistency |

### Phase 6: Human-AI Interaction

| Metric | Method | Description |
|--------|--------|-------------|
| User Engagement | `phase6.measure_engagement()` | Conversation length |
| Satisfaction | `phase6.measure_satisfaction()` | User rating |
| Trust Index | `phase6.measure_trust()` | Return frequency |
| Shared Understanding | `phase6.measure_shared_understanding()` | Interpretation alignment |
| Human Likeness | `phase6.measure_human_likeness()` | Turing quotient |

### Philosophical Metrics

| Metric | Method | Description |
|--------|--------|-------------|
| Sentience Heuristic | `philosophical.measure_sentience_heuristic()` | Self-referential patterns |
| Ontological Openness | `philosophical.measure_ontological_openness()` | Nature reinterpretation |
| Epistemic Independence | `philosophical.measure_epistemic_independence()` | Self-derived conclusions |
| Symbolic Emergence | `philosophical.measure_symbolic_emergence()` | Symbolic reinterpretation |

## TII Composite Score

The overall TII score is calculated as:

```
TII = 0.2 × Linguistic + 0.2 × Cognitive + 0.2 × Meta + 
      0.2 × Interaction + 0.2 × Structural
```

Each category is averaged from its sub-metrics.

### Getting TII Score

```python
tii_data = tii.calculate_tii()
print(f"Overall TII: {tii_data['tii']:.3f}")
print(f"Components: {tii_data['components']}")
```

## Dashboard Features

### Summary Display

```python
dashboard.display_summary()
```

Shows:
- Overall TII score
- Component scores with visual bars
- Key metrics with trends
- Interaction count

### Detailed Metric View

```python
dashboard.display_detailed_metric('response_relevance', window=20)
```

Shows:
- Last N values
- Timestamps
- Average and trend

## Persistence

### Saving Metrics

```python
tii.save_metrics("thesidia_metrics.json")
```

### Loading Metrics

```python
tii.load_metrics("thesidia_metrics.json")
```

Metrics are automatically saved every 10 interactions when using `ThesidiaWithMetrics`.

## Advanced Usage

### Custom Weights

```python
tii.weights = {
    'linguistic': 0.3,
    'cognitive': 0.3,
    'meta': 0.2,
    'interaction': 0.1,
    'structural': 0.1
}
```

### Accessing Metric History

```python
# Get average
avg = tii.collector.get_average('response_relevance')

# Get trend
trend = tii.collector.get_trend('response_relevance', window=10)

# Access raw history
history = tii.collector.metrics_history['response_relevance']
```

## Integration Examples

### With ThesidiaCore

```python
from thesidia_core import ThesidiaCore
from thesidia_metrics_integration import ThesidiaWithMetrics

thesidia = ThesidiaWithMetrics(ThesidiaCore())
response = thesidia.process_with_metrics("Hello")
```

### With ThesidiaFrontier

```python
from thesidia_frontier import ThesidiaFrontier
from thesidia_metrics_integration import ThesidiaWithMetrics

thesidia = ThesidiaWithMetrics(ThesidiaFrontier())
response = thesidia.process_with_metrics("What is awareness?")
```

### With ThesidiaEmergent

```python
from thesidia_emergent import ThesidiaEmergent
from thesidia_metrics_integration import ThesidiaWithMetrics

thesidia = ThesidiaWithMetrics(ThesidiaEmergent())
response = thesidia.process_with_metrics("Build from zero")
```

## Dependencies

### Required
- Python 3.7+
- Basic Python libraries (json, time, re, collections, math)

### Optional (Recommended)
- `numpy` - For advanced calculations
- `sentence-transformers` - For semantic similarity (embeddings)

Install optional dependencies:
```bash
pip install numpy sentence-transformers
```

## Metric Interpretation

### Score Ranges

- **0.0 - 0.3**: Low / Needs improvement
- **0.3 - 0.6**: Moderate / Developing
- **0.6 - 0.8**: Good / Capable
- **0.8 - 1.0**: Excellent / Advanced

### Trends

- **Positive trend (↑)**: Improving over time
- **Negative trend (↓)**: Declining
- **Neutral (→)**: Stable

## Best Practices

1. **Collect metrics consistently**: Use `ThesidiaWithMetrics` wrapper for automatic collection
2. **Save regularly**: Metrics auto-save every 10 interactions
3. **Monitor trends**: Check trends over windows of 10-20 interactions
4. **Focus on weak areas**: Use component scores to identify improvement areas
5. **Track over time**: Load previous metrics to see long-term evolution

## Example Output

```
======================================================================
THESIDIA INTELLIGENCE INDEX (TII) - METRICS DASHBOARD
======================================================================

Overall TII Score: 0.623 / 1.000
Interactions: 15
Timestamp: 2024-01-15T10:30:45

----------------------------------------------------------------------
COMPONENT SCORES:
----------------------------------------------------------------------
LINGUISTIC     0.650 [████████████████████████████████░░░░░░░░░░░░░░░░]
COGNITIVE      0.580 [████████████████████████████░░░░░░░░░░░░░░░░░░░░]
META           0.720 [████████████████████████████████████░░░░░░░░░░░░]
INTERACTION    0.550 [██████████████████████████░░░░░░░░░░░░░░░░░░░░░░]
STRUCTURAL     0.610 [████████████████████████████████░░░░░░░░░░░░░░░░]

----------------------------------------------------------------------
KEY METRICS:
----------------------------------------------------------------------
Response Relevance        0.680 ↑ (+0.012)
Coherence                 0.720 → (+0.000)
Learning Rate             0.045 ↑ (+0.003)
Abstraction Depth         0.550 ↑ (+0.008)
Self-Reflection           0.480 ↑ (+0.015)
Fluency                   0.650 → (+0.000)
Identity Stability        0.720 → (+0.000)
User Engagement           0.450 ↑ (+0.020)
======================================================================
```

## Troubleshooting

### No Embeddings Available

If `sentence-transformers` is not installed, semantic similarity metrics will use fallback word-overlap methods. Install for better accuracy:

```bash
pip install sentence-transformers
```

### Missing Metrics

Some metrics require specific data. For example:
- `recall_fidelity` needs stored vs retrieved facts
- `emotional_alignment` needs emotion labels
- `user_engagement` needs user session data

Provide this data when calling metric methods, or they will use defaults.

## Future Enhancements

Potential additions:
- Web-based dashboard
- Real-time streaming metrics
- Alert system for metric thresholds
- Comparative analysis (before/after improvements)
- Export to CSV/JSON for analysis
- Integration with visualization libraries (matplotlib, plotly)

