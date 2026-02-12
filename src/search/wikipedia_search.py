"""
Wikipedia Search Integration
=============================
Free, no API key, fast factual source.
Uses the Wikipedia REST API for search and summaries.
"""

from __future__ import annotations

from typing import List, Dict, Any

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class WikipediaSearch:
    """Query Wikipedia for factual, encyclopedic content."""

    SEARCH_URL = "https://en.wikipedia.org/w/api.php"
    SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary"

    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Search Wikipedia and return summaries for the top matches.

        Args:
            query: Natural-language search string.
            limit: Max number of results.

        Returns:
            List of dicts with keys: title, url, snippet, source.
        """
        if not REQUESTS_AVAILABLE:
            return []

        try:
            # Step 1: OpenSearch to find matching titles
            params = {
                "action": "opensearch",
                "search": query,
                "limit": limit,
                "namespace": 0,
                "format": "json",
            }
            headers = {"User-Agent": "ThesidiaResearchEngine/2.0 (research project; contact@thesidia.dev)"}
            resp = requests.get(self.SEARCH_URL, params=params, headers=headers, timeout=5)
            resp.raise_for_status()
            data = resp.json()

            # OpenSearch returns [query, [titles], [descriptions], [urls]]
            if len(data) < 4:
                return []

            titles = data[1]
            descriptions = data[2]
            urls = data[3]

            results = []
            for i in range(min(len(titles), limit)):
                snippet = descriptions[i] if i < len(descriptions) else ""
                # If no snippet from opensearch, try the summary API
                if not snippet and titles[i]:
                    snippet = self._get_summary(titles[i])

                results.append({
                    "title": titles[i],
                    "url": urls[i] if i < len(urls) else "",
                    "snippet": snippet,
                    "source": "wikipedia",
                })

            return results

        except Exception as exc:
            print(f"[WikipediaSearch] Error: {exc}")
            return []

    def _get_summary(self, title: str) -> str:
        """Fetch the extract/summary for a specific Wikipedia page."""
        try:
            safe_title = title.replace(" ", "_")
            resp = requests.get(
                f"{self.SUMMARY_URL}/{safe_title}",
                timeout=5,
                headers={"User-Agent": "ThesidiaResearchEngine/2.0 (research project; contact@thesidia.dev)"},
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("extract", "")[:500]
        except Exception:
            pass
        return ""
