"""
Multi-Source Search Aggregator
==============================
Parallel fan-out across Brave + SearXNG + Wikipedia + DuckDuckGo.
Merges, deduplicates, and reranks results.

Usage:
    searcher = MultiSearch()
    results = searcher.quick_search("elon musk news")      # Auto mode: 5-15s
    results = searcher.deep_search("history of eclipses")   # Research mode: 15-30s per round
"""

from __future__ import annotations

import os
import time
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .brave_search import BraveSearch
from .wikipedia_search import WikipediaSearch
from .reranker import ResultReranker

# Optional: SearXNG and DuckDuckGo (existing code dependencies)
try:
    import requests
    from bs4 import BeautifulSoup
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False


class MultiSearch:
    """
    Parallel fan-out search across multiple backends.
    All search methods are synchronous but fan out via ThreadPoolExecutor.
    """

    # Public SearXNG instances (fallback if self-hosted not available)
    SEARXNG_INSTANCES = [
        "https://searx.tiekoetter.com",
        "https://searx.prvcy.eu",
        "https://search.sapti.me",
        "https://searx.be",
    ]

    def __init__(self, brave_api_key: Optional[str] = None):
        self.brave = BraveSearch(api_key=brave_api_key)
        self.wikipedia = WikipediaSearch()
        self.reranker = ResultReranker(max_per_domain=2)

    # ── Public API ────────────────────────────────────────────────

    def quick_search(
        self,
        query: str,
        max_results: int = 8,
        freshness: str = "",
    ) -> List[Dict[str, Any]]:
        """
        Auto-mode search: fan out across Brave + SearXNG + Wikipedia in parallel.
        Target: 10-20 candidate results merged into top 8, in <5 seconds.

        Args:
            query: User query.
            max_results: Final result count after reranking.
            freshness: Brave freshness filter ("pd", "pw", "pm", or "").

        Returns:
            Reranked list of result dicts.
        """
        start = time.time()
        all_results = []

        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {
                pool.submit(self.brave.search, query, 10, freshness): "brave",
                pool.submit(self._searxng_search, query, 10): "searxng",
                pool.submit(self._duckduckgo_search, query, 10): "duckduckgo",
                pool.submit(self.wikipedia.search, query, 3): "wikipedia",
            }
            for future in as_completed(futures, timeout=12):
                source = futures[future]
                try:
                    results = future.result(timeout=8)
                    all_results.extend(results)
                    print(f"[MultiSearch] {source}: {len(results)} results", flush=True)
                except Exception as exc:
                    print(f"[MultiSearch] {source} failed: {exc}", flush=True)

        # Rerank and return top N
        ranked = self.reranker.rerank(all_results, query, max_results=max_results)

        elapsed = time.time() - start
        print(f"[MultiSearch] quick_search: {len(all_results)} raw -> {len(ranked)} ranked in {elapsed:.1f}s", flush=True)
        return ranked

    def deep_search(
        self,
        query: str,
        max_results: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Research-mode search: fan out across Brave + SearXNG + DuckDuckGo + Wikipedia.
        Wider net, more results, no tight timeout.

        Args:
            query: User query or sub-query from research planner.
            max_results: Final result count after reranking.

        Returns:
            Reranked list of result dicts.
        """
        start = time.time()
        all_results = []

        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {
                pool.submit(self.brave.search, query, 15): "brave",
                pool.submit(self._searxng_search, query, 15): "searxng",
                pool.submit(self._duckduckgo_search, query, 10): "duckduckgo",
                pool.submit(self.wikipedia.search, query, 5): "wikipedia",
            }
            for future in as_completed(futures, timeout=20):
                source = futures[future]
                try:
                    results = future.result(timeout=15)
                    all_results.extend(results)
                    print(f"[MultiSearch] deep/{source}: {len(results)} results", flush=True)
                except Exception as exc:
                    print(f"[MultiSearch] deep/{source} failed: {exc}", flush=True)

        # For deep search, allow more per domain
        deep_reranker = ResultReranker(max_per_domain=3)
        ranked = deep_reranker.rerank(all_results, query, max_results=max_results)

        elapsed = time.time() - start
        print(f"[MultiSearch] deep_search: {len(all_results)} raw -> {len(ranked)} ranked in {elapsed:.1f}s", flush=True)
        return ranked

    def scrape_urls(self, urls: List[str], max_chars: int = 6000) -> List[Dict[str, Any]]:
        """
        Scrape a list of URLs in parallel and return content.

        Args:
            urls: List of URLs to scrape.
            max_chars: Max characters per page.

        Returns:
            List of dicts with: url, title, content.
        """
        if not WEB_AVAILABLE:
            return []

        def _scrape_one(url: str) -> Dict[str, Any]:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/120.0.0.0 Safari/537.36"
                }
                resp = requests.get(url, headers=headers, timeout=8)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")

                # Remove script/style
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()

                title = soup.title.string.strip() if soup.title and soup.title.string else ""
                text = soup.get_text(separator="\n", strip=True)[:max_chars]

                return {"url": url, "title": title, "content": text}
            except Exception as exc:
                return {"url": url, "title": "", "content": f"[Scrape failed: {exc}]"}

        with ThreadPoolExecutor(max_workers=min(len(urls), 5)) as pool:
            results = list(pool.map(_scrape_one, urls[:10]))  # Cap at 10 URLs

        return results

    # ── Private backends ──────────────────────────────────────────

    def _searxng_search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search via public SearXNG instances. Return first success."""
        if not WEB_AVAILABLE:
            return []

        for instance in self.SEARXNG_INSTANCES:
            try:
                resp = requests.get(
                    f"{instance}/search",
                    params={
                        "q": query,
                        "format": "json",
                        "categories": "general",
                    },
                    timeout=5,
                    headers={"User-Agent": "ThesidiaResearch/2.0"},
                )
                if resp.status_code != 200:
                    continue

                data = resp.json()
                results = []
                for item in data.get("results", [])[:num_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("content", ""),
                        "source": "searxng",
                    })
                if results:
                    return results
            except Exception:
                continue

        return []

    def _duckduckgo_search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search DuckDuckGo via HTML scraping (no API key needed)."""
        if not WEB_AVAILABLE:
            return []

        try:
            from urllib.parse import urlparse, parse_qs, unquote

            resp = requests.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                  "AppleWebKit/537.36"
                },
                timeout=10,
            )
            soup = BeautifulSoup(resp.text, "html.parser")

            results = []
            for div in soup.find_all("div", class_="result")[:num_results]:
                title_el = div.find("a", class_="result__a")
                snippet_el = div.find("a", class_="result__snippet")
                if title_el:
                    raw_url = title_el.get("href", "")
                    # DuckDuckGo wraps URLs in redirects:
                    #   //duckduckgo.com/l/?uddg=ENCODED_URL&...
                    actual_url = raw_url
                    if "duckduckgo.com/l/" in raw_url:
                        try:
                            parsed = urlparse(raw_url)
                            qs = parse_qs(parsed.query)
                            if "uddg" in qs:
                                actual_url = unquote(qs["uddg"][0])
                        except Exception:
                            pass

                    results.append({
                        "title": title_el.get_text(),
                        "url": actual_url,
                        "snippet": snippet_el.get_text() if snippet_el else "",
                        "source": "duckduckgo",
                    })
            return results
        except Exception as exc:
            print(f"[MultiSearch] DuckDuckGo error: {exc}")
            return []
