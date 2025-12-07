"""
Comment Sorting Algorithms
Implements Reddit-style comment sorting: best, top, new, controversial
"""

import math
from typing import List, Dict, Any
from datetime import datetime


def sort_comments(comments: List[Dict[str, Any]], sort_type: str = 'best') -> List[Dict[str, Any]]:
    """
    Sort comments based on sort type
    
    Args:
        comments: List of comment dictionaries (may be nested)
        sort_type: 'best', 'top', 'new', or 'controversial'
    
    Returns:
        Sorted list of comments (with nested replies also sorted)
    """
    if not comments:
        return comments
    
    # Sort top-level comments
    sorted_comments = _sort_comment_list(comments, sort_type)
    
    # Recursively sort replies
    for comment in sorted_comments:
        if comment.get('replies'):
            comment['replies'] = sort_comments(comment['replies'], sort_type)
    
    return sorted_comments


def _sort_comment_list(comments: List[Dict[str, Any]], sort_type: str) -> List[Dict[str, Any]]:
    """Sort a flat list of comments"""
    if sort_type == 'best':
        return sorted(comments, key=_best_score, reverse=True)
    elif sort_type == 'top':
        return sorted(comments, key=lambda c: c.get('score', 0), reverse=True)
    elif sort_type == 'new':
        return sorted(comments, key=lambda c: _parse_date(c.get('created_at', '')), reverse=True)
    elif sort_type == 'controversial':
        return sorted(comments, key=_controversial_score, reverse=True)
    else:
        return sorted(comments, key=_best_score, reverse=True)


def _best_score(comment: Dict[str, Any]) -> float:
    """
    Reddit's "best" algorithm
    Uses confidence interval based on upvotes/downvotes ratio
    """
    upvotes = comment.get('upvotes', 0)
    downvotes = comment.get('downvotes', 0)
    score = upvotes - downvotes
    total = upvotes + downvotes
    
    if total == 0:
        return 0.0
    
    # Wilson score confidence interval (lower bound)
    # This is Reddit's algorithm for "best" sorting
    if total == 0:
        return 0.0
    
    z = 1.96  # 95% confidence
    phat = float(upvotes) / total
    
    denominator = 1 + (z * z / total)
    centre_adjusted_probability = (phat + z * z / (2 * total)) / denominator
    adjusted_standard_deviation = math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total) / denominator
    
    lower_bound = centre_adjusted_probability - z * adjusted_standard_deviation
    
    # Scale by total votes for tie-breaking
    return lower_bound * total


def _controversial_score(comment: Dict[str, Any]) -> float:
    """
    Controversial score: high engagement but mixed votes
    Formula: min(upvotes, downvotes) when score is close to 0
    """
    upvotes = comment.get('upvotes', 0)
    downvotes = comment.get('downvotes', 0)
    score = upvotes - downvotes
    total = upvotes + downvotes
    
    if total == 0:
        return 0.0
    
    # Controversial = high engagement (total votes) but close to neutral (score near 0)
    # Use min(upvotes, downvotes) * total as controversial score
    # This rewards comments with balanced up/down votes
    balance = min(upvotes, downvotes)
    neutrality = 1.0 - abs(score) / max(total, 1)
    
    return balance * neutrality * total


def _parse_date(date_str: str) -> datetime:
    """Parse ISO date string to datetime"""
    try:
        if 'T' in date_str:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return datetime.fromisoformat(date_str)
    except:
        return datetime.min

