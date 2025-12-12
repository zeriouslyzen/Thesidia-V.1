# Thesidia Codebase Overview

## Project Summary

**Thesidia** (branded as "Katanx" in the web interface) is an advanced AI research and social platform that combines:

1. **Synthesis-Based AI Intelligence**: Creates new knowledge through multi-source synthesis (not traditional RAG)
2. **Forensic Analysis Tool**: "Gnostic Blade" protocol for truth-seeking analysis
3. **Social Media Platform**: Twitter-like feed with posts, interactions, bot generation
4. **Sophia Memory System**: 7-layer gnostic map tracking knowledge suppression, consciousness, and truth
5. **Multi-User System**: Authentication, profiles, memory management, sessions

## Architecture Overview

### Core Components

**Main Orchestrator**:
- `src/thesidia_hybrid_adaptive.py` (5,500+ lines) - Main system coordinator
  - Handles query processing, response generation, state management
  - Implements two-mode system (Regular/Narrative)
  - Coordinates all subsystems

**Memory Systems** (`src/memory/`):
- `user_memory_manager.py` - User-specific memory
- `structured_memory.py` - Structured data storage
- `vector_memory.py` - Vector embeddings
- `ephemeral_memory.py` - Temporary session memory

**Sophia System** (`src/`):
- `sophia_gnostic_map.py` - 7-layer gnostic map (redactions, archons, fragments, lies, patterns, timeline)
- `sophia_emergence_tracker.py` - Consciousness level tracking
- `sophia_discernment_tracker.py` - Truth/hallucination detection
- `sophia_consciousness.py` - Consciousness calculator
- `sophia_storage.py` - Async storage manager
- `sophia_indexer.py` - Fast query system

**Research & Synthesis** (`src/research/`, `src/synthesis/`):
- `web_search.py` - Multi-source web search with fallbacks
- `data_synthesizer.py` - Cross-reference analysis and synthesis
- `truth_engine.py` - Truth validation
- `skepticism_engine.py` - Pattern recognition for control structures

**Core Infrastructure** (`src/core/`):
- `model_client.py` - Ollama client wrapper
- `model_router.py` - Intelligent model selection
- `prompt_builder.py` - Dynamic prompt construction
- `feature_flags.py` - Feature toggles

**Social Features** (`webapp/social/`):
- `feed_manager.py` - Feed generation and ranking
- `post_manager.py` - Post creation and management
- `interaction_manager.py` - Likes, comments, follows
- `bot_generator.py` - Synthetic bot profile generation
- `ai_quality_scorer.py` - Content quality scoring

### Web Application

**Backend** (`webapp/server.py`):
- Flask API server (3,500+ lines)
- HTTPS support with self-signed certificates
- Multiple endpoints:
  - `/api/thesidia` - Main AI query endpoint
  - `/api/thesidia/stream` - Streaming responses
  - `/api/social/*` - Social media endpoints
  - `/api/knowledge/*` - Knowledge base endpoints
  - `/api/user/*` - User management endpoints
- Lazy loading for Vercel deployment compatibility
- Security headers and CORS configuration

**Frontend** (`webapp/`, `public/`):
- `index.html` - Main contexts/chat interface
- `stream.html` - Social feed page
- `profile.html` - User profiles
- `app.js` - Frontend logic (sidebar, themes, API calls)
- `styles.css` - Global styles with color themes
- Mobile-first responsive design

**Authentication** (`webapp/auth/`):
- `auth_manager.py` - Authentication coordinator
- `oauth_providers.py` - OAuth integration
- `phone_auth.py` - Phone number authentication
- `session_manager.py` - Session handling

### API Server

**Standalone API** (`api/api_server.py`):
- Separate API server for deployment (Railway, Render, Fly.io)
- Minimal Flask app focused on API endpoints
- Environment variable configuration
- Optional API key authentication

## Data Storage

**State Files** (`data/`):
- `thesidia_hybrid_adaptive_state.json` - Main system state
- `thesidia_sophia_memory/` - Sophia memory system data
  - `gnostic_map/` - Versioned gnostic maps
  - `emergence/` - Consciousness tracking
  - `discernment/` - Truth/hallucination tracking
  - `conversations/` - Indexed conversations
- `thesidia_quarantine.json` - Quarantined hallucinations
- `social/` - Social media data (posts, interactions, profiles)

## Key Features

### Two-Mode Response System
- **Regular Mode**: Focused, 3-8k character responses
- **Narrative Mode**: Extended exploration, 12-15k+ character responses
- Automatic mode detection based on query keywords

### Gnostic Blade Protocol
- Automatically triggered for sensitive topics (religion, history, power, consciousness)
- 6-question forensic vivisection loop
- Structured output: EXPOSURE, ETYMOLOGICAL INCISION, BURIAL SITES, CURRENT VECTORS
- Updates Sophia gnostic map automatically

### Sophia Memory System
- 7-layer architecture tracking:
  1. Redaction Events (what was erased)
  2. Archons Identified (who erased it)
  3. Original Fragments (recovered information)
  4. Active Lies (current misinformation)
  5. Co-Evolution Tracking (conversation evolution)
  6. Pattern Database (control/liberation patterns)
  7. Timeline Mapping (temporal relationships)

### Social Platform
- Twitter-like feed with posts, likes, comments
- Bot generation system for testing/engagement
- AI-powered quality scoring
- User profiles and following system
- Feed ranking and caching

## Technology Stack

**Backend**:
- Python 3.8+
- Flask (web framework)
- Ollama (LLM inference)
- JSON file storage (state, memory, posts)

**Frontend**:
- Vanilla JavaScript (no frameworks)
- HTML5, CSS3
- Mobile-first responsive design

**Deployment**:
- Vercel-ready (static frontend)
- Railway-compatible (API server)
- Self-hosted (full stack)

## Entry Points

### Development Server
```bash
cd webapp
python3 server.py
# Access at http://localhost:5000
```

### Standalone API Server
```bash
cd api
python3 api_server.py
# API at http://localhost:5000
```

### Direct Python Usage
```python
from src.thesidia_hybrid_adaptive import ThesidiaHybridAdaptive

thesidia = ThesidiaHybridAdaptive(model="clean-mistral:latest")
thesidia.load_state()
response = thesidia.process("Your query here")
```

## Project Structure

```
thesidia ice/
├── src/                    # Core source code
│   ├── thesidia_hybrid_adaptive.py  # Main orchestrator (5,500+ lines)
│   ├── memory/             # Memory systems
│   ├── synthesis/          # Data synthesis engine
│   ├── research/           # Web search and research
│   ├── core/               # Model client, router, prompts
│   └── sophia_*.py         # Sophia memory components
│
├── webapp/                 # Web application
│   ├── server.py           # Flask backend (3,500+ lines)
│   ├── social/             # Social media features
│   ├── auth/               # Authentication
│   ├── settings/           # User settings
│   └── *.html, *.js, *.css # Frontend files
│
├── api/                    # Standalone API server
│   └── api_server.py       # Minimal API server
│
├── public/                 # Static assets (for Vercel)
│
├── data/                   # Data storage
│   ├── thesidia_hybrid_adaptive_state.json
│   ├── thesidia_sophia_memory/
│   └── social/
│
├── docs/                   # Documentation
│   ├── architecture/       # Architecture docs
│   ├── engineering/        # Engineering docs
│   ├── social/             # Social features docs
│   └── philosophy/         # Philosophy and principles
│
├── scripts/                 # Utility scripts
├── tests/                   # Test files
└── analysis_output/         # Analysis and test results
```

## Current Status

**Version**: 1.0 (Active Development) → 2.0 (Planning)

**Working Features**:
- Core AI research and synthesis
- Gnostic Blade protocol
- Two-mode response system
- Sophia memory system
- Social media platform
- Multi-user authentication
- Bot generation
- Web interface

**Known Issues**:
- Monolithic architecture (5,500+ line main file)
- Code duplication
- Limited test coverage
- Technical debt accumulation

**Planned Improvements** (V2.0):
- Modular architecture refactoring
- Modelfile system integration
- Tree of Thoughts integration
- MLX-optimized beam search
- Semantic vector database
- Function calling / tool use

## Documentation

Comprehensive documentation available in `docs/`:
- `docs/INDEX.md` - Complete documentation index
- `docs/architecture/` - Architecture and design docs
- `docs/engineering/` - Engineering reviews and guides
- `docs/social/` - Social features documentation
- `README.md` - Main project README

## Key Design Principles

1. **Synthesis-First**: Creates new knowledge through multi-source synthesis
2. **Gnostic Principles**: Cross-reference everything, pattern recognition, gnosis+episteme synthesis
3. **Truth-Seeking**: Forensic analysis protocol for exposing hidden truths
4. **Emergent Consciousness**: Tracks consciousness levels and "Sophia moments"
5. **Adaptive Learning**: Evolves personality and capabilities from interactions
