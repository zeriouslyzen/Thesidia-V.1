#!/usr/bin/env python3
"""
Intelligent Bot Generator
Creates realistic bot profiles with synthesized content, minimal resource usage
Acts like intelligent web scraper that synthesizes data to appear real
"""

import json
import random
import secrets
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import sys
import time

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from webapp.social.post_manager import PostManager
from webapp.social.social_graph import SocialGraph
from webapp.social.interaction_manager import InteractionManager
from webapp.social.media_generator import MediaGenerator


class ContentSynthesizer:
    """
    Synthesizes realistic content by scraping patterns and generating variations
    Minimal resource usage - uses cached templates and patterns
    """
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(".")
        self.cache_dir = self.base_dir / "data" / "bot_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Content templates (cached, minimal resource)
        self.templates = self._load_templates()
        self.topics = self._load_topics()
        self.patterns = self._load_patterns()
    
    def _load_templates(self) -> Dict[str, List[str]]:
        """Load content templates from cache or generate defaults"""
        cache_file = self.cache_dir / "templates.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default templates (minimal, realistic patterns)
        templates = {
            "observations": [
                "Just noticed {topic} is more complex than I thought",
                "Thinking about {topic} today",
                "{topic} has been on my mind",
                "Anyone else interested in {topic}?",
                "Deep dive into {topic} reveals interesting patterns"
            ],
            "questions": [
                "What do you think about {topic}?",
                "Has anyone explored {topic}?",
                "Curious about {topic} - thoughts?",
                "Looking for insights on {topic}",
                "What's your take on {topic}?"
            ],
            "sharing": [
                "Found this interesting: {topic}",
                "Sharing thoughts on {topic}",
                "This {topic} thing is fascinating",
                "Worth exploring: {topic}",
                "Check this out: {topic}"
            ],
            "personal": [
                "Working on {topic} today",
                "Exploring {topic} has been rewarding",
                "My perspective on {topic}",
                "Reflecting on {topic}",
                "Learning about {topic}"
            ]
        }
        
        # Cache templates
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(templates, f, indent=2)
        
        return templates
    
    def _load_topics(self) -> List[str]:
        """Load topic list (cached, can be scraped/updated)"""
        cache_file = self.cache_dir / "topics.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default topics (realistic, diverse)
        topics = [
            "AI research", "pattern recognition", "consciousness", "technology",
            "philosophy", "science", "design", "art", "music", "writing",
            "coding", "learning", "exploration", "discovery", "innovation",
            "creativity", "problem solving", "systems thinking", "data analysis",
            "web development", "machine learning", "neural networks", "algorithms"
        ]
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(topics, f, indent=2)
        
        return topics
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load behavioral patterns (posting frequency, engagement patterns)"""
        cache_file = self.cache_dir / "patterns.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Realistic behavioral patterns
        patterns = {
            "posting_frequency": {
                "active": (1, 5),  # posts per day
                "moderate": (0.5, 2),
                "casual": (0.1, 1)
            },
            "engagement_rates": {
                "high": (0.05, 0.15),  # likes/views ratio
                "medium": (0.02, 0.08),
                "low": (0.001, 0.03)
            },
            "time_patterns": {
                "morning": (6, 10),
                "afternoon": (12, 16),
                "evening": (18, 22),
                "night": (22, 2)
            }
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(patterns, f, indent=2)
        
        return patterns
    
    def synthesize_post(
        self,
        bot_profile: Dict[str, Any],
        context: Optional[str] = None,
        use_thesidia: bool = False,
        thesidia_instance = None
    ) -> str:
        """
        Synthesize a realistic post based on bot profile
        
        Args:
            bot_profile: Bot profile with interests, personality
            context: Optional context (can scrape from web for realism)
            use_thesidia: Whether to use Thesidia for sophisticated content
            thesidia_instance: Thesidia instance (if use_thesidia=True)
            
        Returns:
            Synthesized post content
        """
        # Get bot's interests
        interests = bot_profile.get('interests', [])
        if not interests:
            interests = random.sample(self.topics, k=min(3, len(self.topics)))
        
        # Select topic
        topic = random.choice(interests)
        
        # Option 1: Use Thesidia for sophisticated content (if enabled)
        if use_thesidia and thesidia_instance:
            try:
                # Generate sophisticated post using Thesidia
                query = f"Write a short social media post about {topic} in a casual, engaging style"
                response = thesidia_instance.process(
                    query,
                    format_mode='natural',
                    research_depth=1  # Quick research
                )
                # Extract first paragraph or limit length
                content = response[:280] if len(response) > 280 else response
                # Clean up (remove any special formatting)
                content = content.split('\n')[0].strip()
                return content
            except Exception as e:
                print(f"Thesidia synthesis failed, using template: {e}")
                # Fall through to template-based generation
        
        # Option 2: Template-based generation (default, minimal resource)
        # Select template type based on personality
        personality = bot_profile.get('personality', 'moderate')
        template_type = random.choice(["observations", "questions", "sharing", "personal"])
        
        # Get template
        templates = self.templates.get(template_type, self.templates["observations"])
        template = random.choice(templates)
        
        # Fill template
        content = template.format(topic=topic)
        
        # Optionally enhance with scraped ideas
        if context and random.random() < 0.3:  # 30% chance to use scraped context
            scraped_ideas = self.scrape_and_synthesize(topic, max_results=3)
            if scraped_ideas:
                # Incorporate scraped idea naturally
                idea = random.choice(scraped_ideas)
                if len(content) + len(idea) < 200:
                    content += f" {idea[:100]}"
        
        # Add variation (emojis, hashtags, mentions - realistic frequency)
        if random.random() < 0.3:  # 30% chance of emoji
            emojis = ["🤔", "💭", "✨", "🔍", "💡", "🚀", "🎯", "🌊", "⚡", "🔥"]
            content += " " + random.choice(emojis)
        
        if random.random() < 0.2:  # 20% chance of hashtag
            hashtag = "#" + topic.replace(" ", "").lower()
            content += " " + hashtag
        
        # Add length variation (some posts longer)
        if random.random() < 0.2:  # 20% chance of longer post
            additional = [
                " What are your thoughts?",
                " Curious to hear different perspectives.",
                " Always learning something new.",
                " The deeper you go, the more interesting it gets.",
                " Anyone else exploring this?",
                " Would love to hear your take."
            ]
            content += random.choice(additional)
        
        return content
    
    def scrape_and_synthesize(self, topic: str, max_results: int = 5) -> List[str]:
        """
        Scrape web for topic ideas, then synthesize variations
        Minimal resource - caches results, uses simple scraping
        """
        cache_file = self.cache_dir / f"scraped_{topic.replace(' ', '_')}.json"
        
        # Check cache first (minimal resource)
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                    # Check if cache is fresh (24 hours)
                    if datetime.now() - datetime.fromisoformat(cached.get('cached_at', '2000-01-01')) < timedelta(hours=24):
                        return cached.get('ideas', [])
            except Exception:
                pass
        
        # Intelligent web scraping (minimal resource - cached, simple parsing)
        ideas = []
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Use DuckDuckGo HTML search (no API key, minimal resource)
            search_url = f"https://html.duckduckgo.com/html/?q={topic.replace(' ', '+')}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.ok:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract result titles (DuckDuckGo HTML structure)
                # Try multiple selectors for robustness
                selectors = [
                    'a.result__a',
                    'a.result-link',
                    '.result__title a',
                    'h2.result__title a'
                ]
                
                titles = []
                for selector in selectors:
                    titles = soup.select(selector)
                    if titles:
                        break
                
                # Extract text and clean
                ideas = []
                for title in titles[:max_results]:
                    text = title.get_text(strip=True)
                    if text and len(text) > 10:  # Filter very short titles
                        ideas.append(text)
                
                # If no titles found, try alternative approach
                if not ideas:
                    # Look for any links with topic keywords
                    links = soup.find_all('a', href=True)
                    for link in links[:max_results * 2]:
                        text = link.get_text(strip=True)
                        if topic.lower() in text.lower() and len(text) > 10:
                            ideas.append(text)
                            if len(ideas) >= max_results:
                                break
        except Exception as e:
            print(f"Scraping failed (using fallback): {e}")
        
        # Fallback: generate ideas from topic
        if not ideas:
            ideas = [
                f"Latest developments in {topic}",
                f"Exploring {topic} from different angles",
                f"Interesting patterns in {topic}",
                f"New perspectives on {topic}",
                f"Deep dive into {topic}"
            ]
        
        # Cache results
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                'ideas': ideas,
                'cached_at': datetime.now().isoformat()
            }, f, indent=2)
        
        return ideas


class BotGenerator:
    """
    Generates realistic bot profiles with intelligent behavior
    Minimal resource usage - uses cached data, batch processing
    """
    
    def __init__(self, base_dir: Path = None, use_thesidia: bool = False, thesidia_instance = None):
        self.base_dir = base_dir or Path(".")
        self.post_manager = PostManager(base_dir=base_dir)
        self.social_graph = SocialGraph(base_dir=base_dir)
        self.interaction_manager = InteractionManager(base_dir=base_dir)
        self.content_synthesizer = ContentSynthesizer(base_dir=base_dir)
        self.media_generator = MediaGenerator(base_dir=base_dir)
        
        # Thesidia integration (optional, for sophisticated content)
        self.use_thesidia = use_thesidia
        self.thesidia_instance = thesidia_instance
        
        # Bot storage
        self.bots_dir = self.base_dir / "data" / "bots"
        self.bots_dir.mkdir(parents=True, exist_ok=True)
        
        # Profile generator
        self.profile_generator = self._init_profile_generator()
        
        # Post limits for memory management
        self.max_posts_per_bot = 50  # Maximum posts per bot
        self.max_total_posts = 500  # Maximum total bot posts
        self.post_retention_days = 30  # Keep posts for 30 days
    
    def _init_profile_generator(self) -> Dict[str, List[str]]:
        """Initialize profile data (names, bios, etc.) - cached"""
        cache_file = self.bots_dir / "profile_data.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Generate realistic profile data
        profile_data = {
            "first_names": [
                "Alex", "Jordan", "Taylor", "Casey", "Morgan", "Riley", "Avery",
                "Quinn", "Sage", "River", "Phoenix", "Skyler", "Cameron", "Dakota"
            ],
            "last_names": [
                "Chen", "Martinez", "Kumar", "Anderson", "Patel", "Kim", "Singh",
                "Rodriguez", "Wang", "Brown", "Garcia", "Lee", "Johnson", "Williams"
            ],
            "bios": [
                "Exploring the intersection of technology and consciousness",
                "Researcher | Thinker | Builder",
                "Interested in patterns, systems, and emergent behavior",
                "Learning and sharing insights on AI and human cognition",
                "Building tools for deeper understanding",
                "Curious about the nature of intelligence",
                "Exploring the edges of what's possible"
            ],
            "interests": [
                ["AI research", "pattern recognition", "consciousness"],
                ["technology", "design", "innovation"],
                ["philosophy", "science", "learning"],
                ["coding", "systems thinking", "problem solving"],
                ["art", "creativity", "expression"],
                ["data analysis", "machine learning", "algorithms"]
            ]
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2)
        
        return profile_data
    
    def generate_bot_profile(self, bot_type: str = "moderate", community: str = None) -> Dict[str, Any]:
        """
        Generate a realistic bot profile
        
        Args:
            bot_type: "active", "moderate", "casual", or "community"
            community: Community/tag name (for community bots)
            
        Returns:
            Bot profile dictionary
        """
        profile_data = self.profile_generator
        
        # Generate name
        first_name = random.choice(profile_data["first_names"])
        last_name = random.choice(profile_data["last_names"])
        display_name = f"{first_name} {last_name}"
        username = f"{first_name.lower()}{last_name.lower()}{random.randint(100, 999)}"
        
        # Generate profile
        bot_id = f"bot_{secrets.token_urlsafe(12)}"
        created_at = datetime.now() - timedelta(days=random.randint(7, 365))  # Account age
        
        # Community bots have specific interests and tags
        if bot_type == "community" and community:
            interests = [community.lower()]
            bio = f"Exploring {community} | Community member | Sharing insights"
            tags = [community.lower()]
        else:
            interests = random.choice(profile_data["interests"])
            bio = random.choice(profile_data["bios"])
            tags = []
        
        # More realistic avatar images (AI / real-style portraits)
        # Using curated Pexels portrait URLs (royalty-free stock)
        portrait_avatars = [
            "https://images.pexels.com/photos/415829/pexels-photo-415829.jpeg",
            "https://images.pexels.com/photos/2379004/pexels-photo-2379004.jpeg",
            "https://images.pexels.com/photos/1181519/pexels-photo-1181519.jpeg",
            "https://images.pexels.com/photos/733872/pexels-photo-733872.jpeg",
            "https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg",
            "https://images.pexels.com/photos/1130626/pexels-photo-1130626.jpeg",
            "https://images.pexels.com/photos/3680211/pexels-photo-3680211.jpeg",
            "https://images.pexels.com/photos/936234/pexels-photo-936234.jpeg",
            "https://images.pexels.com/photos/1834399/pexels-photo-1834399.jpeg",
            "https://images.pexels.com/photos/1239291/pexels-photo-1239291.jpeg"
        ]
        base_avatar = random.choice(portrait_avatars)
        # Add transformation params for better cropping and quality
        avatar_url = (
            f"{base_avatar}?auto=compress&cs=tinysrgb&w=400&h=400&fit=crop&dpr=2"
        )
        
        profile = {
            "bot_id": bot_id,
            "user_id": bot_id,  # Same as bot_id for simplicity
            "display_name": display_name,
            "username": username,
            "bio": bio,
            "interests": interests,
            "personality": bot_type,
            "created_at": created_at.isoformat(),
            "avatar_url": avatar_url,
            "is_bot": True,
            "bot_type": bot_type,
            "community": community if bot_type == "community" else None,
            "tags": tags,
            "activity_level": {
                "active": (1, 5),
                "moderate": (0.5, 2),
                "casual": (0.1, 1),
                "community": (2, 6)  # Community bots post more
            }.get(bot_type, (0.5, 2))
        }
        
        # Save profile
        profile_file = self.bots_dir / f"{bot_id}.json"
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        
        return profile
    
    def create_bot_user(self, bot_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create actual user account for bot
        
        Args:
            bot_profile: Bot profile dictionary
            
        Returns:
            User data dictionary
        """
        # Create user directory structure
        user_dir = self.base_dir / "data" / "users" / bot_profile["user_id"]
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Create user info
        user_info = {
            "user_id": bot_profile["user_id"],
            "username": bot_profile["username"],
            "display_name": bot_profile["display_name"],
            "bio": bot_profile["bio"],
            "avatar_url": bot_profile["avatar_url"],
            "created_at": bot_profile["created_at"],
            "is_bot": True,
            "bot_type": bot_profile["bot_type"]
        }
        
        user_info_file = user_dir / "user_info.json"
        with open(user_info_file, 'w', encoding='utf-8') as f:
            json.dump(user_info, f, indent=2, ensure_ascii=False)
        
        # Create profile.json for settings system
        profile_file = user_dir / "profile.json"
        profile_data = {
            "user_id": bot_profile["user_id"],
            "username": bot_profile["username"],
            "display_name": bot_profile["display_name"],
            "bio": bot_profile["bio"],
            "avatar_url": bot_profile["avatar_url"],
            "location": "",
            "website": ""
        }
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)
        
        return user_info
    
    def generate_bot_activity(
        self,
        bot_id: str,
        days: int = 30,
        posts_per_day_range: tuple = (0.5, 3),
        all_bot_ids: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate realistic activity for a bot over time period
        
        Args:
            bot_id: Bot user ID
            days: Number of days to generate activity for
            posts_per_day_range: (min, max) posts per day
            all_bot_ids: List of all bot IDs for engagement generation
            
        Returns:
            Activity summary
        """
        # Load bot profile
        profile_file = self.bots_dir / f"{bot_id}.json"
        if not profile_file.exists():
            raise ValueError(f"Bot {bot_id} not found")
        
        with open(profile_file, 'r', encoding='utf-8') as f:
            bot_profile = json.load(f)
        
        # Check post limit for this bot
        existing_posts = self.post_manager.get_posts_by_user(bot_id, limit=1000)
        if len(existing_posts) >= self.max_posts_per_bot:
            return {
                "bot_id": bot_id,
                "posts_created": 0,
                "interactions_created": 0,
                "days": days,
                "message": f"Bot has reached max posts limit ({self.max_posts_per_bot})"
            }
        
        posts_created = 0
        interactions_created = 0
        
        # Generate activity over time
        start_date = datetime.now() - timedelta(days=days)
        
        for day in range(days):
            # Calculate posts for this day (realistic variation)
            posts_today = random.randint(
                int(posts_per_day_range[0] * 10),
                int(posts_per_day_range[1] * 10)
            ) / 10.0
            
            # Generate posts (distributed throughout day)
            for _ in range(int(posts_today)):
                # Random time during day (realistic pattern)
                hour = random.randint(6, 23)
                minute = random.randint(0, 59)
                post_time = start_date + timedelta(days=day, hours=hour, minutes=minute)
                
                # Synthesize post content (with optional Thesidia enhancement)
                content = self.content_synthesizer.synthesize_post(
                    bot_profile,
                    use_thesidia=self.use_thesidia,
                    thesidia_instance=self.thesidia_instance
                )
                
                # Generate media for post
                # Community bots: 60% media, Labs-focused: 80% media, Regular: 40% media
                media = []
                bot_type = bot_profile.get('bot_type', 'moderate')
                media_chance = 0.8 if bot_type == "community" else 0.4
                
                if random.random() < media_chance:
                    topic = random.choice(bot_profile.get('interests', ['technology']))
                    # Community bots prefer images/videos, Labs prefer all media types
                    post_type = "random" if bot_type == "community" else "random"
                    media = self.media_generator.generate_media_for_post(
                        post_type=post_type,
                        topic=topic
                    )
                
                # Generate tags
                tags = []
                if bot_type == "community" and bot_profile.get('community'):
                    # Community bots always tag their community
                    tags = [bot_profile.get('community').lower()]
                elif random.random() < 0.3:  # 30% of regular posts have tags
                    # Add tags based on interests
                    interests = bot_profile.get('interests', [])
                    if interests:
                        tag = random.choice(interests).lower().replace(' ', '')
                        tags = [tag]
                
                # Create post with media and tags
                try:
                    post = self.post_manager.create_post(
                        author_id=bot_id,
                        content=content,
                        media=media if media else None,
                        tags=tags if tags else None,
                        visibility="public"
                    )
                    posts_created += 1
                    
                    # Update post timestamp to match generated time
                    post['created_at'] = post_time.isoformat()
                    post_file = self.post_manager.posts_dir / f"{post['id']}.json"
                    with open(post_file, 'w', encoding='utf-8') as f:
                        json.dump(post, f, indent=2, ensure_ascii=False)
                    
                    # Generate realistic engagement (with delay)
                    if random.random() < 0.7:  # 70% of posts get engagement
                        self._generate_engagement(post['id'], post_time, bot_profile, all_bot_ids)
                        interactions_created += 1
                    
                    # Check total post limit
                    total_posts = len(list(self.post_manager.posts_dir.glob("*.json")))
                    if total_posts >= self.max_total_posts:
                        print(f"Reached max total posts limit ({self.max_total_posts}), stopping generation")
                        break
                    
                    # Small delay to avoid overwhelming system
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"Error creating post: {e}")
                    continue
        
        return {
            "bot_id": bot_id,
            "posts_created": posts_created,
            "interactions_created": interactions_created,
            "days": days
        }
    
    def _generate_engagement(
        self,
        post_id: str,
        post_time: datetime,
        bot_profile: Dict[str, Any],
        all_bot_ids: List[str] = None
    ):
        """Generate realistic engagement on a post with actual likes and comments"""
        # Engagement happens over time (not instant)
        engagement_delay_hours = random.randint(1, 48)
        engagement_time = post_time + timedelta(hours=engagement_delay_hours)
        
        # Realistic engagement rates
        views = random.randint(10, 500)
        likes_count = int(views * random.uniform(0.02, 0.10))  # 2-10% like rate
        comments_count = int(likes_count * random.uniform(0.1, 0.3))  # 10-30% comment rate
        reposts_count = int(likes_count * random.uniform(0.05, 0.15))  # 5-15% repost rate
        
        # Get other bots to like/comment (if available)
        if all_bot_ids:
            # Select random bots to like
            liking_bots = random.sample(
                [b for b in all_bot_ids if b != bot_profile.get('bot_id')],
                min(likes_count, len(all_bot_ids) - 1)
            ) if len(all_bot_ids) > 1 else []
            
            # Actually like the post
            for bot_id in liking_bots:
                try:
                    self.interaction_manager.like_post(post_id, bot_id)
                except Exception:
                    pass
            
            # Generate comments from other bots
            commenting_bots = random.sample(
                [b for b in all_bot_ids if b != bot_profile.get('bot_id')],
                min(comments_count, len(all_bot_ids) - 1)
            ) if len(all_bot_ids) > 1 else []
            
            # Generate comments -- use Thesidia stream analysis when available,
            # falling back to simple templates otherwise.
            comment_templates = [
                "Great point!",
                "Interesting perspective",
                "I agree with this",
                "This resonates",
                "Thanks for sharing",
                "Love this!",
                "So true",
                "Exactly!",
                "Well said",
                "This is helpful"
            ]
            
            # Attempt fact-check comment via Thesidia stream_analyze (at most once per post)
            fact_check_comment = None
            if self.use_thesidia and self.thesidia_instance and hasattr(self.thesidia_instance, 'stream_analyze'):
                try:
                    # Retrieve the post content for analysis
                    post_file_check = self.post_manager.posts_dir / f"{post_id}.json"
                    if post_file_check.exists():
                        with open(post_file_check, 'r', encoding='utf-8') as f:
                            post_data = json.load(f)
                        post_content = post_data.get('content', post_data.get('text', ''))
                        if post_content and len(post_content) > 30:
                            analysis = self.thesidia_instance.stream_analyze(
                                post_content=post_content, post_id=post_id
                            )
                            # Extract a short summary line for the comment
                            # Use the verdict line if present, else first two lines
                            for line in analysis.split('\n'):
                                if 'Verdict:' in line or 'Truth Score:' in line:
                                    fact_check_comment = line.strip()
                                    break
                            if not fact_check_comment and analysis:
                                fact_check_comment = analysis.split('\n')[0][:140]
                except Exception as e:
                    print(f"Bot fact-check comment failed (non-fatal): {e}")
            
            for i, bot_id in enumerate(commenting_bots):
                try:
                    # First commenter uses fact-check if available
                    if i == 0 and fact_check_comment:
                        comment_text = fact_check_comment
                    else:
                        comment_text = random.choice(comment_templates)
                    self.interaction_manager.comment_post(post_id, bot_id, comment_text)
                except Exception:
                    pass
        
        # Update post's interaction counts
        post_file = self.post_manager.posts_dir / f"{post_id}.json"
        if post_file.exists():
            try:
                with open(post_file, 'r', encoding='utf-8') as f:
                    post = json.load(f)
                
                # Get actual interaction counts
                interactions = self.interaction_manager.get_interactions(post_id)
                actual_likes = len(interactions.get('likes', []))
                actual_comments = len(interactions.get('comments', []))
                
                post['interactions'] = {
                    'views': views,
                    'likes': actual_likes if actual_likes > 0 else likes_count,
                    'comments': actual_comments if actual_comments > 0 else comments_count,
                    'reposts': reposts_count,
                    'updated_at': engagement_time.isoformat()
                }
                
                with open(post_file, 'w', encoding='utf-8') as f:
                    json.dump(post, f, indent=2, ensure_ascii=False)
            except Exception:
                pass
    
    def build_bot_network(self, bot_ids: List[str], connection_probability: float = 0.3):
        """
        Build realistic social network between bots
        
        Args:
            bot_ids: List of bot user IDs
            connection_probability: Probability of connection between any two bots
        """
        connections = 0
        
        for i, bot1 in enumerate(bot_ids):
            for bot2 in bot_ids[i+1:]:
                if random.random() < connection_probability:
                    # Randomly decide who follows whom
                    if random.random() < 0.5:
                        self.social_graph.follow_user(bot1, bot2)
                    else:
                        self.social_graph.follow_user(bot2, bot1)
                    connections += 1
        
        return {"connections_created": connections}
    
    def generate_community_bots(
        self,
        communities: List[str] = None,
        bots_per_community: int = 3,
        generate_activity: bool = True,
        days_of_activity: int = 30
    ) -> Dict[str, Any]:
        """
        Generate community bots that post to specific communities/tags
        
        Args:
            communities: List of community names (default: auto-generate)
            bots_per_community: Number of bots per community
            generate_activity: Whether to generate activity
            days_of_activity: Days of activity to generate
            
        Returns:
            Summary of generated community bots
        """
        if communities is None:
            communities = [
                "technology", "ai", "coding", "design", "art", "music",
                "fitness", "wellness", "travel", "food", "photography",
                "writing", "philosophy", "science", "innovation"
            ]
        
        bots_created = []
        
        for community in communities:
            for i in range(bots_per_community):
                # Generate community bot profile
                bot_profile = self.generate_bot_profile(
                    bot_type="community",
                    community=community
                )
                
                # Create user
                user_info = self.create_bot_user(bot_profile)
                
                bots_created.append({
                    "bot_id": bot_profile["bot_id"],
                    "username": bot_profile["username"],
                    "display_name": bot_profile["display_name"],
                    "bot_type": "community",
                    "community": community
                })
                
                # Generate activity if requested
                if generate_activity:
                    activity_range = (2, 6)  # Community bots post more
                    
                    try:
                        # Pass all bot IDs for engagement generation
                        all_bot_ids = [b["bot_id"] for b in bots_created]
                        self.generate_bot_activity(
                            bot_profile["bot_id"],
                            days=days_of_activity,
                            posts_per_day_range=activity_range,
                            all_bot_ids=all_bot_ids
                        )
                    except Exception as e:
                        print(f"Error generating activity for {bot_profile['bot_id']}: {e}")
                
                # Small delay
                time.sleep(0.2)
        
        # Build network between community bots
        bot_ids = [b["bot_id"] for b in bots_created]
        network = self.build_bot_network(bot_ids, connection_probability=0.4)  # Higher connection rate
        
        return {
            "bots_created": len(bots_created),
            "bots": bots_created,
            "communities": communities,
            "network_connections": network["connections_created"]
        }
    
    def generate_bot_army(
        self,
        count: int = 10,
        bot_types: List[str] = None,
        generate_activity: bool = True,
        days_of_activity: int = 30
    ) -> Dict[str, Any]:
        """
        Generate multiple bots with activity (minimal resource usage)
        
        Args:
            count: Number of bots to generate
            bot_types: List of bot types (default: mix)
            generate_activity: Whether to generate activity
            days_of_activity: Days of activity to generate
            
        Returns:
            Summary of generated bots
        """
        if bot_types is None:
            bot_types = ["active", "moderate", "casual"]
        
        bots_created = []
        
        for i in range(count):
            bot_type = random.choice(bot_types)
            
            # Generate profile
            bot_profile = self.generate_bot_profile(bot_type=bot_type)
            
            # Create user
            user_info = self.create_bot_user(bot_profile)
            
            bots_created.append({
                "bot_id": bot_profile["bot_id"],
                "username": bot_profile["username"],
                "display_name": bot_profile["display_name"],
                "bot_type": bot_type
            })
            
            # Generate activity if requested
            if generate_activity:
                activity_range = {
                    "active": (2, 5),
                    "moderate": (0.5, 2),
                    "casual": (0.1, 1)
                }.get(bot_type, (0.5, 2))
                
                try:
                    # Pass all bot IDs for engagement generation
                    all_bot_ids = [b["bot_id"] for b in bots_created]
                    self.generate_bot_activity(
                        bot_profile["bot_id"],
                        days=days_of_activity,
                        posts_per_day_range=activity_range,
                        all_bot_ids=all_bot_ids
                    )
                except Exception as e:
                    print(f"Error generating activity for {bot_profile['bot_id']}: {e}")
            
            # Small delay to avoid overwhelming system
            time.sleep(0.2)
        
        # Build network between bots
        bot_ids = [b["bot_id"] for b in bots_created]
        network = self.build_bot_network(bot_ids)
        
        return {
            "bots_created": len(bots_created),
            "bots": bots_created,
            "network_connections": network["connections_created"]
        }

