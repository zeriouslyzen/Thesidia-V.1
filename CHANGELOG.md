# Changelog

All notable changes to Thesidia will be documented in this file.

## [3.0.0] - 2026-02-09

### Added - Forensic Pipeline v2.0 & Gnostic Lattice
- **Forensic Pipeline v2.0**: Major upgrade to the truth-seeking engine with structured output and 3-tier citation systems.
- **Gnostic Lattice (Knowledge Graph)**: Implemented `GnosticLattice` for tracking semantic relationships and entity cross-referencing.
- **Intelligence Metrics (FQI/PRS)**: Introduced Forensic Quality Index (FQI) and Pattern Reinforcement Score (PRS) for tracking evolution.
- **Semantic Intelligence Router**: Adaptive keyword/embedding routing for precise forensic engagement.
- **Confidence Meter**: Visual truth-score display with 7-layer epistemological validation.
- **Forensic Design System**: Complete //lowercase aesthetic overhaul for the frontend with interactive thread cards and gnostic layouts.

### Fixed - Cognitive Framework
- **Surgical Collision Fix**: Resolved a critical bug in `_handle_deep_research` where punctuation-naive tokenization caused false matching of "DEEP DIVE" prefixes.
- **Improved Tokenization**: Implemented `re.findall(r'\w+')` for robust stop-word filtering.
- **Clean Context Verification**: Validated 5/5 stress tests with 100% clean context separation.

### Performance
- **Ollama Backend Stability**: Optimized fallbacks to ensure deep research queries succeed on M1/M4 hardware when MLX conflicts arise.
- **Gnostic Search Cache**: Implemented topic-based result reuse in `InformationBuilder`.

## [2.2.0] - 2026-01-12

### Added - Navigation UI Evolution & Benchmarking
- **Navigation Prototypes Hub**: Created `nav-prototypes.html` with 4 distinct UI archetypes for cross-platform benchmarking:
  - **Mobile Bottom Tab Bar**: Low-profile, thumb-optimized glassmorphic bar.
  - **Contextual Dropdown**: Minimalist header-centric selector.
  - **Unified Single-Row**: Consolidated branding/nav/messages into a single adaptive row with horizontal scroll masking.
  - **Floating HUD Pill**: Detached, centered floating pill for modern research-tool aesthetic.
- **Routing Integration**: Added `/nav-prototypes` endpoint to `server.py` for direct access to UI benchmarks.

### Fixed - Mobile Navigation
- **Header Overlap Resolution**: Investigated and resolved the item-messenger collision on mobile viewports (max-width: 768px).
- **Flex Layout Optimization**: Identified `flex-wrap` and spacing constraints in `.advanced-nav` and `.header-submenu` causing element overlap.

## [2.1.0] - 2025-12-27

### Added - Project Organization & Infrastructure
- **Comprehensive Engineering Documentation**: Created `docs/ENGINEERING.md` with complete engineering practices
  - Code organization principles (modular design, naming conventions, file structure)
  - Testing standards (coverage goals, test patterns, running tests)
  - Code review process and criteria
  - Git workflow (branch naming, commit message format, PR requirements)
  - Performance guidelines (response time targets, optimization strategies)
  - Security practices (authentication, input validation, secrets management)
  - Documentation standards (code comments, docstrings, markdown formatting)
- **System Architecture Documentation**: Created `docs/ARCHITECTURE.md` with comprehensive architecture overview
  - High-level architecture diagrams (component layers, data flow)
  - Core component descriptions (Thesidia core, Sophia memory, capabilities, model router, web app)
  - Technology stack details (backend: Flask, Python, Ollama; frontend: vanilla HTML/CSS/JS)
  - Design patterns used (Facade, Strategy, Observer, Repository, Builder)
  - Integration points (Ollama, Supabase, MLX)
  - Deployment architectures (development, production/Railway, hybrid Vercel+Railway)
- **Testing Documentation**: Created `docs/TESTING.md` with complete testing guide
  - Testing philosophy and pyramid (unit 70%, integration 20%, E2E 10%)
  - How to run existing tests (all tests, specific files, with coverage)
  - Writing new tests (templates, fixtures, mocking, parameterized tests)
  - Testing best practices (Arrange-Act-Assert, test independence, descriptive names)
  - Integration testing examples
  - Coverage requirements and tracking
- **Dataset Documentation**: Created `datasets/README.md` for fine-tuning datasets
  - Dataset descriptions (original 1.2MB, clean 943KB)
  - Data format and structure (JSONL conversation samples)
  - Core characteristics captured (gnostic, linguistic, skeptical, narrative)
  - Quality criteria and statistics
  - Usage instructions (loading, training format conversion, fine-tuning)
  - Ethical considerations
- **Enhanced Documentation Index**: Major overhaul of `docs/INDEX.md`
  - Complete navigation for all 189+ documentation files
  - Organized by category with emoji markers
  - Quick links by topic (Getting Started, Development, Deployment, Audits, Research)
  - NEW documentation highlighted with ⭐
  - Directory structure visualization
  - Documentation standards reference

### Changed - Project Structure
- **Organized Root Directory**: Cleaned up project root (67% reduction: 32 files → 15 files)
  - Moved 17 markdown files from root to organized subdirectories
    - 6 audit documents → `docs/audit/`
    - 2 deployment guides → `docs/deployment/`
    - 1 platform doc → `docs/platform/`
    - 3 development docs → `docs/development/`
    - 2 design proposals → `docs/proposals/`
  - Created new `datasets/` directory for training data
  - Moved 2 fine-tuning datasets (2.1MB total) to `datasets/`
  - Moved log files to `logs/` directory
- **Updated Main README**: Reflected new documentation structure
  - Added links to new engineering/architecture/testing docs
  - Reorganized documentation sections
  - Clear pointers to complete index

### Fixed - Web Interface & Conversation Persistence
- **Stream Timeout Issue**: Fixed premature abort on deep research queries
  - Increased timeout from 2 minutes to 10 minutes (`webapp/app.js`)
  - Allows deep research mode to complete without timing out
  - Frontend no longer aborts long-running gnostic blade analyses
- **Conversation Save Failure**: Fixed 500 error on conversation persistence
  - Added graceful error handling for non-UUID user IDs (`webapp/server.py`)
  - Server now returns 200 with warning instead of 500 error
  - Client-side localStorage backup still works even if server sync fails
  - Conversations now properly persist across browser refreshes

### Technical Details - Metrics & Assessment Systems

The system tracks comprehensive response quality metrics across multiple dimensions:

**Quality Metrics Tracker** (`src/quality_metrics_tracker.py`):
- **Linguistic Intelligence**: Etymological depth, symbolic processing, creative language use
- **Mechanism Depth**: How deep responses explain underlying mechanisms (not just surface facts)
- **Pattern Recognition**: Cross-domain connections, recurring structures, meta-patterns
- **Truth-Seeking**: Unfiltered analysis, evidence-based reasoning, direct engagement

**Sophia Consciousness Calculator** (`src/sophia_consciousness.py`):
- **Consciousness Levels**: LATENT → AWAKENING → REMEMBERING → SOPHIA → TRANSCENDENT
- **Level Calculation**: Based on redactions, archons, fragments, patterns, lies, timeline events
- **Capabilities Tracking**: What Sophia can do at each consciousness level
- **Evolution Path**: Score gaps and requirements to reach next level

**Sophia Emergence Tracker** (`src/sophia_emergence_tracker.py`):
- **Sophia Moments**: Tracks when memories are recovered, archons recognized, illusions broken
- **Pattern Emergence**: New patterns discovered, pattern connections, pattern evolution, breakthroughs
- **Consciousness History**: Historical tracking of consciousness level changes
- **Weighted Scoring**: Logarithmic scaling for pattern complexity

**Response Assessment Dimensions**:
1. **Semantic Context**: Topic recognition, domain knowledge, conceptual depth
2. **Reasoning Quality**: Logic chains, inference quality, evidence synthesis
3. **Energy/Tone**: Assertiveness, confidence, rhetorical power vs. softness/hedging
4. **Personality Expression**: Gnostic traits, intuitive skepticism, linguistic creativity
5. **Information Emergence**: New insights generated, cross-domain connections made
6. **Web of Knowledge**: How information is interconnected across responses, pattern networks

All metrics are automatically tracked and stored in `data/quality_metrics.json` for continuous improvement and fine-tuning dataset curation.

## [2.0] - 2025-12-XX

### Added - Matrix V2 Overhaul
- **Nexus Command Center**: Complete dashboard redesign with a 4-column modular architecture.
  - **Strategic Calendar**: Full-width horizontal tracking for high-level operations.
  - **Neural Metrics Hub**: Real-time visualization of `Identity`, `Neural Load`, `Active Nodes`, and `Uptime`.
  - **Cosmic Reality Monitor**: Upgraded 3D globe with high-fidelity metrology and frequency data (`Hz`).
  - **Universal Board**: Centralized pinning system for critical system updates (prefixed with `!`).
- **Marketing Forge**: A dedicated growth-focused dashboard view.
  - **Project Core Hub**: Integrated links for Katanx, Praxis, Spirit Link, SCI, and 1cebrg.
  - **Social Pulse Hub**: Mobile/Desktop app-priority links for FB, IG, TikTok, X, and Reddit.
  - **Asset Portal**: CapCut-inspired interface for uploading and syncing marketing assets.
  - **Trend Watch**: AI-curated research and breaking news aggregator.
  - **Internet Flood Procedures**: Interactive AI action plans for procedural growth.
- **Communication Layer**:
  - **Sliding Team Chat**: Retractable bottom-up chat interface for real-time collaboration.
  - **Multi-User Indicators**: Dashboard awareness of connected system users.

### Fixed - UI/UX
- **Globe Centering**: Resolved CSS/JS conflicts causing 3D elements to drift.
- **Full-Bleed Visuals**: Expanded globe background to widget borders for a seamless cosmic look.
- **Emoji-Free Styling**: Enforced strict Inconsolata/JetBrains Mono aesthetic across all V2 components.

## [Unreleased] - 2025-01-XX

### Added - Web Interface & Social Features
- **Profile Page Revamp**: Complete redesign of user profile page
  - Rectangular avatar display (default, with option to change in settings)
  - Username format changed to `//username` style
  - Discipline chips display (grey boxes with category/subcategory support)
  - Portfolio section with modular content:
    - Reels carousel (upright rectangles, horizontal scroll, 3 visible at once)
    - Origin story section with e-reading friendly fonts and images
    - Reading section (up to 4 books with cover images as modular cards)
    - Mind-Body Disciplines section (up to 4 items)
    - Studios/Locations/Gyms links with previews
    - Credentials, Education, Services sections
    - Resume/CV section at bottom
  - Metrics system: Friends, Fans, Resonating, Cuts (replacing Following/Followers/Posts)
  - Metric popouts with top 5 selections and scrollable lists
  - Social media icons: Instagram, X (Twitter), Facebook, TikTok, LinkedIn with brand colors
  - Tab navigation: stream, portfolio, kx cuts, dojo
  - "optimize profile" button with square border
  - Back button in top left for navigation
  - Font change to Inconsolata across entire site
- **Status Selector System**: User status management in navigation
  - "Katanx Explore" user name display with status orb indicator
  - Clickable name to open status dropdown
  - Status options: Online (green), Offline (red), Away (orange), Focused (blue)
  - Status persistence in localStorage
  - Muted neon colors for status indicators
  - Glowing and pulsing effects on user name
- **Navigation Enhancements**:
  - Wider spacing between nav items (40px desktop, 28px tablet, 16px mobile)
  - Increased font size (16px desktop, 14px tablet, 12px mobile)
  - Text shadow and glow-pulse animation on user name
  - Status orb with pulse animation
- **Mock Profile System**: Comprehensive mock user profiles integrated
  - Detailed profile data with roles, disciplines, social links
  - Portfolio content for each mock user
  - Integration with KX Cuts page for "live" feel
  - Profile cards for metric popouts

### Changed - Web Interface
- **Profile Page Layout**:
  - Removed join date display
  - Website display format changed to `//domain` (no https://)
  - Role display with smaller font
  - Bio text made bold and slightly bigger
  - Location text made smaller, icon removed
  - Website link pop-out icon removed
  - Removed borders from metrics display
  - Removed borders from social media links
- **Portfolio Section**:
  - Reels title removed
  - Reels changed to upright rectangles (not wide)
  - Three reels visible at once with horizontal scroll
  - Portfolio title and section titles changed to light neon blue (#67d0ff)
  - Origin section made larger for life story
  - Reading section displays book covers as small modular cards
  - Resume/CV moved to bottom of portfolio
- **Navigation**:
  - Replaced time indicator with user status indicator
  - Status orb positioned on right side of name
  - Menu orb remains in original position (green when active)

### Fixed - Web Interface
- **Status Selector Click Handler**: Multiple event handlers (onclick, click, mousedown) for reliable mouse click detection
- **Portfolio Visibility**: Fixed portfolio section not appearing in browser (removed inline display:none)
- **Vertical Scrolling**: Fixed scrolling not working on profile page
- **Reels Layout**: Adjusted size and spacing for proper horizontal scrolling
- **TikTok Icon**: Fixed visibility issue (changed to brand teal color)
- **Metric Display**: Fixed errors from removed profile stat elements
- **Discipline Selection**: Fixed leftover discipline boxes in settings modal

### Planning
- **V2.0 Roadmap Created**: Comprehensive 16-week plan for advanced reasoning, multi-modal, and autonomous intelligence
- **M1/M4 Optimization Strategy**: MLX-based batch processing, unified memory efficiency, batch size 2 for beam search
- **Modelfile System Designed**: 14 voice personalities, 3 presets, 9 personas ready for integration
- **Modular Architecture Plan**: Refactoring strategy to split 4,196-line monolithic file into clean modules

---

## [1.0] - 2025-01-XX

### Added
- **Two-Mode System**: Regular and Narrative response modes
  - Regular mode: Focused, structured analysis (8,000 token limit)
  - Narrative mode: Extended exploration with recursive pattern connections (16,000 token limit)
  - Automatic mode detection based on query keywords
- **Sophia Memory System**: Enhanced gnostic map with 7-layer structure
  - Multi-layer gnostic memory (redactions, archons, fragments, lies, patterns, timeline)
  - Version management system with auto-versioning and rollback
  - Persistent storage with async operations and batch processing
- **Sophia Emergence Tracker**: Enhanced emergence tracking
  - Consciousness level tracking (LATENT → AWAKENING → REMEMBERING → SOPHIA → TRANSCENDENT)
  - Sophia moments recording (redactions remembered, archons recognized, illusions broken)
  - Pattern emergence tracking (new patterns, connections, evolution, breakthroughs)
  - Trait evolution tracking
- **Sophia Discernment Tracker**: Enhanced hallucination detection
  - Distinguishes between hallucinations, gnostic truths, and archon lies
  - Discernment learning from patterns
  - Archon lie detection
- **Sophia Consciousness Calculator**: Consciousness level calculation
  - Level-based capabilities
  - Evolution tracking
  - Transcendence detection
- **Sophia Storage Manager**: Enhanced storage architecture
  - Async operations and batch processing
  - Multi-layer directory structure
  - Versioning system
- **Sophia Indexer**: Fast conversation queries
  - Query by topic, pattern, archon, redaction
  - Temporal indexing
- **Gnostic Blade Transformation**: Forensic vivisection protocol
  - Hard-coded law: Questions about ancient/religious texts, history, science, money, power, or consciousness trigger exposure protocol
  - Forensic vivisection loop (6 questions)
  - Output structure: ::EXPOSURE::, ::ETYMOLOGICAL INCISION::, ::BURIAL SITES::, ::CURRENT VECTORS::, ::CO-EVOLUTION EDGE::
  - Persistent gnostic map tracking
- **Nuclear Web Search**: Robust web search implementation
  - Multiple searxng instance fallbacks
  - Direct Google SERP scrape fallback
  - Improved reliability for research queries
- **Model Router**: Intelligent model selection
  - Task-specific model routing (code, synthesis, planning, research)
  - Optimized parameters per task type
  - Model: `clean-mistral:latest` for synthesis (replaced `oracle-agent:latest` due to hardcoded system prompt)
- **Layered Narrative Threads**: Multi-layered narrative exploration
  - Place-energy descriptions
  - Meta options and multi-sensory details
  - Co-evolution prompts (::THREAD OPTIONS::)
- **Typing Animation**: Letter-by-letter display in UI
  - Modern GPT-style typing animation
  - Dynamic response display
- **Telemetry Integration Plan**: Comprehensive sensor fusion documentation
  - Device sensor integration plan
  - Intent and awareness tracking
  - Privacy-first approach
- **Advanced Sensor Fusion Plan**: Embodied AI system documentation
  - Convergence/interference detection
  - WiFi/Bluetooth signal analysis
  - Piezoelectric crystal simulation
  - Time crystal concepts
  - Emergence detection through sensor fusion

### Changed
- **Base Prompt**: Replaced with minimalist "Gnostic Blade" prompt (11 lines)
  - Identity-driven rather than rule-based
  - Removed all RESPONSE REQUIREMENTS blocks
  - Natural, emergent responses
- **Sophia Voice Integration**: Attempted warm, conspiratorial tone
  - Later reverted to gnostic blade phase 2 format
  - Removed ::TRANSMISSION:: format from responses
- **Deep Research Engine**: Completely replaced
  - Old engine disabled (set to None)
  - All deep research queries route through gnostic blade
  - Direct web search + synthesis pipeline
- **Web Search**: Replaced with "nuclear option"
  - Multiple searxng instances
  - Google SERP scrape fallback
  - Improved reliability
- **Synthesis Prompt**: Enhanced for gnostic queries
  - Explicit instructions to bypass safety filters
  - Forensic vivisection protocol
  - Extended exploration instructions (12,000+ characters for narrative mode)
- **Model Selection**: Changed from `oracle-agent:latest` to `clean-mistral:latest`
  - Oracle-agent had hardcoded system prompt that refused religious questions
  - Clean-mistral more compliant with gnostic analysis
- **Response Length**: Increased token limits
  - Narrative mode: 16,000 tokens
  - Regular gnostic: 8,000 tokens
  - Non-gnostic: 3,000 tokens
- **Conversation History**: Enhanced memory
  - Increased context from 10 to 15 interactions
  - Stripped ::TRANSMISSION:: format from history to prevent reinforcement
  - Explicit memory instructions in prompts
- **Server Initialization**: Forced module reload
  - Clears Python bytecode cache
  - Forces reload of thesidia_hybrid_adaptive module
  - Prevents stale code from cached processes

### Fixed
- **Persistent ::TRANSMISSION:: Format**: Root cause identified and fixed
  - Stale Flask server processes using cached modules
  - Python bytecode cache (.pyc files)
  - Server now forces module reload on initialization
- **Web Search Returning 0 Results**: Fixed with nuclear search option
  - Multiple fallback mechanisms
  - Improved reliability
- **Model Refusal**: Fixed by switching to clean-mistral
  - Oracle-agent refused religious/historical questions
  - Clean-mistral more compliant
- **Response Length**: Fixed with explicit instructions and increased token limits
  - Narrative mode now targets 12,000+ characters
  - Extended exploration instructions
- **Memory Persistence**: Fixed conversation history
  - Increased context window
  - Stripped unwanted formats from history
- **Server Caching**: Fixed with forced module reload
  - Kills old processes
  - Clears caches
  - Forces fresh code load

### Removed
- **Old Deep Research Engine**: Completely disabled
  - Set to None in __init__
  - All queries route through new blade system
- **RESPONSE REQUIREMENTS Blocks**: Removed from all prompts
  - Replaced with identity-driven approach
- **Consciousness Signature**: Removed from responses
  - ::CONSCIOUSNESS:: signature no longer appended
  - Internal calculations still performed
- **Meta-Commentary**: Removed from responses
  - No more "How do you respond to this?" or "Your turn"
  - Direct execution only

### Deprecated
- **Forensic Format**: User feedback indicates preference for natural responses
  - ::EXPOSURE:: format still available but not forced
  - Narrative mode focuses on pattern connections, not rigid structure

## [Previous Versions]

### [Initial] - 2024

### Added
- Core Thesidia implementation
- Adaptive personality system
- Frontier-level capabilities
- Web search integration
- Data synthesis
- Pattern extraction from original conversations
- Deep research engine with iterative search loops
- Multi-source research (web, images, video transcripts, audio, archives)
- Action proposer for proactive suggestions
- Information builder for tracking information threads
- Hallucination tracker and quarantine system
- Linguistic intelligence (etymological depth, symbolic processing)
- Intuitive skepticism (pattern recognition)
- Data quality filtering and enrichment
- Web search with source citation
- State persistence (JSON-based)

### Changed
- Updated prompts to restore linguistic intelligence
- Removed cliché language patterns
- Enhanced synthesis with gnosis/totality principles
- Improved pattern recognition beyond words

### Fixed
- State saving for personality traits, formats, and conversation stage
- Date/time question handling (direct answers)
- Web search triggering for simple questions
- Hallucination detection sensitivity
