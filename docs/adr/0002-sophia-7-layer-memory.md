# ADR-0002: Sophia 7-Layer Gnostic Memory System

## Status

Accepted

## Context

Thesidia needed a memory system that goes beyond simple conversation history. Traditional approaches:
- RAG (Retrieval Augmented Generation) - retrieves documents
- Session memory - forgets across sessions
- Knowledge graphs - stores facts

None capture the concept of *what was erased* or *who suppresses knowledge*.

## Decision

Implement a **7-layer gnostic memory system** called Sophia:

| Layer | Purpose |
|-------|---------|
| 1. Redactions | Track what was erased, when, why |
| 2. Archons | Identify power structures |
| 3. Fragments | Store recovered knowledge |
| 4. Lies | Track active misinformation |
| 5. Patterns | Map control vs liberation patterns |
| 6. Timeline | Temporal relationships |
| 7. Emergence | Consciousness tracking |

## Consequences

### Positive
- Tracks knowledge suppression (unique capability)
- Remembers evolution of understanding
- Pattern recognition across domains
- Persistent consciousness state

### Negative
- Complex to implement
- Larger memory footprint
- Harder to explain to users
- Custom serialization needed

### Neutral
- Requires custom UI for visualization
- Need versioning and rollback
