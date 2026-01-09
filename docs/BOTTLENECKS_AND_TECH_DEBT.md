# Bottlenecks & Technical Debt Registry

**Created**: 2026-01-08  
**Status**: Active tracking document

---

## Critical Bottlenecks

### B-001: Monolithic Core File ⚠️ CRITICAL

| Metric | Value |
|--------|-------|
| **File** | `src/thesidia_hybrid_adaptive.py` |
| **Size** | 330KB / ~5,700 lines |
| **Impact** | Hard to test, maintain, navigate |
| **Priority** | HIGH |

**Fix**: Follow extraction plan in `docs/audit/MONOLITHIC_ARCHITECTURE_EXPLAINED.md`

---

### B-002: KIM Group Chat = Cleartext ⚠️ SECURITY

| Metric | Value |
|--------|-------|
| **File** | `webapp/js/kim-crypto.js` (line 330) |
| **Impact** | Group messages not encrypted |
| **Fix** | Implement Signal's Sender Keys protocol |

---

### B-003: Frontend Memory Bloat

| Issue | File | Impact |
|-------|------|--------|
| All conversations loaded at startup | `webapp/app.js:19` | 50-100KB wasted |
| Status polling every 5s | `webapp/app.js:75` | Network overhead |
| KnowledgeBase loaded at startup | `webapp/server.py:39` | 10-50KB wasted |

**Fix**: Implement lazy loading (see `analysis_output/ux/UX_AUDIT_AND_OPTIMIZATION.md`)

---

## Tracking Table

| ID | Issue | Priority | Status |
|----|-------|----------|--------|
| B-001 | Monolithic core | HIGH | Not started |
| B-002 | KIM cleartext groups | HIGH | Not started |
| B-003 | Frontend memory bloat | MEDIUM | Not started |
| B-004 | Large webapp files | MEDIUM | Not started |
| B-005 | No DB migrations | LOW | Not started |
| B-006 | Test coverage | MEDIUM | In progress |
