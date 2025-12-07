"""
Mock Profile Data Generator
Generates realistic user profiles following engineering practices.
"""

import random
from typing import Dict, List, Any
from datetime import datetime, timedelta


# Sample data pools
USERNAMES = [
    'alexander', 'sophia', 'marcus', 'elena', 'david', 'luna', 'james', 'zara',
    'noah', 'maya', 'oliver', 'isabella', 'ethan', 'ava', 'lucas', 'chloe',
    'henry', 'emma', 'william', 'olivia', 'michael', 'sophia', 'daniel', 'mia'
]

DISPLAY_NAMES = [
    'Alexander Chen', 'Sophia Martinez', 'Marcus Johnson', 'Elena Rodriguez',
    'David Kim', 'Luna Williams', 'James Brown', 'Zara Davis',
    'Noah Wilson', 'Maya Anderson', 'Oliver Taylor', 'Isabella Thomas',
    'Ethan Jackson', 'Ava White', 'Lucas Harris', 'Chloe Martin',
    'Henry Thompson', 'Emma Garcia', 'William Moore', 'Olivia Clark',
    'Michael Lewis', 'Sophia Walker', 'Daniel Hall', 'Mia Young'
]

BIO_SAMPLES = [
    'Exploring consciousness and technology.',
    'Building the future, one line at a time.',
    'Seeker of truth and knowledge.',
    'Creator, thinker, dreamer.',
    'On a journey of continuous learning.',
    'Passionate about innovation and growth.',
    'Curious mind, open heart.',
    'Transforming ideas into reality.',
    'Living intentionally, creating meaningfully.',
    'Student of life, teacher by nature.'
]


def generate_profile(user_id: str = None, seed: int = None) -> Dict[str, Any]:
    """
    Generate a single user profile.
    
    Args:
        user_id: Optional user ID. If not provided, generates one.
        seed: Optional random seed for reproducibility.
    
    Returns:
        Dictionary containing profile data.
    """
    if seed is not None:
        random.seed(seed)
    
    if user_id is None:
        user_id = f"user_{random.randint(1000, 9999)}"
    
    username = random.choice(USERNAMES)
    display_name = random.choice(DISPLAY_NAMES)
    bio = random.choice(BIO_SAMPLES)
    
    # Generate creation date (within last 2 years)
    days_ago = random.randint(0, 730)
    created_at = (datetime.now() - timedelta(days=days_ago)).isoformat()
    
    return {
        'user_id': user_id,
        'username': username,
        'display_name': display_name,
        'avatar_url': f'/avatars/{username}.jpg',  # Placeholder
        'bio': bio,
        'created_at': created_at,
        'stats': {
            'posts': random.randint(0, 500),
            'followers': random.randint(0, 10000),
            'following': random.randint(0, 1000),
            'interactions': random.randint(0, 5000)
        }
    }


def generate_profiles(count: int = 10, seed: int = None) -> List[Dict[str, Any]]:
    """
    Generate multiple user profiles.
    
    Args:
        count: Number of profiles to generate.
        seed: Optional random seed for reproducibility.
    
    Returns:
        List of profile dictionaries.
    """
    if seed is not None:
        random.seed(seed)
    
    profiles = []
    for i in range(count):
        profile = generate_profile(seed=seed + i if seed is not None else None)
        profiles.append(profile)
    
    return profiles

