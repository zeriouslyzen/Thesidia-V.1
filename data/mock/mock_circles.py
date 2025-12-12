"""
Mock Circles Data Generator
Generates forum threads and discussions for the circles section.
"""

import random
from typing import Dict, List, Any
from datetime import datetime, timedelta
from data.mock.forum_categories import (
    FORUM_CATEGORIES,
    get_all_subcategories,
    TAG_LEVELS,
    TAG_FORMATS,
    TAG_SOURCING,
    LEGACY_CIRCLE_TOPICS
)


# Thread titles
THREAD_TITLES = [
    "What are your thoughts on {topic}?",
    "Discussion: {topic}",
    "Exploring {topic} together",
    "Deep dive into {topic}",
    "Understanding {topic}",
    "Question about {topic}",
    "Insights on {topic}",
    "Breaking down {topic}",
    "Thoughts on {topic}?",
    "Guide: {topic}",
    "Study: {topic}",
    "Critique: {topic}"
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
    "What questions do you have about {topic}?",
    "Here's a comprehensive guide to {topic} based on my research and practice.",
    "I've been studying {topic} and wanted to share some findings.",
    "Critical analysis of {topic} - let's examine the evidence and limitations."
]

# Legacy compatibility - use new category structure
CIRCLE_TOPICS = LEGACY_CIRCLE_TOPICS


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
    
    # Select a random category and subcategory
    category_id = random.choice(list(FORUM_CATEGORIES.keys()))
    category = FORUM_CATEGORIES[category_id]
    subcategories = category.get('subcategories', [])
    
    if subcategories:
        subcategory = random.choice(subcategories)
        topic = f"{category['name']} - {subcategory['name']}"
        circle = f"{category_id}/{subcategory['id']}"
    else:
        topic = category['name']
        circle = category_id
    
    title_template = random.choice(THREAD_TITLES)
    body_template = random.choice(THREAD_BODIES)
    
    title = title_template.format(topic=topic)
    body = body_template.format(topic=topic)
    
    # Generate creation date (within last 14 days)
    days_ago = random.randint(0, 14)
    hours_ago = random.randint(0, 23)
    created_at = (datetime.now() - timedelta(days=days_ago, hours=hours_ago)).isoformat()
    
    thread_id = f"thread_{random.randint(10000, 99999)}"
    
    # Generate tags (level, format, sourcing)
    tags = {}
    if random.random() > 0.3:  # 70% chance of having level tag
        tags['level'] = random.choice(TAG_LEVELS)
    if random.random() > 0.2:  # 80% chance of having format tag
        tags['format'] = random.choice(TAG_FORMATS)
    if random.random() > 0.3:  # 70% chance of having sourcing tag
        tags['sourcing'] = random.choice(TAG_SOURCING)
    
    # Legacy tags list for backward compatibility
    legacy_tags = [circle]
    if tags.get('level'):
        legacy_tags.append(f"level:{tags['level']}")
    if tags.get('format'):
        legacy_tags.append(f"format:{tags['format']}")
    if tags.get('sourcing'):
        legacy_tags.append(f"sourcing:{tags['sourcing']}")
    
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
        'circle': circle,  # Category/subcategory path
        'category_id': category_id,
        'subcategory_id': subcategory['id'] if subcategories else None,
        'tags': legacy_tags,  # Legacy format
        'tag_metadata': tags,  # Structured tag metadata
        'category_name': category['name'],
        'subcategory_name': subcategory['name'] if subcategories else None
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


def generate_one_thread_per_category(author_ids: List[str] = None, seed: int = None) -> List[Dict[str, Any]]:
    """
    Generate exactly one thread per main category (10 threads total).
    Each thread will have exactly 3 comments.
    
    Args:
        author_ids: List of author IDs to use. If None, generates random ones.
        seed: Optional random seed for reproducibility.
    
    Returns:
        List of 10 thread dictionaries, one per category.
    """
    if seed is not None:
        random.seed(seed)
    
    if author_ids is None:
        author_ids = [f"user_{i}" for i in range(10)]
    
    threads = []
    category_ids = list(FORUM_CATEGORIES.keys())
    
    for i, category_id in enumerate(category_ids):
        category = FORUM_CATEGORIES[category_id]
        subcategories = category.get('subcategories', [])
        
        # Select first subcategory for consistency
        if subcategories:
            subcategory = subcategories[0]
            topic = f"{category['name']} - {subcategory['name']}"
            circle = f"{category_id}/{subcategory['id']}"
            subcategory_id = subcategory['id']
            subcategory_name = subcategory['name']
        else:
            topic = category['name']
            circle = category_id
            subcategory_id = None
            subcategory_name = None
        
        # Generate thread with consistent seed per category
        thread_seed = (seed + i * 100) if seed is not None else i * 100
        random.seed(thread_seed)
        
        author_id = random.choice(author_ids)
        title_template = random.choice(THREAD_TITLES)
        body_template = random.choice(THREAD_BODIES)
        
        title = title_template.format(topic=topic)
        body = body_template.format(topic=topic)
        
        # Generate creation date (spread over last 7 days)
        days_ago = i % 7
        hours_ago = i * 2
        created_at = (datetime.now() - timedelta(days=days_ago, hours=hours_ago)).isoformat()
        
        thread_id = f"thread_cat_{category_id}_{i}"
        
        # Generate tags
        tags = {}
        tags['level'] = random.choice(TAG_LEVELS)
        tags['format'] = random.choice(TAG_FORMATS)
        tags['sourcing'] = random.choice(TAG_SOURCING)
        
        legacy_tags = [circle]
        legacy_tags.append(f"level:{tags['level']}")
        legacy_tags.append(f"format:{tags['format']}")
        legacy_tags.append(f"sourcing:{tags['sourcing']}")
        
        thread = {
            'id': thread_id,
            'author_id': author_id,
            'title': title,
            'body': body,
            'created_at': created_at,
            'upvotes': random.randint(5, 50),
            'downvotes': random.randint(0, 5),
            'comment_count': 3,  # Exactly 3 comments
            'views': random.randint(50, 500),
            'circle': circle,
            'category_id': category_id,
            'subcategory_id': subcategory_id,
            'tags': legacy_tags,
            'tag_metadata': tags,
            'category_name': category['name'],
            'subcategory_name': subcategory_name
        }
        threads.append(thread)
    
    # Sort by created_at (newest first)
    threads.sort(key=lambda x: x['created_at'], reverse=True)
    
    return threads

