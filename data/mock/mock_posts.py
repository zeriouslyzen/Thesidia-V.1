"""
Mock Post Data Generator
Generates realistic posts for the stream section.
"""

import random
from typing import Dict, List, Any
from datetime import datetime, timedelta


# Sample content templates
POST_TEMPLATES = [
    "Just finished reading {topic}. The implications are fascinating.",
    "Deep dive into {topic} reveals some interesting patterns.",
    "Exploring the intersection of {topic} and consciousness.",
    "New insights on {topic} that challenge conventional thinking.",
    "The relationship between {topic} and reality is more complex than we think.",
    "Reflecting on {topic} and its deeper meaning.",
    "Breaking down {topic} from a new perspective.",
    "The hidden layers of {topic} are worth examining.",
    "Connecting the dots between {topic} and broader patterns.",
    "Questioning assumptions about {topic}."
]

TOPICS = [
    'quantum mechanics', 'consciousness', 'technology', 'philosophy',
    'artificial intelligence', 'human nature', 'society', 'creativity',
    'innovation', 'learning', 'growth', 'transformation', 'truth',
    'reality', 'perception', 'knowledge', 'wisdom', 'experience'
]


def generate_post(author_id: str = None, seed: int = None) -> Dict[str, Any]:
    """
    Generate a single post.
    
    Args:
        author_id: Author user ID.
        seed: Optional random seed for reproducibility.
    
    Returns:
        Dictionary containing post data.
    """
    if seed is not None:
        random.seed(seed)
    
    if author_id is None:
        author_id = f"user_{random.randint(1000, 9999)}"
    
    topic = random.choice(TOPICS)
    template = random.choice(POST_TEMPLATES)
    content = template.format(topic=topic)
    
    # Generate creation date (within last 30 days)
    days_ago = random.randint(0, 30)
    hours_ago = random.randint(0, 23)
    created_at = (datetime.now() - timedelta(days=days_ago, hours=hours_ago)).isoformat()
    
    post_id = f"post_{random.randint(10000, 99999)}"
    
    return {
        'id': post_id,
        'author_id': author_id,
        'content': content,
        'created_at': created_at,
        'likes': random.randint(0, 500),
        'validates': random.randint(0, 100),
        'references': random.randint(0, 50),
        'contributions': random.randint(0, 20),
        'comments': random.randint(0, 30),
        'media_url': None,  # Can be extended with media
        'tags': [topic] if random.random() > 0.5 else []
    }


def generate_posts(count: int = 20, author_ids: List[str] = None, seed: int = None) -> List[Dict[str, Any]]:
    """
    Generate multiple posts.
    
    Args:
        count: Number of posts to generate.
        author_ids: List of author IDs to use. If None, generates random ones.
        seed: Optional random seed for reproducibility.
    
    Returns:
        List of post dictionaries, sorted by created_at (newest first).
    """
    if seed is not None:
        random.seed(seed)
    
    posts = []
    for i in range(count):
        author_id = random.choice(author_ids) if author_ids else None
        post = generate_post(author_id=author_id, seed=seed + i if seed is not None else None)
        posts.append(post)
    
    # Sort by created_at (newest first)
    posts.sort(key=lambda x: x['created_at'], reverse=True)
    
    return posts

