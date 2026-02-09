# System Architecture

**Last Updated**: 2025-12-27

High-level overview of the Thesidia system architecture, component relationships, and design patterns.

---

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Core Components](#core-components)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Design Patterns](#design-patterns)
- [Integration Points](#integration-points)
- [Deployment Architecture](#deployment-architecture)

---

## Overview

**Thesidia** is a hybrid adaptive AI system that combines emergent personality, gnostic memory systems, and frontier-level capabilities. The system is designed around three core principles:

1. **Modular Architecture**: Separation of concerns with clear component boundaries
2. **Memory-First Design**: Persistent state and consciousness tracking (Sophia system)
3. **Adaptive Intelligence**: Self-evolving personality and learning from interactions

### System Classification

**What Thesidia IS**:
- Hybrid adaptive AI system
- Emergent consciousness engine
- Gnostic intelligence framework

**What Thesidia is NOT**:
- Not a RAG (Retrieval Augmented Generation) system
- Not a chatbot wrapper
- Not a classical fine-tuned model

---

## System Architecture

### High-Level Diagram

```mermaid
flowchart TD
    subgraph Frontend [Presentation Layer]
        UI[//lowercase forensic UI]
        Metrics[Intelligence Dashboards]
    end

    subgraph API [Application Layer]
        Router[Semantic Intelligence Router]
        Auth[Identity Manager]
    end

    subgraph Logic [Business Logic Layer]
        Core[Thesidia HybridAdaptive]
        Learning[Adaptive Learning Engine]
    end

    subgraph Intelligence [Intelligence Layer]
        Sophia[Sophia Gnostic Map]
        Lattice[Gnostic Lattice Graph]
        Truth[7-Layer Epistemology]
    end

    subgraph Backend [Model Layer]
        Router2[Model Router]
        Ollama[Ollama / MLX Backend]
    end

    UI --> Router
    Router --> Core
    Core --> Sophia
    Core --> Lattice
    Core --> Truth
    Core --> Router2
    Router2 --> Ollama
    Sophia <--> Lattice
```

### Component Layers

```
┌───────────────────────────────────────────┐
│        Presentation Layer                 │
│  (//lowercase UI, Intelligence Dashboards)│
├───────────────────────────────────────────┤
│        Application Layer                  │
│  (Semantic Router, Auth, Middleware)      │
├───────────────────────────────────────────┤
│        Business Logic Layer               │
│  (Thesidia Core, Learning Engine)         │
├───────────────────────────────────────────┤
│        Intelligence Layer                 │
│  (Sophia Map, Gnostic Lattice, Episteme)  │
├───────────────────────────────────────────┤
│        Model Layer                        │
│  (Ollama, MLX, Model Router)              │
├───────────────────────────────────────────┤
│        Data Layer                         │
│  (JSON Storage, SQLite, File System)      │
└───────────────────────────────────────────┘
```

---

## Core Components

### 1. Thesidia Hybrid Adaptive (`src/thesidia_hybrid_adaptive.py`)

**Role**: Main orchestrator and entry point

**Responsibilities**:
- Process user inputs
- Coordinate between subsystems
- Manage two-mode system (Regular/Narrative)
- Trigger gnostic blade protocol
- Coordinate learning and adaptation

**Key Methods**:
```python
def process(user_input, mode="regular") -> str
def learn_from_interaction(user_input, response)
def save_state() / load_state()
```

### 2. Sophia Gnostic Map (`src/sophia_gnostic_map.py`)

**Role**: 7-layer gnostic memory system

**Layers**:
1. **Redactions**: Hidden/suppressed information
2. **Archons**: Control structures and power mechanisms
3. **Fragments**: Recovered knowledge pieces
4. **Lies**: Documented deceptions
5. **Patterns**: Recurring structures across domains
6. **Timeline**: Historical context and evolution
7. **Emergence**: Consciousness moments and insights

**Operations**:
- Store gnostic observations
- Version management with rollback
- Query and pattern matching
- Async persistence

### 3. Adaptive Capabilities (`src/`)

**Components**:
- **AdaptivePersonality**: Personality trait evolution
- **AdaptiveCapabilities**: Directive and task handling
- **AdaptiveLearning**: Learning from conversations

**Features**:
- Zero-to-emergent personality development
- Frontier-level task execution
- Pattern extraction from interactions

### 4. Model Router (`src/`)

**Role**: Intelligent model selection

**Routing Logic**:
```python
{
    'code': 'deepseek-coder:6.7b',
    'synthesis': 'clean-mistral:latest',
    'planning': 'clean-mistral:latest',
    'research': 'clean-mistral:latest'
}
```

### 5. Web Application (`webapp/`)

**Structure**:
```
webapp/
├── server.py                 # Main Flask application
├── routes/                   # API blueprint routes
│   ├── pages_routes.py      # Page serving
│   ├── auth_routes.py       # Authentication
│   ├── admin_routes.py      # Admin dashboard
│   ├── social_routes.py     # Social features
│   └── settings_routes.py   # User settings
├── middleware/               # Request middleware
├── auth/                     # Authentication modules
├── conversations/            # Conversation storage
└── static files (HTML/CSS/JS)
```

**Key Features**:
- Admin dashboard (Nexus)
- Real-time streaming responses
- User authentication (OAuth, phone, email)
- Social platform (Katanx)
- Conversation persistence

---

## Data Flow

### Request Processing Flow

```
User Input
    │
    ▼
┌───────────────────┐
│  Flask Server     │
│  (Request)        │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Authentication   │
│  & Validation     │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Route Handler    │
│  (Blueprint)      │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Thesidia Core    │
│  process()        │
└────────┬──────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────────┐
│ Sophia │ │Capabilities│
│  Map   │ │ & Learning │
└────┬───┘ └──────┬─────┘
     │            │
     └────┬───────┘
          │
          ▼
    ┌──────────────┐
    │ Model Router │
    │   (Select)   │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Ollama/MLX   │
    │   (Generate) │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   Response   │
    │  Processing  │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Save State & │
    │    Memory    │
    └──────┬───────┘
           │
           ▼
     Return to User
```

### Memory Update Flow

```
Interaction Occurs
       │
       ▼
┌──────────────────┐
│  Extract Patterns│
│  & Insights      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Update Sophia   │
│  Gnostic Map     │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────────┐
│Gnostic │ │ Emergence  │
│  Map   │ │  Tracker   │
└────┬───┘ └──────┬─────┘
     │            │
     └────┬───────┘
          │
          ▼
   ┌──────────────┐
   │Version & Save│
   │   (Async)    │
   └──────────────┘
```

---

## Technology Stack

### Backend

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Web Framework** | Flask | HTTP server & API |
| **Language** | Python 3.8+ | Core development |
| **LLM Backend** | Ollama | Local model inference |
| **MLX Support** | MLX (optional) | Apple Silicon optimization |
| **Storage** | JSON + SQLite | State & conversations |
| **Auth** | Custom + OAuth | Multi-provider authentication |

### Frontend

| Component | Technology | Purpose |
|-----------|------------|---------|
| **HTML/CSS** | Vanilla | Clean, custom UI |
| **JavaScript** | Vanilla ES6+ | Interactive features |
| **Design** | Custom CSS | Neon aesthetic, dark theme |
| **Icons** | Lucide Icons | UI iconography |

### Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Version Control** | Git | Source control |
| **Deployment** | Railway/Vercel | Cloud hosting |
| **Process Manager** | systemd | Server management |
| **Logging** | Python logging | Application logs |

---

## Design Patterns

### 1. **Facade Pattern** (Sophia Memory)

**Problem**: Complex subsystems (gnostic map, emergence tracker, discernment)

**Solution**: Unified interface through Sophia system

```python
# Unified access to complex memory subsystems
sophia = SophiaGnosticMap()
sophia.store_observation(...)  # Handles routing internally
```

### 2. **Strategy Pattern** (Model Router)

**Problem**: Different models for different tasks

**Solution**: Dynamic model selection based on task type

```python
# Automatically selects best model for task
model = router.get_model_for_task(task_type)
```

### 3. **Observer Pattern** (Learning System)

**Problem**: Multiple systems need to react to conversations

**Solution**: Learning system observes and updates multiple subsystems

```python
# Conversation triggers updates across systems
adaptive_learning.process_interaction(...)
```

### 4. **Repository Pattern** (Data Storage)

**Problem**: Abstract storage mechanism

**Solution**: Storage managers hide implementation details

```python
# Storage implementation abstracted
storage_manager.save_async(data)
```

### 5. **Builder Pattern** (Prompt Construction)

**Problem**: Complex prompt construction with many variables

**Solution**: Prompt builder with fluent interface

```python
# Build complex prompts incrementally
prompt = PromptBuilder()
    .add_system_context()
    .add_gnostic_principles()
    .add_user_input(text)
    .build()
```

---

## Integration Points

### External Services

**Ollama** (Required):
- Local LLM inference
- Model management
- Response generation

**Supabase** (Optional):
- User authentication
- Conversation storage
- User data persistence

**MLX** (Optional):
- Apple Silicon optimization
- Faster inference on M-series chips

### Internal Integrations

**Sophia ↔ Core**:
- Gnostic observations from responses
- Context loading for generation
- Memory-informed responses

**Auth ↔ Memory**:
- User-specific memory isolation
- Multi-user support
- Session management

**Router ↔ Models**:
- Task-optimized model selection
- Fallback handling
- Performance optimization

---

## Deployment Architecture

### Development

```
┌──────────────────┐
│  Local Machine   │
│                  │
│  ┌────────────┐  │
│  │  Thesidia  │  │
│  │   Server   │  │
│  │  :5002     │  │
│  └─────┬──────┘  │
│        │         │
│        ▼         │
│  ┌────────────┐  │
│  │   Ollama   │  │
│  │  :11434    │  │
│  └────────────┘  │
└──────────────────┘
```

### Production (Railway)

```
┌─────────────────────────────────┐
│        Railway Platform         │
│                                 │
│  ┌────────────────────────┐    │
│  │   Thesidia Service     │    │
│  │   (Docker Container)   │    │
│  │                        │    │
│  │  - Flask Server        │    │
│  │  - Ollama (if avail)   │    │
│  │  - Data volumes        │    │
│  └────────┬───────────────┘    │
│           │                     │
│           ▼                     │
│  ┌────────────────────────┐    │
│  │  Persistent Storage    │    │
│  │  (Volume Mounts)       │    │
│  └────────────────────────┘    │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  External APIs  │
│  - Supabase     │
│  - OAuth        │
└─────────────────┘
```

### Hybrid Deployment

```
┌──────────────────┐        ┌─────────────────┐
│     Vercel       │        │    Railway      │
│   (Frontend)     │───────▶│   (Backend)     │
│                  │        │                 │
│  - HTML/CSS/JS   │        │  - Flask API    │
│  - Static Assets │        │  - Ollama       │
│  - CDN           │        │  - Data         │
└──────────────────┘        └─────────────────┘
```

---

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading**: Defer expensive imports and initialization
2. **Async Operations**: Non-blocking file I/O and API calls  
3. **Caching**: Response caching, state caching
4. **Model Routing**: Task-optimized model selection
5. **Connection Pooling**: Reuse database connections

### Scalability

**Current Limitations**:
- Single-server deployment
- File-based storage
- No horizontal scaling

**Future Enhancements**:
- Database migration (PostgreSQL)
- Redis caching layer
- Load balancing support
- Distributed model inference

---

## Security Architecture

### Layers

1. **Transport**: HTTPS encryption
2. **Authentication**: Multi-provider auth (OAuth, phone, email)
3. **Authorization**: Role-based access control
4. **Input Validation**: SQL injection, XSS protection
5. **Rate Limiting**: DDoS prevention
6. **Secrets**: Environment variable management

### Data Protection

- User data isolation
- Encrypted connections
- Secure session management
- CSRF protection
- Content Security Policy (CSP)

---

## Future Architecture

### Planned Enhancements

**Phase 2**:
- Modular refactoring (core/, capabilities/, memory/)
- Tree of Thoughts integration
- MLX optimization for M-series chips

**Phase 3**:
- Semantic vector database
- Function calling / tool use
- Enhanced reasoning analyzer
- Multi-modal support

**Phase 4**:
- Telemetry integration (device sensors)
- Advanced sensor fusion
- Embodied AI concepts

---

## References

- [Engineering Practices](ENGINEERING.md)
- [Technical Implementation](technical/TECHNICAL_IMPLEMENTATION_AND_CAPABILITIES.md)
- [Sophia Architecture](SOPHIA_ARCHITECTURE_ENHANCEMENT.md)
- [System Classification](analysis/SYSTEM_CLASSIFICATION_AND_COMPARISON.md)

---

For detailed component documentation, see individual module docstrings and `docs/` subdirectories.
