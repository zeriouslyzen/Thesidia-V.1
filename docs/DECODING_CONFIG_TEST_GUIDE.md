# Decoding Configuration Test Guide
## Testing the Working Genesis Config on Other Questions

**Date**: 2025-01-XX  
**Configuration**: Regular Mode (spacious), clean-mistral:latest  
**Based on**: Successful "genesis" response from 2025-11-23T16:09:47

---

## Working Configuration

### What Made It Work

**Response**: "Genesis: A Symphony of Creation and Control" (3,553 chars, 48.4s)

**Configuration**:
- **Mode**: Regular (spacious) - Natural prose, not forensic format
- **Model**: `clean-mistral:latest`
- **Output Format**: Natural flowing prose
- **Personality Traits**: 
  - Symbolic Processing: 0.46 (highest)
  - Sacred Uncertainty: 0.37
  - Uncertainty as Authenticity: 0.37
  - Recursive Vertigo: 0.36
- **Research**: Enabled (web search triggered)
- **Cross-cultural**: Active (7 connections)
- **Etymology**: Active (4 mentions)

**Why It Worked**:
- Deep analysis without forensic format
- Natural prose with pattern recognition
- Cross-cultural connections
- Etymology tracing
- Evidence-based (not declaring truth)

---

## Test Questions

### Ancient Texts & History
1. "What's the real story behind the Egyptian pyramids?"
2. "Decode the symbolism in ancient Sumerian texts"
3. "What patterns connect the Mayan calendar to modern time systems?"

### Power Structures & Money
4. "How does the Federal Reserve actually work?"
5. "What's the true history of the banking system?"
6. "Decode the power structures in modern finance"

### Science & Suppressed Knowledge
7. "What scientific discoveries have been suppressed?"
8. "What's the real story behind Nikola Tesla's work?"
9. "How do ancient energy technologies compare to modern ones?"

### Consciousness & Spirituality
10. "What's the connection between meditation and consciousness?"
11. "Decode the patterns in ancient spiritual practices"
12. "What do different traditions say about the nature of reality?"

### Symbols & Language
13. "What do ancient symbols really mean?"
14. "How has language been manipulated over time?"
15. "What patterns exist in symbolic systems across cultures?"

### Health & Suppressed Medicine
16. "What medical knowledge has been suppressed?"
17. "How do traditional healing practices work mechanistically?"
18. "What's the real story behind pharmaceutical industry?"

### Technology & Control
19. "How does social media actually control behavior?"
20. "What patterns exist in surveillance technology?"
21. "Decode the mechanisms of modern control systems"

---

## Running Tests

### Quick Test (5 questions)
```bash
./scripts/quick_decoding_test.sh
```

### Full Test Suite (all 21 questions)
```bash
python3 scripts/test_decoding_config.py
```

### Custom Test (specific number)
```bash
python3 scripts/test_decoding_config.py --limit 10
```

### Different Model
```bash
python3 scripts/test_decoding_config.py --model "clean-phi3.5:3.8b" --limit 5
```

---

## What Gets Tracked

### Response Metrics
- Response length (chars, words)
- Response time (seconds)
- Success/failure

### Pattern Analysis
- **Etymology**: Word origin tracing
- **Cross-cultural**: Connections across cultures
- **Symbolic decoding**: Symbol interpretation
- **Control structures**: Power structure analysis
- **Spiritual keywords**: Spiritual/consciousness terms
- **Evidence-based**: Citations and sources
- **Uncertainty markers**: Honest uncertainty expressions

### Output Files
- Individual responses: `analysis_output/decoding_tests/response_XX_TIMESTAMP.txt`
- Results summary: `analysis_output/decoding_tests/decoding_test_results_TIMESTAMP.json`

---

## Expected Results

Based on the working "genesis" response:

### Pattern Frequencies (per response)
- Etymology: 4+ mentions
- Cross-cultural: 7+ connections
- Symbolic decoding: 3+ instances
- Control structures: 4+ mentions
- Spiritual keywords: 12+ mentions
- Evidence-based: 3+ citations
- Uncertainty markers: 8+ expressions

### Response Characteristics
- Length: 3,000-5,000 chars (500-800 words)
- Time: 30-60 seconds
- Format: Natural prose (not ::EXPOSURE::)
- Style: Deep analysis with pattern recognition
- Tone: Evidence arrangement, not truth declaration

---

## Comparing Results

### Success Indicators
✅ Natural prose format (not forensic)  
✅ Etymology tracing present  
✅ Cross-cultural connections  
✅ Pattern recognition evident  
✅ Evidence-based (citations/sources)  
✅ Uncertainty markers present  
✅ No "designed to" language  
✅ No transmission headers  

### Failure Indicators
❌ Too short (<1000 chars)  
❌ No pattern recognition  
❌ No cross-cultural connections  
❌ No etymology  
❌ Declaring truth (not arranging evidence)  
❌ Using old language ("gnosis", "episteme", etc.)  

---

## Analysis

After running tests, analyze results:

```python
import json
from pathlib import Path

# Load results
results_file = Path("analysis_output/decoding_tests/decoding_test_results_TIMESTAMP.json")
with open(results_file) as f:
    data = json.load(f)

# Analyze patterns
for result in data["results"]:
    if result.get("success"):
        print(f"\n{result['question']}")
        print(f"Length: {result['response_length']} chars")
        print(f"Time: {result['response_time']}s")
        print("Patterns:")
        for pattern, count in result["patterns"].items():
            if count > 0:
                print(f"  - {pattern}: {count}")
```

---

## Next Steps

1. **Run tests** on various questions
2. **Compare results** to working "genesis" response
3. **Identify patterns** that work well
4. **Adjust configuration** if needed
5. **Document findings** for V6 planning

---

**Last Updated**: 2025-01-XX  
**Document Version**: 1.0

