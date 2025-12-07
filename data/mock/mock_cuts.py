"""
Mock KX Cuts Data Generator
Generates short-form content (videos/clips) for the kx cuts section.
"""

import random
from typing import Dict, List, Any
from datetime import datetime, timedelta


# Sample descriptions for cuts
CUT_DESCRIPTIONS = [
    "Quick insight on {topic}",
    "Breaking down {topic} in 60 seconds",
    "The truth about {topic}",
    "Why {topic} matters",
    "Exploring {topic}",
    "Deep dive: {topic}",
    "The hidden side of {topic}",
    "Understanding {topic}",
    "Reality check: {topic}",
    "Insights on {topic}"
]

CUT_TOPICS = [
    'consciousness', 'technology', 'philosophy', 'science', 'art',
    'creativity', 'innovation', 'learning', 'growth', 'wisdom',
    'truth', 'reality', 'perception', 'knowledge', 'experience',
    'transformation', 'evolution', 'mind', 'spirit', 'nature'
]


def generate_cut(author_id: str = None, seed: int = None) -> Dict[str, Any]:
    """
    Generate a single cut (short-form content).
    
    Args:
        author_id: Author user ID.
        seed: Optional random seed for reproducibility.
    
    Returns:
        Dictionary containing cut data.
    """
    if seed is not None:
        random.seed(seed)
    
    if author_id is None:
        author_id = f"user_{random.randint(1000, 9999)}"
    
    topic = random.choice(CUT_TOPICS)
    template = random.choice(CUT_DESCRIPTIONS)
    description = template.format(topic=topic)
    
    # Generate creation date (within last 7 days)
    days_ago = random.randint(0, 7)
    hours_ago = random.randint(0, 23)
    created_at = (datetime.now() - timedelta(days=days_ago, hours=hours_ago)).isoformat()
    
    cut_id = f"cut_{random.randint(10000, 99999)}"
    
    # Generate video duration (15-120 seconds)
    duration = random.randint(15, 120)
    
    return {
        'id': cut_id,
        'author_id': author_id,
        'description': description,
        'video_url': f'/videos/cuts/{cut_id}.mp4',  # Placeholder
        'thumbnail_url': f'/thumbnails/cuts/{cut_id}.jpg',  # Placeholder
        'duration': duration,
        'created_at': created_at,
        'likes': random.randint(0, 10000),
        'comments': random.randint(0, 500),
        'views': random.randint(100, 100000),
        'shares': random.randint(0, 1000)
    }


def generate_cuts(count: int = 20, author_ids: List[str] = None, seed: int = None) -> List[Dict[str, Any]]:
    """
    Generate multiple cuts.
    
    Args:
        count: Number of cuts to generate.
        author_ids: List of author IDs to use. If None, generates random ones.
        seed: Optional random seed for reproducibility.
    
    Returns:
        List of cut dictionaries, sorted by created_at (newest first).
    """
    if seed is not None:
        random.seed(seed)
    
    cuts = []
    for i in range(count):
        author_id = random.choice(author_ids) if author_ids else None
        cut = generate_cut(author_id=author_id, seed=seed + i if seed is not None else None)
        cuts.append(cut)
    
    # Sort by created_at (newest first)
    cuts.sort(key=lambda x: x['created_at'], reverse=True)
    
    return cuts

