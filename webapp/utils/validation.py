#!/usr/bin/env python3
"""
Input Validation Utilities for API Endpoints
Comprehensive validation for all API inputs
"""

from typing import Dict, Any, Optional, Tuple, List


def validate_user_id(user_id: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate user ID format
    
    Args:
        user_id: User ID to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not user_id:
        return False, 'User ID is required'
    if not isinstance(user_id, str):
        return False, 'User ID must be a string'
    if len(user_id) < 3 or len(user_id) > 100:
        return False, 'User ID must be between 3 and 100 characters'
    if not user_id.replace('_', '').replace('-', '').isalnum():
        return False, 'User ID contains invalid characters'
    return True, None


def validate_session_id(session_id: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate session ID format
    
    Args:
        session_id: Session ID to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not session_id:
        return False, 'Session ID is required'
    if not isinstance(session_id, str):
        return False, 'Session ID must be a string'
    if len(session_id) < 10 or len(session_id) > 200:
        return False, 'Session ID must be between 10 and 200 characters'
    return True, None


def validate_post_content(content: Any, max_length: int = 10000) -> Tuple[bool, Optional[str]]:
    """
    Validate post content
    
    Args:
        content: Post content to validate
        max_length: Maximum length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not content:
        return False, 'Content is required'
    if not isinstance(content, str):
        return False, 'Content must be a string'
    if len(content) > max_length:
        return False, f'Content must be no more than {max_length} characters'
    if not content.strip():
        return False, 'Content cannot be empty'
    return True, None


def validate_post_id(post_id: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate post ID format
    
    Args:
        post_id: Post ID to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not post_id:
        return False, 'Post ID is required'
    if not isinstance(post_id, str):
        return False, 'Post ID must be a string'
    if len(post_id) < 5 or len(post_id) > 100:
        return False, 'Post ID must be between 5 and 100 characters'
    if not post_id.replace('_', '').replace('-', '').isalnum():
        return False, 'Post ID contains invalid characters'
    return True, None


def validate_pagination(limit: Any, offset: Any, max_limit: int = 100) -> Tuple[bool, Optional[str], Optional[int], Optional[int]]:
    """
    Validate pagination parameters
    
    Args:
        limit: Items per page
        offset: Offset
        max_limit: Maximum limit
        
    Returns:
        Tuple of (is_valid, error_message, limit, offset)
    """
    try:
        limit_num = int(limit)
    except (ValueError, TypeError):
        return False, 'Limit must be an integer', None, None
    
    try:
        offset_num = int(offset)
    except (ValueError, TypeError):
        return False, 'Offset must be an integer', None, None
    
    if limit_num < 1:
        return False, 'Limit must be a positive integer', None, None
    if limit_num > max_limit:
        return False, f'Limit cannot exceed {max_limit}', None, None
    if offset_num < 0:
        return False, 'Offset must be a non-negative integer', None, None
    
    return True, None, limit_num, offset_num


def validate_feed_type(feed_type: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate feed type
    
    Args:
        feed_type: Feed type to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_types = ['chronological', 'quality', 'personalized']
    if not feed_type:
        return False, 'Feed type is required'
    if feed_type not in valid_types:
        return False, f'Feed type must be one of: {", ".join(valid_types)}'
    return True, None


def validate_comment_content(content: Any, max_length: int = 5000) -> Tuple[bool, Optional[str]]:
    """
    Validate comment content
    
    Args:
        content: Comment content
        max_length: Maximum length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not content:
        return False, 'Comment content is required'
    if not isinstance(content, str):
        return False, 'Comment content must be a string'
    if len(content) > max_length:
        return False, f'Comment must be no more than {max_length} characters'
    if not content.strip():
        return False, 'Comment cannot be empty'
    return True, None


def validate_media(media: Any, max_items: int = 10) -> Tuple[bool, Optional[str]]:
    """
    Validate media array
    
    Args:
        media: Media array
        max_items: Maximum items
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(media, list):
        return False, 'Media must be an array'
    if len(media) > max_items:
        return False, f'Cannot attach more than {max_items} media items'
    
    for item in media:
        if not isinstance(item, dict):
            return False, 'Each media item must be an object'
        if 'type' not in item or 'url' not in item:
            return False, 'Each media item must have type and url'
        if item['type'] not in ['image', 'video']:
            return False, 'Media type must be "image" or "video"'
        if not isinstance(item['url'], str) or not item['url']:
            return False, 'Media URL must be a non-empty string'
    
    return True, None


def validate_tags(tags: Any, max_items: int = 20) -> Tuple[bool, Optional[str]]:
    """
    Validate tags array
    
    Args:
        tags: Tags array
        max_items: Maximum items
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(tags, list):
        return False, 'Tags must be an array'
    if len(tags) > max_items:
        return False, f'Cannot use more than {max_items} tags'
    
    for tag in tags:
        if not isinstance(tag, str):
            return False, 'Each tag must be a string'
        if len(tag) == 0 or len(tag) > 50:
            return False, 'Each tag must be between 1 and 50 characters'
        # Allow alphanumeric, underscore, hyphen, and #
        if not all(c.isalnum() or c in ['_', '-', '#'] for c in tag):
            return False, 'Tags can only contain letters, numbers, underscores, hyphens, and #'
    
    return True, None


def validate_visibility(visibility: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate visibility setting
    
    Args:
        visibility: Visibility setting
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_values = ['public', 'followers', 'private']
    if not visibility:
        return False, 'Visibility is required'
    if visibility not in valid_values:
        return False, f'Visibility must be one of: {", ".join(valid_values)}'
    return True, None


def validate_message(message: Any, max_length: int = 10000) -> Tuple[bool, Optional[str]]:
    """
    Validate message content (for Thesidia API)
    
    Args:
        message: Message content
        max_length: Maximum length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not message:
        return False, 'Message is required'
    if not isinstance(message, str):
        return False, 'Message must be a string'
    if len(message) > max_length:
        return False, f'Message must be no more than {max_length} characters'
    if not message.strip():
        return False, 'Message cannot be empty'
    return True, None

