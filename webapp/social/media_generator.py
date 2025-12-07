#!/usr/bin/env python3
"""
Media Generator for Bot Posts
Generates realistic images, GIFs, and videos for bot posts
Uses free APIs: Unsplash, Pexels, Giphy
"""

import random
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from datetime import datetime, timedelta


class MediaGenerator:
    """
    Generates media URLs for bot posts
    Uses free APIs with caching to minimize resource usage
    """
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(".")
        self.cache_dir = self.base_dir / "data" / "bot_cache" / "media"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Free API endpoints (no API keys needed for basic usage)
        self.unsplash_base = "https://source.unsplash.com"
        self.pexels_base = "https://images.pexels.com/photos"
        self.giphy_base = "https://api.giphy.com/v1/gifs"
        
        # Cache for media URLs
        self.media_cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, List[str]]:
        """Load cached media URLs"""
        cache_file = self.cache_dir / "media_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "images": [],
            "gifs": [],
            "videos": []
        }
    
    def _save_cache(self):
        """Save media cache"""
        cache_file = self.cache_dir / "media_cache.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.media_cache, f, indent=2)
    
    def generate_image(self, topic: str = None, width: int = 800, height: int = 600) -> str:
        """
        Generate realistic image URL
        
        Args:
            topic: Topic keyword for image search
            width: Image width
            height: Image height
            
        Returns:
            Image URL
        """
        # Use Unsplash Source API (no key needed, random images)
        # Bias towards realistic portraits / people to make the feed feel more human.
        if topic:
            # Combine portrait / person keywords with the topic
            base_keywords = "portrait,person,face,closeup"
            topic_keywords = topic.lower().replace(' ', ',')
            keywords = f"{base_keywords},{topic_keywords}"
            url = f"{self.unsplash_base}/{width}x{height}/?{keywords}"
        else:
            # Generic portrait / people images
            url = f"{self.unsplash_base}/{width}x{height}/?portrait,person,face"
        
        # Cache URL
        if url not in self.media_cache["images"]:
            self.media_cache["images"].append(url)
            if len(self.media_cache["images"]) > 100:
                self.media_cache["images"] = self.media_cache["images"][-100:]  # Keep last 100
            self._save_cache()
        
        return url
    
    def generate_gif(self, topic: str = None) -> str:
        """
        Generate GIF URL
        
        Args:
            topic: Topic keyword for GIF search
            
        Returns:
            GIF URL
        """
        # Use Giphy's public API (trending GIFs, no key needed for basic)
        # Or use a curated list of free GIF URLs
        gif_urls = [
            "https://media.giphy.com/media/3o7aD2saQqpyIMYKw0/giphy.gif",  # Celebration
            "https://media.giphy.com/media/l0MYC0LajbaPoEADu/giphy.gif",  # Thinking
            "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif",  # Success
            "https://media.giphy.com/media/l0HlBO7eyXzSZkJri/giphy.gif",  # Excited
            "https://media.giphy.com/media/26BRuo6sLetdllPAQ/giphy.gif",  # Happy
            "https://media.giphy.com/media/3o7aCTPPm4OHfRLSH6/giphy.gif",  # Working
            "https://media.giphy.com/media/l0HlNQ03J5JxX6lva/giphy.gif",  # Creative
            "https://media.giphy.com/media/3o7abldf0PId4KYRd2/giphy.gif",  # Learning
        ]
        
        # Select random or topic-based
        url = random.choice(gif_urls)
        
        # Cache URL
        if url not in self.media_cache["gifs"]:
            self.media_cache["gifs"].append(url)
            self._save_cache()
        
        return url
    
    def generate_video(self, topic: str = None, duration: int = 15) -> str:
        """
        Generate short video URL
        
        Args:
            topic: Topic keyword
            duration: Video duration in seconds
            
        Returns:
            Video URL
        """
        # Use Pexels Videos API (free, no key for basic usage)
        # Or use curated list of free video URLs
        video_urls = [
            "https://videos.pexels.com/video-files/3045163/3045163-hd_1920_1080_30fps.mp4",  # Nature
            "https://videos.pexels.com/video-files/2491284/2491284-hd_1920_1080_30fps.mp4",  # Workout
            "https://videos.pexels.com/video-files/3045163/3045163-hd_1920_1080_30fps.mp4",  # Tech
            "https://videos.pexels.com/video-files/2491284/2491284-hd_1920_1080_30fps.mp4",  # Creative
        ]
        
        url = random.choice(video_urls)
        
        # Cache URL
        if url not in self.media_cache["videos"]:
            self.media_cache["videos"].append(url)
            self._save_cache()
        
        return url
    
    def generate_multiple_images(self, count: int = 2, topic: str = None) -> List[Dict[str, Any]]:
        """
        Generate multiple images for a post
        
        Args:
            count: Number of images (2-4)
            topic: Topic keyword
            
        Returns:
            List of image media objects
        """
        count = max(2, min(4, count))  # Limit to 2-4 images
        images = []
        
        for i in range(count):
            url = self.generate_image(topic=topic, width=800, height=600)
            images.append({
                "type": "image",
                "url": url,
                "thumbnail": url.replace("800x600", "400x300")
            })
        
        return images
    
    def generate_media_for_post(self, post_type: str = "random", topic: str = None) -> List[Dict[str, Any]]:
        """
        Generate appropriate media for a post type
        
        Args:
            post_type: "image", "gif", "video", "multiple_images", "none", "random"
            topic: Topic keyword
            
        Returns:
            List of media objects
        """
        if post_type == "none":
            return []
        
        if post_type == "random":
            # 40% image, 20% gif, 15% video, 15% multiple images, 10% none
            rand = random.random()
            if rand < 0.4:
                post_type = "image"
            elif rand < 0.6:
                post_type = "gif"
            elif rand < 0.75:
                post_type = "video"
            elif rand < 0.9:
                post_type = "multiple_images"
            else:
                post_type = "none"
        
        if post_type == "image":
            url = self.generate_image(topic=topic)
            return [{
                "type": "image",
                "url": url,
                "thumbnail": url.replace("800x600", "400x300")
            }]
        
        elif post_type == "gif":
            url = self.generate_gif(topic=topic)
            return [{
                "type": "gif",
                "url": url,
                "thumbnail": url
            }]
        
        elif post_type == "video":
            url = self.generate_video(topic=topic)
            return [{
                "type": "video",
                "url": url,
                "thumbnail": url.replace(".mp4", ".jpg") if ".mp4" in url else url,
                "duration": random.randint(10, 30)
            }]
        
        elif post_type == "multiple_images":
            count = random.randint(2, 4)
            return self.generate_multiple_images(count=count, topic=topic)
        
        return []

