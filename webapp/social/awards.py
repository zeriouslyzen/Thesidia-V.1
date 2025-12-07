"""
Awards System
Manages awards/badges for comments and threads
"""

from typing import Dict, List, Any
from datetime import datetime


# Award types
AWARD_TYPES = [
    {'id': 'quality', 'name': 'Quality', 'icon': '★'},
    {'id': 'insightful', 'name': 'Insightful', 'icon': '💡'},
    {'id': 'helpful', 'name': 'Helpful', 'icon': '✓'},
    {'id': 'original', 'name': 'Original', 'icon': '✨'},
    {'id': 'well_researched', 'name': 'Well Researched', 'icon': '📚'},
    {'id': 'thoughtful', 'name': 'Thoughtful', 'icon': '🤔'}
]


def get_award_types() -> List[Dict[str, Any]]:
    """Get all available award types"""
    return AWARD_TYPES


def add_award(comment_id: str, user_id: str, award_type: str) -> Dict[str, Any]:
    """
    Add an award to a comment
    
    Args:
        comment_id: Comment ID
        user_id: User giving the award
        award_type: Type of award (must be in AWARD_TYPES)
    
    Returns:
        Award data dictionary
    """
    # Validate award type
    valid_types = [a['id'] for a in AWARD_TYPES]
    if award_type not in valid_types:
        raise ValueError(f"Invalid award type: {award_type}")
    
    award = {
        'id': f"award_{comment_id}_{int(datetime.now().timestamp() * 1000)}",
        'comment_id': comment_id,
        'user_id': user_id,
        'type': award_type,
        'created_at': datetime.now().isoformat()
    }
    
    return award


def aggregate_awards(awards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Aggregate awards by type (count how many of each type)
    
    Args:
        awards: List of award dictionaries
    
    Returns:
        List of aggregated awards with counts
    """
    counts = {}
    for award in awards:
        award_type = award.get('type')
        if award_type:
            if award_type not in counts:
                counts[award_type] = {
                    'type': award_type,
                    'count': 0
                }
            counts[award_type]['count'] += 1
    
    return list(counts.values())

