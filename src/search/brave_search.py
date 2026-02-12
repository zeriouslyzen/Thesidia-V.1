"""
Brave Search API Wrapper
========================
Primary search backend for Thesidia v2.
Free tier: 2,000 queries/month. Paid: $5/1K queries.
"""

from __future__ import annotations

import os
import time
from typing import List, Dict, Any, Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class BraveSearch:
    """Wraps the Brave Web Search API for structured search results."""

    ENDPOINT = "https://api.search.brave.com/res/v1/web/search"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("BRAVE_API_KEY", "")
        self._last_request_time = 0.0
        self._min_interval = 1.0  # 1 req/s on free tier

    @property
    def available(self) -> bool:
        return bool(self.api_key) and REQUESTS_AVAILABLE

    def search(self, query: str, count: int = 10, freshness: str = "") -> List[Dict[str, Any]]:
        """
        Search Brave and return structured results.

        Args:
            query: Search query string.
            count: Number of results (max 20).
            freshness: Optional freshness filter -- "pd" (past day), "pw" (past week),
                       "pm" (past month), or "" (any time).

        Returns:
            List of dicts with keys: title, url, snippet, source, age.
        """
        if not self.available:
            return []

        # Rate-limit: 1 request/sec on free tier
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)

        params = {
            "q": query,
            "count": min(count, 20),
            "search_lang": "en",
            "text_decorations": False,
        }
        if freshness:
            params["freshness"] = freshness

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key,
        }

        try:
            self._last_request_time = time.time()
            resp = requests.get(
                self.ENDPOINT,
                params=params,
                headers=headers,
                timeout=8,
            )
            resp.raise_for_status()
            data = resp.json()

            results = []
            for item in data.get("web", {}).get("results", [])[:count]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("description", ""),
                    "source": "brave",
                    "age": item.get("age", ""),
                })
            return results

        except Exception as exc:
            print(f"[BraveSearch] Error: {exc}")
            return []
