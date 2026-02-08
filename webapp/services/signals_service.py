"""
Signals Service - Fetches curated news signals from Brave Search API
with fallback to static curated content.
"""
import os
import json
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import urllib.request
import urllib.parse
import urllib.error


class SignalsService:
    """
    Service for fetching curated news signals.
    
    Sources:
    1. Brave Search API (primary) - Real-time news
    2. Static curated content (fallback) - Manual curation
    """
    
    # Cache for API responses (in-memory)
    _cache: Dict[str, tuple] = {}  # key -> (data, timestamp)
    CACHE_TTL = 1800  # 30 minutes
    
    # Default topics for signal discovery
    DEFAULT_TOPICS = [
        "AI artificial intelligence",
        "technology innovation",
        "business entrepreneurship",
        "personal development mastery",
        "philosophy wisdom"
    ]
    
    def __init__(self, api_key: Optional[str] = None, base_dir: Optional[str] = None):
        """
        Initialize the signals service.
        
        Args:
            api_key: Brave Search API key. If not provided, reads from BRAVE_API_KEY env var.
            base_dir: Base directory for static content. Defaults to webapp directory.
        """
        self.api_key = api_key or os.environ.get('BRAVE_API_KEY', '')
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent
        self.curated_path = self.base_dir / 'data' / 'curated_signals.json'
        
    def get_signals(
        self, 
        limit: int = 6, 
        topic: Optional[str] = None,
        include_curated: bool = True
    ) -> Dict[str, Any]:
        """
        Get signals from all sources.
        
        Args:
            limit: Maximum number of signals to return
            topic: Search topic/query (uses defaults if not provided)
            include_curated: Whether to include static curated content
            
        Returns:
            Dict with 'featured' signal, 'signals' list and 'source' info
        """
        signals = []
        sources_used = []
        featured = None
        
        # Load featured article (always from curated)
        featured = self._load_featured_signal()
        
        # Try Brave Search API first for dynamic signals
        if self.api_key:
            try:
                brave_signals = self._fetch_brave_news(topic or "technology AI innovation", limit)
                if brave_signals:
                    signals.extend(brave_signals)
                    sources_used.append('brave')
            except Exception as e:
                print(f"⚠️ Brave Search API error: {e}")
        
        # Add curated content if needed
        if include_curated and len(signals) < limit:
            try:
                curated = self._load_curated_signals(limit - len(signals))
                if curated:
                    signals.extend(curated)
                    sources_used.append('curated')
            except Exception as e:
                print(f"⚠️ Curated signals error: {e}")
        
        # Deduplicate by title similarity
        signals = self._deduplicate(signals)
        
        return {
            'featured': featured,
            'signals': signals[:limit],
            'sources': sources_used,
            'count': len(signals[:limit]),
            'cached': self._is_cached(topic or "default")
        }
    
    def _load_featured_signal(self) -> Optional[Dict]:
        """Load the pinned featured signal from curated JSON."""
        if not self.curated_path.exists():
            return self._get_default_featured()
        
        try:
            with open(self.curated_path, 'r') as f:
                data = json.load(f)
            
            # New structure has 'featured' key
            if isinstance(data, dict) and 'featured' in data:
                featured = data['featured']
                featured['source'] = 'curated'
                featured['pinned'] = True
                return featured
            
            return self._get_default_featured()
        except Exception as e:
            print(f"Error loading featured signal: {e}")
            return self._get_default_featured()
    
    def _get_default_featured(self) -> Dict:
        """Default featured article."""
        return {
            'id': 'featured_neuroplasticity',
            'title': 'The Science of Neuroplasticity',
            'tag': 'Neuroscience',
            'excerpt': 'Your brain can rewire itself at any age. New research reveals how deliberate practice reshapes neural pathways.',
            'image': '/assets/neuroplasticity-featured.webp',
            'url': '#',
            'source': 'curated',
            'pinned': True,
            'timestamp': datetime.now().isoformat()
        }
    
    def _fetch_brave_news(self, query: str, limit: int = 6) -> List[Dict]:
        """
        Fetch news from Brave Search API.
        
        Uses the /web/search endpoint with news focus.
        """
        cache_key = f"brave_{hashlib.md5(query.encode()).hexdigest()}"
        
        # Check cache
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self.CACHE_TTL:
                return data
        
        # Build request
        base_url = "https://api.search.brave.com/res/v1/web/search"
        params = {
            'q': query,
            'count': min(limit * 2, 20),  # Fetch extra for filtering
            'search_lang': 'en',
            'result_filter': 'news',
            'freshness': 'pw'  # Past week
        }
        
        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        
        req = urllib.request.Request(url)
        req.add_header('Accept', 'application/json')
        req.add_header('X-Subscription-Token', self.api_key)
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            print(f"Brave API HTTP Error: {e.code} - {e.reason}")
            return []
        except Exception as e:
            print(f"Brave API Error: {e}")
            return []
        
        # Parse results
        signals = []
        news_results = data.get('news', {}).get('results', [])
        
        # Fallback to web results if no news
        if not news_results:
            news_results = data.get('web', {}).get('results', [])
        
        for i, result in enumerate(news_results[:limit]):
            signal = {
                'id': f"brave_{hashlib.md5(result.get('url', str(i)).encode()).hexdigest()[:8]}",
                'title': result.get('title', 'Untitled'),
                'tag': self._extract_tag(result),
                'excerpt': result.get('description', '')[:200],
                'image': result.get('thumbnail', {}).get('src', '') or self._get_placeholder_image(query),
                'url': result.get('url', ''),
                'source': 'brave',
                'timestamp': result.get('age', datetime.now().isoformat()),
                'source_name': result.get('meta_url', {}).get('hostname', 'Web')
            }
            signals.append(signal)
        
        # Cache results
        self._cache[cache_key] = (signals, time.time())
        
        return signals
    
    def _load_curated_signals(self, limit: int = 6) -> List[Dict]:
        """Load static curated signals from JSON file."""
        if not self.curated_path.exists():
            return self._get_default_curated()[:limit]
        
        try:
            with open(self.curated_path, 'r') as f:
                data = json.load(f)
            
            # New structure has 'signals' key
            if isinstance(data, dict) and 'signals' in data:
                curated = data['signals']
            elif isinstance(data, list):
                curated = data  # Old array format
            else:
                return self._get_default_curated()[:limit]
            
            # Mark as curated source
            for signal in curated:
                signal['source'] = 'curated'
            
            return curated[:limit]
        except Exception as e:
            print(f"Error loading curated signals: {e}")
            return self._get_default_curated()[:limit]
    
    def _get_default_curated(self) -> List[Dict]:
        """Default curated content when JSON file doesn't exist."""
        return [
            {
                'id': 'cur_1',
                'title': 'The Rise of Local AI Models',
                'tag': 'AI Research',
                'excerpt': 'How local models like Ollama and MLX are democratizing AI access for developers and researchers.',
                'image': '/assets/placeholder-ai.webp',
                'url': '#',
                'source': 'curated',
                'timestamp': datetime.now().isoformat()
            },
            {
                'id': 'cur_2', 
                'title': 'Mastery Through Deliberate Practice',
                'tag': 'Personal Growth',
                'excerpt': 'New research on skill acquisition reveals the compound effect of focused, intentional practice.',
                'image': '/assets/placeholder-mastery.webp',
                'url': '#',
                'source': 'curated',
                'timestamp': datetime.now().isoformat()
            },
            {
                'id': 'cur_3',
                'title': 'The Philosophy of Flow States',
                'tag': 'Philosophy',
                'excerpt': 'Ancient wisdom meets modern neuroscience in understanding peak performance and presence.',
                'image': '/assets/placeholder-flow.webp',
                'url': '#',
                'source': 'curated',
                'timestamp': datetime.now().isoformat()
            },
            {
                'id': 'cur_4',
                'title': 'Building Sustainable Businesses',
                'tag': 'Business',
                'excerpt': 'Entrepreneurs share insights on creating ventures that serve both profit and purpose.',
                'image': '/assets/placeholder-business.webp',
                'url': '#',
                'source': 'curated',
                'timestamp': datetime.now().isoformat()
            },
            {
                'id': 'cur_5',
                'title': 'The Intersection of Art and Technology',
                'tag': 'Creative Tech',
                'excerpt': 'Artists are using AI tools not to replace creativity, but to amplify human expression.',
                'image': '/assets/placeholder-art.webp',
                'url': '#',
                'source': 'curated',
                'timestamp': datetime.now().isoformat()
            },
            {
                'id': 'cur_6',
                'title': 'Movement as Medicine',
                'tag': 'Wellness',
                'excerpt': 'The science behind why physical practice transforms not just the body, but the mind.',
                'image': '/assets/placeholder-movement.webp',
                'url': '#',
                'source': 'curated',
                'timestamp': datetime.now().isoformat()
            }
        ]
    
    def _extract_tag(self, result: Dict) -> str:
        """Extract a tag/category from search result."""
        # Try to infer from URL or title
        url = result.get('url', '').lower()
        title = result.get('title', '').lower()
        
        tag_map = {
            'ai': 'AI Research',
            'artificial intelligence': 'AI Research',
            'machine learning': 'AI Research',
            'tech': 'Technology',
            'business': 'Business',
            'startup': 'Business',
            'philosophy': 'Philosophy',
            'science': 'Science',
            'health': 'Wellness',
            'fitness': 'Wellness',
            'art': 'Creative',
            'design': 'Creative',
            'psychology': 'Mind',
            'meditation': 'Mindfulness'
        }
        
        combined = f"{url} {title}"
        for keyword, tag in tag_map.items():
            if keyword in combined:
                return tag
        
        return 'Signals'
    
    def _get_placeholder_image(self, query: str) -> str:
        """Get a placeholder image based on query."""
        # Use gradient placeholders based on topic
        if 'ai' in query.lower() or 'tech' in query.lower():
            return '/assets/placeholder-ai.webp'
        elif 'business' in query.lower():
            return '/assets/placeholder-business.webp'
        else:
            return '/assets/placeholder-signal.webp'
    
    def _deduplicate(self, signals: List[Dict]) -> List[Dict]:
        """Remove duplicate signals based on title similarity."""
        seen_titles = set()
        unique = []
        
        for signal in signals:
            # Normalize title for comparison
            normalized = signal.get('title', '').lower().strip()[:50]
            if normalized and normalized not in seen_titles:
                seen_titles.add(normalized)
                unique.append(signal)
        
        return unique
    
    def _is_cached(self, query: str) -> bool:
        """Check if query results are cached."""
        cache_key = f"brave_{hashlib.md5(query.encode()).hexdigest()}"
        if cache_key in self._cache:
            _, timestamp = self._cache[cache_key]
            return time.time() - timestamp < self.CACHE_TTL
        return False
    
    def clear_cache(self):
        """Clear the signal cache."""
        self._cache.clear()


# Singleton instance
_signals_service: Optional[SignalsService] = None

def get_signals_service(api_key: Optional[str] = None, base_dir: Optional[str] = None) -> SignalsService:
    """Get or create the singleton signals service instance."""
    global _signals_service
    if _signals_service is None:
        _signals_service = SignalsService(api_key=api_key, base_dir=base_dir)
    return _signals_service
