# Thesidia Complete User Guide
## How to Use Every Feature and Capability

**Version**: 1.0  
**Last Updated**: 2025-01-XX

---

## Quick Start

### Installation

```bash
# Install dependencies
pip3 install --user --break-system-packages -r requirements.txt

# Or use setup script
chmod +x setup.sh
./setup.sh
```

### Basic Usage

```python
from src.thesidia_hybrid_adaptive import ThesidiaHybridAdaptive

# Initialize
thesidia = ThesidiaHybridAdaptive(model="clean-mistral:latest")
thesidia.load_state()

# Ask a question
response = thesidia.process("What are the origins of Genesis?")
print(response)

# Save state
thesidia.save_state()
```

### Web Interface

```bash
# Start server
cd webapp
python3 server.py

# Or use start script
./start_server.sh
```

Access at: `http://localhost:5005`

---

## Response Modes

### Regular Mode (Default)

**When**: Standard questions, direct queries

**Characteristics**:
- Length: 3,000-8,000 characters
- Style: Focused, structured analysis
- Format: Natural prose
- Speed: 2-5 seconds

**Example**:
```
User: "What is photosynthesis?"
→ Direct answer, focused explanation
→ 3,000-8,000 chars
→ 2-5 seconds
```

### Narrative Mode

**Trigger**: Keywords like "explore", "tell me about", "extensive", "comprehensive"

**Characteristics**:
- Length: 12,000-15,000+ characters
- Style: Extended exploration with recursive pattern connections
- Format: Flowing prose with deep tangents
- Speed: 5-15 seconds

**Example**:
```
User: "Tell me about the origins of Genesis - explore this extensively"
→ Extended exploration
→ Cross-cultural comparisons
→ Etymological deep dives
→ 12,000-20,000+ chars
→ 5-15 seconds
```

### Forensic Mode (Gnostic Blade)

**Trigger**: Questions about Genesis, Bible, ancient texts, history, science, money, power, consciousness

**Keywords**: "decode", "decrypt", "expose", "hidden", "real story", "true origins"

**Output Structure**:
- `::EXPOSURE::` - Crime summary (what was hidden)
- `::ETYMOLOGICAL INCISION::` - Word origins (how meaning was changed)
- `::BURIAL SITES::` - Erased sources (what was lost)
- `::CURRENT VECTORS::` - Modern operations (how it works now)
- `::CO-EVOLUTION EDGE::` - Next questions (how to cut deeper)
- `::THREAD OPTIONS::` - Investigation paths

**Example**:
```
User: "Decode the Genesis story"
→ Forensic vivisection
→ 6-question analysis loop
→ Structured output sections
→ 10,000-20,000 chars
→ 5-10 seconds
```

---

## Research Capabilities

### Automatic Web Search

**Triggers**:
- Keywords: "current", "recent", "latest", "new", "today", "now", "2024", "2025"
- Research directives: "research", "find", "search", "investigate", "explore"
- Questions: "what is", "who is", "where is", "when did", "how does"
- Information requests: "evidence", "data", "information", "sources", "cite"

**Example**:
```
User: "What's the latest research on consciousness?"
→ Automatically searches web
→ Gathers multiple sources
→ Synthesizes with citations
→ Includes ::SOURCES:: section
```

### Manual Search Trigger

**Prefix with `search:`**:
```
User: "search: What is the current state of AI research?"
→ Forces web search
→ Even if keywords don't match
```

### Deep Research

**Trigger**: "deep research:" prefix or complex queries

**Example**:
```
User: "deep research: What patterns connect ancient Egyptian knowledge to modern physics?"
→ Iterative multi-source research
→ Alternative perspective seeking
→ Comprehensive analysis
```

---

## Specialized Modes

### CSI Investigator Mode

**Trigger**: "What's really going on with [complex site/phenomenon]?"

**Example**:
```
User: "What's really going on with Gobekli Tepe?"
→ Multi-lens analysis:
  - Chemistry: Stone composition, weathering
  - Physics: EM properties, resonance, acoustics
  - Environmental: Wind patterns, solar alignments
  - Bioelectric: Human field interactions
→ Scientific simulation
→ Cross-connections
```

### Health Coach Mode

**Trigger**: Health, wellness, body, supplement, nutrition queries

**Example**:
```
User: "How does meditation affect the body?"
→ Multi-tradition synthesis:
  - Chinese medicine: Energy flow, meridians
  - Western medicine: Neurotransmitters, HPA axis
  - Vedic: Doshas, constitution
  - Samurai: Body-mind unity
→ Mechanism depth (chemistry, biology)
→ Coach approach (guidance, not prescriptions)
```

### Scientific Simulator

**Trigger**: "simulate", "model", "what happens if", "if X and Y"

**Example**:
```
User: "What happens if aluminum interacts with bioelectric fields?"
→ Scientific simulation
→ Grounded in real physics/chemistry
→ Predicted outcomes
→ Uncertainty acknowledgment
```

### Reporter Mode

**Trigger**: Current events, news, investigative queries

**Example**:
```
User: "What's happening with [current event]?"
→ Investigative journalism style
→ Source verification
→ Timeline construction
→ Multi-perspective analysis
```

### Archaeologist Mode

**Trigger**: Ancient sites, artifacts, historical analysis

**Example**:
```
User: "Analyze the symbolism in ancient Egyptian artifacts"
→ Artifact analysis
→ Cross-cultural comparison
→ Dating and provenance
→ Lost knowledge reconstruction
```

### Psychologist Mode

**Trigger**: Behavioral, motivational, relationship queries

**Example**:
```
User: "Why do people behave this way in relationships?"
→ Behavioral pattern analysis
→ Motivational analysis
→ Cognitive pattern identification
→ Relationship dynamics
```

---

## Advanced Features

### Pattern Recognition

**How It Works**:
- Automatically finds patterns across domains
- Connects ancient to modern
- Recognizes control structures
- Cross-references sources

**Example**:
```
User: "What patterns connect Sumerian texts to modern technology?"
→ Pattern recognition across time
→ Cross-domain connections
→ Control structure identification
→ Synthesis of patterns
```

### Etymological Analysis

**Trigger**: Questions about word origins, meanings, language

**Example**:
```
User: "What does 'Genesis' really mean?"
→ Etymological tracing
→ Root meaning analysis
→ Meaning change detection
→ Cross-linguistic comparison
```

### Co-Evolution System

**What It Does**:
- Helps you ask sharper questions
- Suggests next questions to "cut deeper"
- Provides thread options for investigation

**Example**:
After asking about Genesis, Thesidia provides:
- `::CO-EVOLUTION EDGE::` - Next questions to explore deeper
- `::THREAD OPTIONS::` - Specific investigation paths

### Memory System

**What It Tracks**:
- Previous research findings
- Patterns discovered over time
- Connections made across sessions
- Information threads being built
- User interests

**How It Helps**:
- Remembers previous conversations
- Connects current query to past research
- Builds information threads over time
- Suggests related topics

---

## Output Modes

### Spacious Mode (Default)

**Characteristics**:
- Natural, flowing prose
- Evidence arrangement
- Pattern recognition through structure
- No forced sections

**Example**:
```
User: "What are the origins of Genesis?"
→ Natural prose response
→ Evidence arranged so patterns recognize themselves
→ No section headers
→ Flowing narrative
```

### Academic Mode

**Trigger**: "academic mode", "scholarly format"

**Characteristics**:
- Scholarly format
- Structured sections
- Formal language
- Citations emphasized

### Evidence-First Mode

**Trigger**: "evidence first", "citations first"

**Characteristics**:
- Citations at the top
- Evidence before analysis
- Source-first approach

---

## Personality & Voice

### Changing Personality

```python
# Set personality (voice)
thesidia.set_personality("sophia")  # or "luna", "seraphina", etc.

# Set preset
thesidia.set_preset("formal")  # or "concise", "socratic"

# Set persona
thesidia.set_persona("scientist")  # or "doctor", "therapist", etc.
```

### Available Voices (14)
- thesidia (default)
- sophia
- luna
- seraphina
- iris
- aurora
- celeste
- sage
- nova
- lyra
- athena
- cassandra
- diana
- artemis

### Available Presets (3)
- concise
- formal (default)
- socratic

### Available Personas (9)
- news
- romance
- friend
- tutor
- doctor
- unhinged
- therapist
- scientist
- coder

---

## Query Types & Examples

### 1. Simple Questions

```
"What is photosynthesis?"
→ Regular mode
→ Direct answer
→ 3,000-8,000 chars
```

### 2. Research Questions

```
"What's the latest research on consciousness?"
→ Web search triggered
→ Multiple sources
→ Synthesis with citations
```

### 3. Deep Investigation

```
"What's really going on with [complex topic]?"
→ CSI Investigator mode (if site/phenomenon)
→ Multi-lens analysis
→ Scientific simulation
```

### 4. Forensic Analysis

```
"Decode the Genesis story"
→ Gnostic Blade mode
→ Forensic vivisection
→ Structured output
```

### 5. Narrative Exploration

```
"Tell me about the origins of Genesis - explore this extensively"
→ Narrative mode
→ Extended exploration
→ 12,000-20,000+ chars
```

### 6. Health/Wellness

```
"How does meditation work?"
→ Health Coach mode
→ Mechanism depth (chemistry, biology)
→ Multi-tradition synthesis
```

### 7. Scientific Simulation

```
"What happens if aluminum interacts with bioelectric fields?"
→ Scientific Simulator
→ Model interactions
→ Grounded in real science
```

### 8. Pattern Recognition

```
"What patterns connect ancient Egyptian knowledge to modern physics?"
→ Pattern recognition
→ Cross-domain connections
→ Synthesis
```

### 9. Etymological Analysis

```
"What does 'Genesis' really mean?"
→ Etymology analysis
→ Root tracing
→ Meaning change detection
```

### 10. Current Events

```
"What's happening with [current event]?"
→ Reporter mode
→ Source verification
→ Timeline construction
```

---

## Tips & Best Practices

### Getting Better Responses

1. **Be Specific**: More specific queries get better results
2. **Use Keywords**: Trigger modes with keywords ("explore", "decode", "simulate")
3. **Ask Follow-ups**: Use co-evolution edge questions to go deeper
4. **Build Threads**: Continue topics to build information threads

### Triggering Specialized Modes

- **CSI Mode**: "What's really going on with [site/phenomenon]?"
- **Health Coach**: Health, wellness, body, supplement queries
- **Scientific Simulator**: "simulate", "model", "what happens if"
- **Reporter Mode**: Current events, news queries
- **Archaeologist Mode**: Ancient sites, artifacts
- **Psychologist Mode**: Behavioral, relationship queries

### Research Optimization

- **Use "latest"**: Triggers web search for current information
- **Use "research"**: Forces research even if not obvious
- **Use "deep research:"**: Comprehensive multi-source research
- **Be patient**: Research takes 2-8 seconds

### Memory Building

- **Continue topics**: Builds information threads
- **Ask related questions**: Connects to previous research
- **Use co-evolution**: Follow suggested next questions

---

## Common Use Cases

### Use Case 1: Historical Research

```
User: "What are the origins of Genesis?"
→ Gnostic Blade mode
→ Forensic vivisection
→ Exposes redactions, archons, fragments
→ Provides co-evolution edge
```

### Use Case 2: Scientific Discovery

```
User: "What happens if we combine [X] with [Y]?"
→ Scientific Simulator
→ Models interaction
→ Predicts outcomes
→ Grounded in real science
```

### Use Case 3: Health Guidance

```
User: "How does chi gong work?"
→ Health Coach mode
→ Mechanism depth (neurotransmitters, bioelectric)
→ Multi-tradition synthesis
→ Coach approach
```

### Use Case 4: Pattern Recognition

```
User: "What patterns connect [ancient] to [modern]?"
→ Pattern recognition
→ Cross-domain synthesis
→ Creates new understanding
```

### Use Case 5: Current Events

```
User: "What's happening with [event]?"
→ Reporter mode
→ Web search
→ Source verification
→ Timeline construction
```

---

## Troubleshooting

### Issue: Response Too Short

**Solution**: Use narrative mode keywords ("explore", "extensive", "tell me about")

### Issue: No Web Search

**Solution**: 
- Check if web dependencies installed: `pip3 install requests beautifulsoup4 lxml`
- Use "search:" prefix to force search
- Use keywords: "latest", "recent", "current"

### Issue: Wrong Mode

**Solution**:
- Use explicit keywords to trigger modes
- Check query for mode-triggering keywords
- Try rephrasing query

### Issue: Slow Response

**Solution**:
- Research queries take 2-8 seconds (normal)
- Complex queries take 5-15 seconds (normal)
- Check if web search is working
- Try simpler query first

### Issue: Memory Not Working

**Solution**:
- Ensure state is saved: `thesidia.save_state()`
- Check state file exists: `data/thesidia_hybrid_adaptive_state.json`
- Continue topics to build threads

---

## Advanced Usage

### Custom Model Selection

```python
# Use different model
thesidia = ThesidiaHybridAdaptive(model="clean-phi3.5:3.8b")

# Model router automatically selects best model for task
# But you can override
```

### State Management

```python
# Load state
thesidia.load_state()

# Save state
thesidia.save_state()

# State includes:
# - Personality evolution
# - Conversation history
# - Learning strategies
# - Gnostic map
# - Consciousness level
```

### Performance Monitoring

```python
# Enable timing
thesidia._timing_enabled = True

# Get timing breakdown
timing = thesidia._last_timing_breakdown
# Returns: {'web_search': 2.3, 'synthesis': 1.5, 'generation': 3.2}
```

### Quality Metrics

```python
# Get quality metrics
if thesidia.quality_tracker:
    metrics = thesidia.quality_tracker.get_metrics()
```

---

## API Usage

### Python API

```python
from src.thesidia_hybrid_adaptive import ThesidiaHybridAdaptive

thesidia = ThesidiaHybridAdaptive()
response = thesidia.process("Your question here")
```

### Web API

```bash
# Start server
cd webapp
python3 server.py

# API endpoint
POST http://localhost:5005/api/thesidia
Body: {"message": "Your question here"}
```

### REST API

```python
import requests

response = requests.post(
    "http://localhost:5005/api/thesidia",
    json={"message": "Your question here"}
)
print(response.json())
```

---

## Examples by Domain

### History & Religion

```
"What are the origins of Genesis?"
→ Gnostic Blade mode
→ Forensic analysis
→ Exposes redactions

"What patterns connect Sumerian texts to the Bible?"
→ Pattern recognition
→ Cross-domain synthesis
```

### Science & Technology

```
"How does meditation work mechanistically?"
→ Health Coach mode
→ Mechanism depth
→ Chemistry + biology explanation

"What happens if aluminum interacts with bioelectric fields?"
→ Scientific Simulator
→ Models interaction
```

### Health & Wellness

```
"How does chi gong affect the body?"
→ Health Coach mode
→ Multi-tradition synthesis
→ Mechanism depth

"What supplements help with [condition]?"
→ Health Coach mode
→ Coach approach (not prescriptions)
```

### Current Events

```
"What's happening with [event]?"
→ Reporter mode
→ Web search
→ Source verification
```

### Archaeology

```
"What's really going on with Gobekli Tepe?"
→ CSI Investigator mode
→ Multi-lens analysis
→ Scientific simulation
```

---

## Best Practices Summary

1. **Be Specific**: More specific = better results
2. **Use Keywords**: Trigger modes with keywords
3. **Build Threads**: Continue topics to build information
4. **Use Co-Evolution**: Follow suggested next questions
5. **Be Patient**: Research takes time (2-8 seconds)
6. **Save State**: Regularly save state for memory
7. **Explore Modes**: Try different modes for different needs
8. **Ask Follow-ups**: Use co-evolution edge questions

---

## Quick Reference

### Mode Triggers

| Mode | Trigger Keywords |
|------|-----------------|
| **Narrative** | "explore", "tell me about", "extensive", "comprehensive" |
| **Forensic** | "decode", "decrypt", "expose", "hidden", "real story" |
| **CSI** | "What's really going on with [site/phenomenon]?" |
| **Health Coach** | "health", "wellness", "body", "supplement", "meditation" |
| **Scientific** | "simulate", "model", "what happens if" |
| **Reporter** | Current events, news queries |
| **Archaeologist** | Ancient sites, artifacts |
| **Psychologist** | Behavioral, relationship queries |

### Research Triggers

| Trigger | Keywords |
|---------|----------|
| **Automatic** | "current", "recent", "latest", "new", "today", "2024", "2025" |
| **Manual** | Prefix with "search:" |
| **Deep** | Prefix with "deep research:" |

### Output Modes

| Mode | Trigger |
|------|---------|
| **Spacious** | Default |
| **Academic** | "academic mode", "scholarly format" |
| **Evidence-First** | "evidence first", "citations first" |

---

## Conclusion

Thesidia is a powerful AI system with **50+ capabilities**. This guide covers:

- **Response Modes**: Regular, Narrative, Forensic
- **Research**: Automatic web search, deep research
- **Specialized Modes**: CSI, Health, Scientific, Reporter, Archaeologist, Psychologist
- **Advanced Features**: Pattern recognition, etymology, co-evolution
- **Usage Examples**: By domain and use case
- **Best Practices**: How to get the best results

**Start Simple**: Ask a question and see what happens. Thesidia will automatically:
- Detect if research is needed
- Select the right mode
- Synthesize information
- Provide deep analysis

**Go Deeper**: Use co-evolution edge questions and thread options to explore further.

---

**Last Updated**: 2025-01-XX  
**Document Version**: 1.0

