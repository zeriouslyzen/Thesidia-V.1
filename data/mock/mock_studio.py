"""
Mock Studio Data Generator
Generates mentor program data for the studio section.
"""

import random
from typing import Dict, List, Any
from datetime import datetime, timedelta


# Program titles
PROGRAM_TITLES = [
    "Mastering {topic}",
    "Deep Dive: {topic}",
    "The {topic} Journey",
    "Exploring {topic}",
    "Transformation Through {topic}",
    "Understanding {topic}",
    "The Art of {topic}",
    "Path to {topic}",
    "Unlocking {topic}",
    "The {topic} Experience"
]

PROGRAM_DESCRIPTIONS = [
    "A comprehensive program designed to help you master {topic} through structured learning and practice.",
    "Join us on a deep exploration of {topic}, covering theory, practice, and real-world applications.",
    "Transform your understanding of {topic} through this intensive program with expert guidance.",
    "Learn the fundamentals and advanced concepts of {topic} in this structured course.",
    "Discover the deeper layers of {topic} through guided exploration and mentorship.",
    "A journey into {topic} that combines knowledge, practice, and personal growth.",
    "Master the art of {topic} through hands-on learning and expert mentorship.",
    "Navigate the path to mastery in {topic} with structured guidance and support.",
    "Unlock the secrets of {topic} through this comprehensive program.",
    "Experience {topic} in a new way through this transformative program."
]

MENTOR_NAMES = [
    'Dr. Sarah Chen', 'Prof. Marcus Johnson', 'Elena Rodriguez', 'David Kim',
    'Dr. Luna Williams', 'James Brown', 'Zara Davis', 'Noah Wilson',
    'Maya Anderson', 'Oliver Taylor', 'Isabella Thomas', 'Ethan Jackson'
]

PROGRAM_TOPICS = [
    'Consciousness', 'Philosophy', 'Technology', 'Science', 'Art',
    'Creativity', 'Innovation', 'Learning', 'Growth', 'Wisdom',
    'Transformation', 'Leadership', 'Mindfulness', 'Design', 'Strategy'
]

STATUSES = ['active', 'upcoming', 'completed']


def generate_program(mentor_id: str = None, seed: int = None) -> Dict[str, Any]:
    """
    Generate a single mentor program.
    
    Args:
        mentor_id: Mentor user ID.
        seed: Optional random seed for reproducibility.
    
    Returns:
        Dictionary containing program data.
    """
    if seed is not None:
        random.seed(seed)
    
    if mentor_id is None:
        mentor_id = f"mentor_{random.randint(100, 999)}"
    
    topic = random.choice(PROGRAM_TOPICS)
    title_template = random.choice(PROGRAM_TITLES)
    desc_template = random.choice(PROGRAM_DESCRIPTIONS)
    
    title = title_template.format(topic=topic)
    description = desc_template.format(topic=topic)
    
    mentor_name = random.choice(MENTOR_NAMES)
    
    # Generate dates
    days_from_now = random.randint(-30, 90)  # Past to future
    start_date = (datetime.now() + timedelta(days=days_from_now)).isoformat()
    
    # Duration in weeks
    duration_weeks = random.choice([4, 6, 8, 12, 16])
    duration_text = f"{duration_weeks} weeks"
    
    program_id = f"program_{random.randint(1000, 9999)}"
    
    status = random.choice(STATUSES)
    if days_from_now < 0:
        status = 'completed'
    elif days_from_now > 14:
        status = 'upcoming'
    else:
        status = 'active'
    
    return {
        'id': program_id,
        'title': title,
        'description': description,
        'mentor_id': mentor_id,
        'mentor': {
            'name': mentor_name,
            'avatar_url': f'/avatars/mentors/{mentor_id}.jpg'
        },
        'start_date': start_date,
        'duration': duration_text,
        'duration_weeks': duration_weeks,
        'status': status,
        'thumbnail_url': f'/thumbnails/programs/{program_id}.jpg',
        'trailer_url': f'/videos/programs/{program_id}_trailer.mp4',
        'enrolled': random.randint(0, 500),
        'capacity': random.choice([50, 100, 200, 500]),
        'price': random.choice(['Free', '$99', '$199', '$299', '$499']),
        'category': topic.lower(),
        'tags': [topic.lower(), 'mentorship', 'learning']
    }


def generate_programs(count: int = 12, mentor_ids: List[str] = None, seed: int = None) -> List[Dict[str, Any]]:
    """
    Generate multiple programs.
    
    Args:
        count: Number of programs to generate.
        mentor_ids: List of mentor IDs to use. If None, generates random ones.
        seed: Optional random seed for reproducibility.
    
    Returns:
        List of program dictionaries, sorted by start_date.
    """
    if seed is not None:
        random.seed(seed)
    
    programs = []
    for i in range(count):
        mentor_id = random.choice(mentor_ids) if mentor_ids else None
        program = generate_program(mentor_id=mentor_id, seed=seed + i if seed is not None else None)
        programs.append(program)
    
    # Sort by start_date
    programs.sort(key=lambda x: x['start_date'])
    
    return programs

