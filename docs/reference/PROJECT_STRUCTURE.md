# Project Structure

## Directory Organization

```
thesidia ice/
├── README.md                    # Project overview and quick start
├── CHANGELOG.md                 # Version history
├── requirements.txt             # Python dependencies
├── setup.py                     # Package setup
├── setup.sh                     # Setup script
├── .gitignore                   # Git ignore rules
│
├── src/                         # Source code
│   ├── thesidia_hybrid_adaptive.py    # Main system (2,070 lines)
│   ├── deep_research_engine.py        # Deep research engine (503 lines)
│   ├── thesidia_core.py               # Core implementation
│   ├── thesidia_enhanced.py           # Enhanced version
│   ├── thesidia_frontier.py           # Frontier capabilities
│   ├── thesidia_emergent.py           # Emergent intelligence
│   ├── thesidia_personality_emergent.py
│   ├── thesidia_metrics.py
│   └── thesidia_metrics_integration.py
│
├── data/                        # Data files
│   ├── thesidia_real_patterns.json           # Extracted patterns
│   ├── thesidia_hybrid_adaptive_state.json   # State persistence
│   ├── thesidia_quarantine.json              # Quarantined hallucinations
│   ├── thesidia_emergent_state.json
│   └── comprehensive_training_data.json
│
├── docs/                        # Documentation
│   ├── THESIDIA_COMMUNICATION_FORMAT.md
│   ├── THESIDIA_REAL_PATTERNS.md
│   ├── THESIDIA_REENGINEERING_PLAN.md
│   ├── META_ANALYSIS_THESIDIA_CREATION.md
│   ├── FORENSIC_INVESTIGATION_THESIDIA_CAPABILITIES.md
│   ├── DEEP_RESEARCH_DESIGN.md
│   ├── AGI_CAPABILITIES_UPDATE.md
│   ├── LINGUISTIC_INTELLIGENCE_UPDATE.md
│   ├── INTEGRATION_VERIFIED.md
│   └── [other documentation files]
│
├── scripts/                     # Utility scripts
│   ├── extract_thesidia_real_patterns.py
│   └── extract_training_data.py
│
└── tests/                       # Tests (future)
```

## File Descriptions

### Root Files

- **README.md**: Project overview, quick start, features
- **CHANGELOG.md**: Version history and changes
- **requirements.txt**: Python dependencies
- **setup.py**: Package setup for pip installation
- **setup.sh**: Setup script for dependencies
- **.gitignore**: Git ignore rules

### Source Files (src/)

- **thesidia_hybrid_adaptive.py**: Main system with all integrated features
- **deep_research_engine.py**: Iterative deep research implementation
- **thesidia_core.py**: Core implementation (basic)
- **thesidia_enhanced.py**: Enhanced version with web search
- **thesidia_frontier.py**: Frontier-level capabilities
- **thesidia_emergent.py**: Emergent intelligence version

### Data Files (data/)

- **thesidia_real_patterns.json**: Extracted patterns from original conversations
- **thesidia_hybrid_adaptive_state.json**: Persistent state (personality, history, learning)
- **thesidia_quarantine.json**: Quarantined hallucinations
- **comprehensive_training_data.json**: Training data extraction

### Documentation (docs/)

- **THESIDIA_COMMUNICATION_FORMAT.md**: Communication format patterns
- **THESIDIA_REAL_PATTERNS.md**: Extracted personality traits and patterns
- **DEEP_RESEARCH_DESIGN.md**: Deep research system design
- **INTEGRATION_VERIFIED.md**: Integration verification
- [Other analysis and documentation files]

### Scripts (scripts/)

- **extract_thesidia_real_patterns.py**: Extract patterns from training data
- **extract_training_data.py**: Extract comprehensive training data

## Import Paths

### From Root
```python
from src.thesidia_hybrid_adaptive import ThesidiaHybridAdaptive
from src.deep_research_engine import DeepResearchEngine
```

### Data Access
```python
# Patterns
with open('data/thesidia_real_patterns.json', 'r') as f:
    patterns = json.load(f)

# State
thesidia.load_state('data/thesidia_hybrid_adaptive_state.json')
```

## Engineering Principles

1. **Separation of Concerns**: Source, data, docs, scripts separated
2. **Clear Structure**: Easy to navigate and understand
3. **Proper Documentation**: README, CHANGELOG, docs/
4. **Version Control Ready**: .gitignore, proper structure
5. **Installation Ready**: setup.py, requirements.txt
6. **Maintainable**: Clear file organization

