"""
Result Reranker
===============
Deduplicates, caps per-domain results, and scores by relevance/trust/freshness.
"""

from __future__ import annotations

import re
from typing import List, Dict, Any
from urllib.parse import urlparse
from collections import defaultdict


# Trusted domains get a score boost
_TRUSTED_DOMAINS = frozenset({
    "wikipedia.org", "en.wikipedia.org",
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk",
    "nytimes.com", "washingtonpost.com", "theguardian.com",
    "nature.com", "science.org", "sciencedirect.com",
    "arxiv.org", "scholar.google.com",
    "gov", "edu",  # TLD-level trust
})

# Freshness signals in the "age" field from Brave
_FRESH_RE = re.compile(r"(\d+)\s*(hour|minute|second|day)", re.IGNORECASE)


class ResultReranker:
    """Deduplicate, cap per-domain, and score search results."""

    def __init__(self, max_per_domain: int = 2):
        self.max_per_domain = max_per_domain

    def rerank(
        self,
        results: List[Dict[str, Any]],
        query: str,
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Process raw search results:
            1. Normalize and deduplicate by URL
            2. Cap per-domain
            3. Score by relevance + trust + freshness
            4. Return top max_results sorted by score descending

        Each result dict should have: title, url, snippet, source, age (optional).
        """
        # Step 1: Deduplicate by normalized URL
        seen_urls = set()
        unique = []
        for r in results:
            norm = self._normalize_url(r.get("url", ""))
            if norm and norm not in seen_urls:
                seen_urls.add(norm)
                r["_norm_url"] = norm
                unique.append(r)

        # Step 2: Cap per domain
        domain_counts = defaultdict(int)
        capped = []
        for r in unique:
            domain = self._extract_domain(r.get("url", ""))
            if domain_counts[domain] < self.max_per_domain:
                domain_counts[domain] += 1
                r["_domain"] = domain
                capped.append(r)

        # Step 3: Score
        query_terms = set(query.lower().split())
        for r in capped:
            r["_score"] = self._score(r, query_terms)

        # Step 4: Sort and return
        capped.sort(key=lambda r: r["_score"], reverse=True)
        # Strip internal keys before returning
        output = []
        for r in capped[:max_results]:
            clean = {k: v for k, v in r.items() if not k.startswith("_")}
            clean["relevance_score"] = r["_score"]
            output.append(clean)

        return output

    # ── Internal helpers ──────────────────────────────────────────

    def _normalize_url(self, url: str) -> str:
        """Strip tracking params, www prefix, trailing slashes."""
        try:
            parsed = urlparse(url)
            host = parsed.netloc.lower().lstrip("www.")
            path = parsed.path.rstrip("/")
            return f"{host}{path}"
        except Exception:
            return url.lower().strip("/")

    def _extract_domain(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            host = parsed.netloc.lower().lstrip("www.")
            parts = host.split(".")
            if len(parts) >= 2:
                return ".".join(parts[-2:])
            return host
        except Exception:
            return "unknown"

    def _score(self, result: Dict[str, Any], query_terms: set) -> float:
        score = 0.0

        # Title relevance: count query term overlaps
        title_terms = set(result.get("title", "").lower().split())
        overlap = len(query_terms & title_terms)
        score += overlap * 2.0

        # Snippet relevance
        snippet_terms = set(result.get("snippet", "").lower().split())
        score += len(query_terms & snippet_terms) * 0.5

        # Source trust
        domain = result.get("_domain", "")
        tld = domain.split(".")[-1] if "." in domain else ""
        if domain in _TRUSTED_DOMAINS or tld in _TRUSTED_DOMAINS:
            score += 3.0

        # Source diversity bonus (wikipedia always valuable)
        if result.get("source") == "wikipedia":
            score += 2.0

        # Freshness bonus
        age = result.get("age", "")
        if age:
            m = _FRESH_RE.search(age)
            if m:
                num = int(m.group(1))
                unit = m.group(2).lower()
                if unit in ("hour", "minute", "second"):
                    score += 2.0
                elif unit == "day" and num <= 7:
                    score += 1.0

        return round(score, 2)
