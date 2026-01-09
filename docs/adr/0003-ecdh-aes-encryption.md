# ADR-0003: ECDH + AES-GCM Encryption for KIM

## Status

Accepted

## Context

KIM (Killer Instant Messaging) needed end-to-end encryption for DMs. Requirements:
- Server cannot read messages
- Works in browser (no native code)
- Key exchange without pre-shared secrets
- Future-proof encryption

Options considered:
1. **WebCrypto ECDH + AES-GCM** - Browser native
2. **RSA + AES** - Traditional, larger keys
3. **libsodium (NaCl)** - Requires WASM
4. **Signal Protocol** - Complex, overkill for 1:1

## Decision

Use **ECDH P-256 + AES-GCM 256-bit** via Web Crypto API:
- ECDH for key exchange (P-256 curve)
- AES-GCM for message encryption
- 12-byte random IV per message
- Keys stored in IndexedDB

## Consequences

### Positive
- Browser-native (no dependencies)
- Strong encryption (256-bit AES)
- Server cannot decrypt (true E2E)
- Fast on modern hardware

### Negative
- No forward secrecy (key rotation needed)
- Group encryption needs Sender Keys (not implemented)
- Keys in IndexedDB need protection
- P-256 vs newer curves (X25519) debate

### Neutral
- Need separate solution for group chat
- Key backup/recovery is user's responsibility
