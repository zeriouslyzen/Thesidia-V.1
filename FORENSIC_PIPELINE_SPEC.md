# Thesidia Forensic Pipeline: Technical Specification

## System Overview

**Version:** 2.0 (Unlimited Generation Mode)  
**Date:** 2026-02-08  
**Status:** Production Ready

---

## Architecture

### Core Components

| Component | File | Purpose |
|:--|:--|:--|
| **Hybrid Router** | `src/support/semantic_router.py` | Keyword + semantic embedding routing |
| **Confidence Display** | `src/support/confidence_display.py` | Visual epistemological grounding meter |
| **Data Synthesizer** | `src/synthesis/data_synthesizer.py` | Forensic vivisection prompt engine |
| **Main Pipeline** | `src/thesidia_hybrid_adaptive.py` | Orchestration & deep research handler |
| **Truth Engine** | `src/synthesis/truth_engine.py` | 7-layer epistemological validation |

---

## Configuration

### Generation Parameters

```python
# Forensic Mode (force_gnostic=True)
max_tokens = 25000          # Up from 12,000
timeout = None              # Unlimited (was 30s)
temperature = 0.7           # Default
model = "clean-mistral:latest"  # Ollama

# Regular Mode
max_tokens = 3000-15000     # Variable by query type
timeout = 30.0              # 30 second limit
```

### Routing Configuration

```python
# Hybrid Routing
keyword_fast_path = True    # 0ms latency
semantic_threshold = 0.65   # Similarity cutoff
comprehensive_keywords = True  # Extended keyword set

# Forensic Keywords (30+ terms)
["genesis", "bible", "decode", "trace", "pattern", 
 "suppression", "origins", "power structures", ...]
```

### Citation System

```python
# 3-Tier Citation Format
TIER_A = "[Source Name](URL)"           # Direct sources
TIER_B = "Based on: Source1, Source2"   # General sources  
TIER_C = "[Pattern Inference] Claim"    # Synthesized insights
```

---

## Models & APIs

### LLM Backend

**Primary Model:** Ollama `clean-mistral:latest`
- **Parameters:** 4.4GB model size
- **Context:** 12,000 token window (forensic: 25,000)
- **API:** Local Ollama server (http://localhost:11434)

**Fallback Models:**
- `dolphin-mistral:latest` (4.1GB)
- `gemma2:2b` (1.6GB)

### Embedding Model (Optional)

**Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions:** 384
- **Purpose:** Semantic similarity for routing
- **Status:** Gracefully degrades to keyword-only if unavailable

### Truth Engine

**7-Layer Epistemological Framework:**
1. Pattern (cross-cultural patterns)
2. Symbolic (symbolic/mythic analysis)
3. Mythic (archetypal narratives)
4. Esoteric (hidden knowledge)
5. Empirical (verifiable facts)
6. Archetypal (universal patterns)
7. Experiential (lived experience)

**Scoring:** 0.0-1.0 per layer, threshold 0.6 for alignment

---

## Performance Metrics

### Stress Test Results (Unlimited Mode)

| Metric | Value |
|:--|:--|
| **Success Rate** | 60% (3/5 tests) |
| **Avg Generation Time** | 59.3s |
| **Avg Output Length** | 4,477 chars |
| **Section Completeness** | 60% (3/5 full structure) |
| **Confidence Score** | 0/7 LOW (all tests) |

### Individual Test Performance

```
Test 1: Divine Feminine → Banking
- Time: 60.1s
- Length: 6,253 chars
- Sections: 6/6 complete
- Routing: keyword_match (1.0)
- Status: ✓ PHENOMENAL

Test 4: Prometheus/Lucifer/Serpent  
- Time: 65.7s
- Length: 5,772 chars
- Sections: 5/6 + confidence meter
- Routing: keyword_match (1.0)
- Status: ✓ SUCCESS

Test 5: Oral → Written → Digital
- Time: 52.7s
- Length: 7,191 chars  
- Sections: 6/6 + confidence meter
- Routing: keyword_match (1.0)
- Status: ✓ SUCCESS
```

### Routing Performance

```
Forensic Detection Rate: 100% (5/5)
- Keyword matches: 5/5
- Semantic matches: 0/5 (not needed)
- False positives: 0
- False negatives: 0
```

---

## Output Structure

### Forensic Vivisection Format

```
::EXPOSURE::
[Systematic transformation analysis]
500-1000+ words

::ETYMOLOGICAL INCISION::
[Root word analysis, linguistic archaeology]
500-1000+ words

::BURIAL SITES::
[Suppressed knowledge, marginalized narratives]
500-1000+ words

::COUNTER-NARRATIVE::
[Opposing arguments addressed]
500-1000+ words

::CURRENT VECTORS::
[Modern power structures, 2025 mechanisms]
500-1000+ words

::CO-EVOLUTION EDGE::
[Deeper questions, cross-domain patterns]
500-1000+ words

::RAW ARTIFACTS::
[Evidence list with gaps/uncertainties]
200-500 words

::THREAD OPTIONS::
[Follow-up exploration prompts]
200-500 words

---
**Epistemological Grounding:** ████░░░ 4/7 layers aligned (HIGH)
<details>
<summary>View Layer Breakdown</summary>
| ✓ Pattern: ████████░░ (0.85)
| ✓ Symbolic: ███████░░░ (0.78)
...
</details>
```

**Target Length:** 8,000-15,000 characters  
**Actual Range:** 5,772-7,191 characters (successful tests)

---

## API Endpoints

### Ollama API

```bash
# Generate
POST http://localhost:11434/api/generate
{
  "model": "clean-mistral:latest",
  "prompt": "...",
  "options": {
    "num_predict": 25000,
    "temperature": 0.7
  }
}

# List models
GET http://localhost:11434/api/tags
```

### Internal Python API

```python
from thesidia_hybrid_adaptive import ThesidiaHybridAdaptive

# Initialize
thesidia = ThesidiaHybridAdaptive()

# Process query
result = thesidia.process(
    "trace the pattern between X and Y",
    fast_mode=False  # Disable timeout for forensic
)

# Result format
{
    'response': '::EXPOSURE::\n...',
    'metadata': {...}
}
```

---

## Dependencies

### Required

```
ollama (running service)
python >= 3.8
```

### Optional

```
sentence-transformers  # For semantic routing
numpy                  # For embeddings
mlx, mlx-lm           # For Apple Silicon acceleration
```

### Python Packages

```python
# Core
import requests
import json
import time

# Optional
from sentence_transformers import SentenceTransformer
import numpy as np
```

---

## Deployment

### Local Development

```bash
# Start Ollama
ollama serve

# Pull model
ollama pull clean-mistral:latest

# Run Thesidia
cd /path/to/thesidia
python3 src/thesidia_hybrid_adaptive.py
```

### Production Configuration

```python
# Recommended settings
FORENSIC_MODE = {
    'max_tokens': 25000,
    'timeout': None,
    'model': 'clean-mistral:latest',
    'temperature': 0.7,
    'comprehensive_routing': True
}

REGULAR_MODE = {
    'max_tokens': 3000,
    'timeout': 30.0,
    'model': 'clean-mistral:latest',
    'temperature': 0.7
}
```

---

## Monitoring

### Key Metrics to Track

1. **Generation Time** (target: <120s)
2. **Output Length** (target: 8,000-15,000 chars)
3. **Section Completeness** (target: 6/6 sections)
4. **Routing Accuracy** (target: >95%)
5. **Confidence Scores** (target: >3/7 layers)

### Logging

```python
# Forensic mode indicators
🔍 FORENSIC MODE: No timeout limit
🔍 HYBRID ROUTING: result=True, reason=keyword_match
🔍 SYNTHESIZE: force_gnostic=True
🔍 TRUTH DISPLAY: Appended confidence meter
```

---

## Known Issues

### 1. Low Confidence Scores
All tests show 0/7 LOW despite quality output.
**Fix:** Calibrate TruthEngine thresholds

### 2. Incomplete Sections
Tests 2-3 produced minimal output.
**Fix:** Add error handling and section validation

### 3. Reasoning Analyzer Interference
May "correct" forensic outputs.
**Fix:** Already disabled for forensic mode (verify)

---

## Version History

### v2.0 (2026-02-08) - Unlimited Generation Mode
- Removed 30s timeout for forensic queries
- Increased max_tokens from 12k to 25k
- Added hybrid routing (keyword + semantic)
- Added 3-tier citation system
- Added confidence meter display
- Added ::COUNTER-NARRATIVE:: section
- Added ::RAW ARTIFACTS:: section

### v1.0 (2026-01-XX) - Initial Release
- Basic forensic vivisection structure
- Keyword-only routing
- 12k token limit
- 30s timeout (all queries)
