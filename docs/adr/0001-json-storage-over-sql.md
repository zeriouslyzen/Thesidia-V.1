# ADR-0001: JSON Storage Over SQL

## Status

Accepted

## Context

Thesidia needed a storage solution for:
- User state and conversations
- Sophia gnostic map (7-layer memory)
- Bot profiles and social data
- KIM message persistence

Options considered:
1. **PostgreSQL/MySQL** - Traditional relational DB
2. **SQLite** - Embedded relational DB
3. **JSON files** - File-based storage
4. **Hybrid** - JSON for some, SQLite for others

## Decision

Use **JSON files as primary storage** with SQLite for specific use cases (KIM messages).

Rationale documented in `docs/WHY_JSON_NOT_SQL.md`:
- Simpler deployment (no DB server)
- Human-readable state files for debugging
- Works offline
- Easy to backup (copy files)
- Gnostic map structure maps naturally to JSON

## Consequences

### Positive
- Zero database setup for local development
- Easy state inspection and debugging
- Fast iteration without migrations
- Works offline

### Negative
- No ACID transactions across files
- Limited querying capability
- Not suitable for high concurrency
- Need to implement caching manually

### Neutral
- File-based locking needed for writes
- Potential need for database migration in future
