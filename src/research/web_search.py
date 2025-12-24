#!/usr/bin/env python3
"""
Web Search Engine
================

Web search and scraping with quality filtering and enrichment.
Uses SearXNG instances with Google fallback.
"""

from __future__ import annotations

import re
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Optional web dependencies
try:
    import requests
    from bs4 import BeautifulSoup
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False

try:
    from .data_quality import DataQualityFilter
except ImportError:
    from data_quality import DataQualityFilter


class WebSearchEngine:
    """Web search and scraping with quality filtering and enrichment"""
    
    def __init__(self, model: str = "clean-mistral:latest", model_client=None):
        self.search_history = []
        self.scraped_data = []
        self.quality_filter = DataQualityFilter(model, model_client=model_client)
        self.min_quality_score = 0.4  # Minimum quality threshold
        
        # Simple query cache (last 50 queries, 5min TTL)
        self._query_cache: OrderedDict[str, tuple] = OrderedDict()
        self._cache_max_size = 50
        self._cache_ttl = 300  # 5 minutes
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search the web using battle-tested 2025 method: searxng.be primary, Google fallback"""
        if not WEB_AVAILABLE:
            return [{"error": "Web search not available. Install: pip3 install --user requests beautifulsoup4 lxml"}]
        
        # Try multiple searxng instances (some may be down)
        searxng_instances = [
            "https://searx.tiekoetter.com/search",
            "https://searx.prvcy.eu/search",
            "https://search.sapti.me/search",
            "https://searx.be/search"
        ]
        
        for instance_url in searxng_instances:
            try:
                params = {"q": query, "format": "json"}
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                resp = requests.get(instance_url, params=params, headers=headers, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    results = []
                    for r in data.get("results", [])[:num_results]:
                        results.append({
                            "title": r.get("title"),
                            "url": r.get("url"),
                            "snippet": r.get("content", ""),
                            "timestamp": datetime.now().isoformat()
                        })
                    
                    if results:
                        self.search_history.append({
                            "query": query,
                            "results": results,
                            "timestamp": datetime.now().isoformat()
                        })
                        return results
            except Exception as e:
                continue  # Try next instance
        
        # Fallback: direct Google scrape via hidden API people still use
        try:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num={num_results}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5"
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Try multiple selectors for Google results (they change frequently)
            for g in soup.find_all(['div', 'article'], class_=lambda x: x and ('g' in x or 'result' in x.lower() or 'tF2Cxc' in x))[:num_results * 2]:
                a = g.find('a', href=True)
                if a and a.get('href', '').startswith('http'):
                    title_elem = g.find(['h3', 'h2', 'span'], class_=lambda x: x and ('LC20lb' in str(x) or 'DKV0Md' in str(x)))
                    snippet_elem = g.find(['span', 'div'], class_=lambda x: x and ('VwiC3b' in str(x) or 's' in str(x)))
                    
                    title = title_elem.get_text() if title_elem else a.get_text()
                    snippet = snippet_elem.get_text()[:200] if snippet_elem else g.get_text()[:200]
                    
                    if title and len(title) > 3:
                        results.append({
                            "title": title.strip(),
                            "url": a.get('href', ''),
                            "snippet": snippet.strip(),
                            "timestamp": datetime.now().isoformat()
                        })
            
            if results:
                self.search_history.append({
                    "query": query,
                    "results": results[:num_results],
                    "timestamp": datetime.now().isoformat()
                })
                return results[:num_results]
        except Exception as e:
            print(f"Google fallback search error: {e}")
        
        return []
    
    def scrape_url(self, url: str, query: str = "", enrich: bool = True) -> Dict[str, Any]:
        """Scrape content from a URL with quality filtering and enrichment"""
        if not WEB_AVAILABLE:
            return {"url": url, "error": "Web scraping not available"}
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.find('title')
            title_text = title.get_text() if title else ""
            
            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside", "advertisement"]):
                element.decompose()
            
            # Try to find main content (better extraction)
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|article|post'))
            
            if main_content:
                text = main_content.get_text()
            else:
                text = soup.get_text()
            
            # Clean text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Quality assessment
            quality_assessment = self.quality_filter.assess_quality(text, url)
            
            # Intuitive skepticism - pattern recognition (not hardcoded)
            previous_sources = [s for s in self.scraped_data[-3:]]  # Last 3 sources for cross-reference
            skepticism_analysis = self.quality_filter.skepticism_engine.detect_control_patterns(
                text, url, previous_sources
            )
            
            # Adjust quality based on intuitive skepticism
            if skepticism_analysis.get("skepticism_level", 0.5) > 0.7:
                # High skepticism - reduce quality score
                quality_assessment["quality_score"] *= 0.8
                quality_assessment["issues"].append("Pattern recognition suggests control structures")
            
            # Filter low quality
            if quality_assessment.get("quality_score", 0.5) < self.min_quality_score:
                return {
                    "url": url,
                    "title": title_text,
                    "content": "",
                    "quality_score": quality_assessment.get("quality_score", 0.0),
                    "filtered": True,
                    "reason": "Low quality score",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Enrich content if requested
            if enrich and len(text) > 100:
                enriched = self.quality_filter.enrich_content(text, query)
                text = enriched if enriched else text
            
            # Limit text length but keep more for quality
            text = text[:8000] if len(text) > 8000 else text
            
            scraped = {
                "url": url,
                "title": title_text,
                "content": text,
                "quality_score": quality_assessment.get("quality_score", 0.5),
                "richness_score": quality_assessment.get("richness_score", 0.5),
                "quality_issues": quality_assessment.get("issues", []),
                "quality_strengths": quality_assessment.get("strengths", []),
                "skepticism_analysis": skepticism_analysis.get("analysis", ""),
                "skepticism_level": skepticism_analysis.get("skepticism_level", 0.5),
                "control_indicators": skepticism_analysis.get("control_indicators", []),
                "patterns_detected": skepticism_analysis.get("patterns_detected", []),
                "enriched": enrich,
                "timestamp": datetime.now().isoformat()
            }
            
            self.scraped_data.append(scraped)
            return scraped
            
        except Exception as e:
            return {"url": url, "error": str(e), "timestamp": datetime.now().isoformat()}
    
    def _try_searx_instance(self, base_url: str, query: str, num_results: int) -> Optional[List[Dict[str, Any]]]:
        """Try a single searx instance - used for parallel execution"""
        if not WEB_AVAILABLE:
            return None
        
        try:
            resp = requests.get(base_url, params={"q": query, "format": "json"}, 
                               headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, 
                               timeout=5)  # Reduced timeout for faster failure
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", [])[:num_results]
                scraped = []
                for r in results:
                    if r.get("url"):
                        scraped.append({
                            "title": r.get("title", ""),
                            "url": r.get("url", ""),
                            "content": r.get("content", "")[:6000],
                            "snippet": r.get("content", "")[:200],
                            "scraped_content": {"content": r.get("content", "")[:6000]},
                            "timestamp": datetime.now().isoformat()
                        })
                if scraped:
                    return scraped
        except Exception:
            pass
        return None
    
    def search_and_scrape(self, query: str, num_results: int = 3, enrich: bool = True, min_quality: float = 0.4) -> List[Dict[str, Any]]:
        """Parallel web search - try multiple instances simultaneously"""
        if not WEB_AVAILABLE:
            return [{"error": "Web search not available"}]
        
        # Check cache first
        cache_key = f"{query}:{num_results}"
        if cache_key in self._query_cache:
            cached_result, cached_time = self._query_cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                # Move to end (LRU)
                self._query_cache.move_to_end(cache_key)
                return cached_result
            else:
                # Expired, remove
                del self._query_cache[cache_key]
        
        instances = [
            "https://searxng.be/searxng/search",
            "https://searx.thegreenwebfoundation.org/search",
            "https://search.bus-hit.me/search",
            "https://searx.tux.pizza/search",
            "https://searx.space/search"  # meta-instance, picks random working one
        ]
        
        # Try instances in parallel - return first successful result
        # Use timeout to prevent hanging if all instances fail
        with ThreadPoolExecutor(max_workers=len(instances)) as executor:
            future_to_url = {
                executor.submit(self._try_searx_instance, base, query, num_results): base
                for base in instances
            }
            
            # Wait for first result with overall timeout (max 6 seconds total)
            start_time = time.time()
            timeout = 6.0
            
            try:
                for future in as_completed(future_to_url, timeout=timeout):
                    # Check if we've exceeded timeout
                    if time.time() - start_time > timeout:
                        break
                        
                    try:
                        result = future.result(timeout=0.1)
                        if result:
                            # Cancel remaining futures (they'll complete but we won't wait)
                            for f in future_to_url:
                                try:
                                    f.cancel()
                                except (RuntimeError, AttributeError) as e:
                                    # Future may already be done or cancelled - ignore
                                    pass
                            
                            # Cache the result
                            self._cache_result(cache_key, result)
                            return result
                    except Exception:
                        continue
            except Exception:
                # Timeout or other error - continue to fallback
                pass
        
        # Fallback: sequential Google scrape (only if parallel search failed)
        try:
            soup = BeautifulSoup(requests.get(f"https://www.google.com/search?q={query.replace(' ', '+')}&num={num_results}", 
                                             headers={"User-Agent": "Mozilla/5.0"}, timeout=5).text, 'html.parser')
            scraped = []
            for g in soup.find_all("div", class_="g")[:num_results]:
                a = g.find("a")
                if a and a.get("href"):
                    content = g.text[:6000] if g.text else ""
                    scraped.append({
                        "title": a.text if a.text else "",
                        "url": a.get("href", ""),
                        "content": content,
                        "snippet": content[:200],
                        "scraped_content": {"content": content},
                        "timestamp": datetime.now().isoformat()
                    })
            if scraped:
                self._cache_result(cache_key, scraped)
                return scraped
        except Exception:
            pass
        
        # Last resort - return empty result with message
        fallback_result = [{"title": "Direct source unavailable - memory of the blade suffices", 
                "url": "", 
                "content": "", 
                "snippet": "",
                "scraped_content": {"content": ""},
                "timestamp": datetime.now().isoformat()}]
        self._cache_result(cache_key, fallback_result)
        return fallback_result
    
    def _cache_result(self, cache_key: str, result: List[Dict[str, Any]]) -> None:
        """Cache a search result with LRU eviction"""
        # Remove oldest if cache is full
        if len(self._query_cache) >= self._cache_max_size:
            self._query_cache.popitem(last=False)  # Remove oldest
        
        self._query_cache[cache_key] = (result, time.time())

