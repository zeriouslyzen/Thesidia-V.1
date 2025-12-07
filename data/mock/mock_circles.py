"""
Mock Circles Data Generator
Generates forum threads and discussions for the circles section.
"""

import random
from typing import Dict, List, Any
from datetime import datetime, timedelta


# Thread titles
THREAD_TITLES = [
    "What are your thoughts on {topic}?",
    "Discussion: {topic}",
    "Exploring {topic} together",
    "Deep dive into {topic}",
    "The truth about {topic}",
    "Understanding {topic}",
    "Question about {topic}",
    "Insights on {topic}",
    "Breaking down {topic}",
    "Thoughts on {topic}?"
]

THREAD_BODIES = [
    "I've been thinking about {topic} lately and wanted to get the community's perspective. What do you all think?",
    "Let's discuss {topic}. There are many layers to explore here.",
    "I've noticed some interesting patterns related to {topic}. Would love to hear your experiences.",
    "The relationship between {topic} and our understanding of reality is fascinating.",
    "What are the deeper implications of {topic}?",
    "I'm curious about the community's take on {topic}.",
    "There's more to {topic} than meets the eye. Let's unpack it together.",
    "How does {topic} relate to your personal experience?",
    "The intersection of {topic} and consciousness is worth exploring.",
    "What questions do you have about {topic}?"
]

CIRCLE_TOPICS = [
    'philosophy', 'yoga', 'science', 'pilates', 'martial arts',
    'business', 'celestial', 'emerging', 'consciousness', 'technology',
    'art', 'creativity', 'learning', 'growth', 'wisdom',
    'truth', 'reality', 'perception', 'knowledge', 'transformation',
    'evolution', 'mind', 'spirit', 'nature', 'society', 'innovation'
]


def generate_thread(author_id: str = None, seed: int = None) -> Dict[str, Any]:
    """
    Generate a single forum thread.
    
    Args:
        author_id: Author user ID.
        seed: Optional random seed for reproducibility.
    
    Returns:
        Dictionary containing thread data.
    """
    if seed is not None:
        random.seed(seed)
    
    if author_id is None:
        author_id = f"user_{random.randint(1000, 9999)}"
    
    topic = random.choice(CIRCLE_TOPICS)
    title_template = random.choice(THREAD_TITLES)
    body_template = random.choice(THREAD_BODIES)
    
    title = title_template.format(topic=topic)
    body = body_template.format(topic=topic)
    
    # Generate creation date (within last 14 days)
    days_ago = random.randint(0, 14)
    hours_ago = random.randint(0, 23)
    created_at = (datetime.now() - timedelta(days=days_ago, hours=hours_ago)).isoformat()
    
    thread_id = f"thread_{random.randint(10000, 99999)}"
    
    return {
        'id': thread_id,
        'author_id': author_id,
        'title': title,
        'body': body,
        'created_at': created_at,
        'upvotes': random.randint(0, 500),
        'downvotes': random.randint(0, 50),
        'comment_count': random.randint(0, 100),
        'views': random.randint(10, 5000),
        'circle': topic,  # Topic/category
        'tags': [topic] if random.random() > 0.3 else []
    }


def generate_threads(count: int = 20, author_ids: List[str] = None, seed: int = None) -> List[Dict[str, Any]]:
    """
    Generate multiple threads.
    
    Args:
        count: Number of threads to generate.
        author_ids: List of author IDs to use. If None, generates random ones.
        seed: Optional random seed for reproducibility.
    
    Returns:
        List of thread dictionaries, sorted by created_at (newest first).
    """
    if seed is not None:
        random.seed(seed)
    
    threads = []
    for i in range(count):
        author_id = random.choice(author_ids) if author_ids else None
        thread = generate_thread(author_id=author_id, seed=seed + i if seed is not None else None)
        threads.append(thread)
    
    # Sort by created_at (newest first)
    threads.sort(key=lambda x: x['created_at'], reverse=True)
    
    return threads

