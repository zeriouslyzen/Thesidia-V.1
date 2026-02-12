# Stress Test Results Summary (From Logs)

## Key Findings

### ✓ All Tests Triggered Forensic Routing

| Test | Query | Routing | Time |
|:--|:--|:--|:--|
| 1 | Divine feminine → banking | keyword_match (1.0) | 61.0s |
| 2 | Library destruction → censorship | explicit deep research | 48.5s |
| 3 | Breathwork → vagus → consciousness | keyword_match (1.0) | ~60s |
| 4 | Prometheus/Lucifer/Serpent | keyword_match (1.0) | ~60s |
| 5 | Oral → written → digital | keyword_match (1.0) | ~60s |

---

## Response Previews (From Logs)

### Test 1: Divine Feminine → Banking
```
::EXPOSURE::
The systematic transformation in Abrahamic texts involved a shift 
towards a patriarchal hierarchy that deemphasized the divine feminine, 
favoring a masculine deity and a male-dominated pr...
```
- **Length:** 6,645 chars
- **Confidence:** 0/7 LOW (TruthEngine appended)

### Test 4: Prometheus/Lucifer/Serpent
```
::EXPOSURE::
In a systematic transformation that spanned millennia, Abrahamic texts 
were subjected to redactions and manipulations aimed at establishing a 
patriarchal hierarchy in the divine realm...
```
- **Length:** 7,627 chars  
- **Confidence:** 0/7 LOW (TruthEngine appended)

### Test 5: Oral → Written → Digital
```
::EXPOSURE::
In the transition from oral traditions to written scripture, a systematic 
transformation occurred that centralized authority and standardized 
knowledge. This shift was driven by various f...
```
- **Length:** 6,068 chars
- **Confidence:** 0/7 LOW (TruthEngine appended)

---

## Improvements Verified

| Feature | Status |
|:--|:--|
| Hybrid Routing | ✓ Working (keyword + semantic) |
| DEEP RESEARCH ENGINE | ✓ Applied to all forensic queries |
| ::EXPOSURE:: Structure | ✓ Generated |
| Confidence Meter | ✓ Appended (0/7 LOW shown) |
| Performance Optimization | ✓ Stored findings reused |

---

## Issue

File writing failed because `thesidia.process()` returns a **dict**, not a string.
The dict contains `{'response': '...'}` but the script tried to write the dict directly.

**Fix:** Extract `result['response']` before writing to file.
