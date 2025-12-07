"""
Profile loading utilities for social features.

Provides shared functions for loading user profile information
and attaching it to posts/feed items.
"""

import json
from pathlib import Path
from typing import Dict, Optional


def load_author_profile(author_id: str, project_root: Path, include_legacy_fields: bool = False) -> Dict:
    """
    Load author profile information from user data directory.
    
    Args:
        author_id: User ID of the author
        project_root: Project root directory (Path object)
        include_legacy_fields: If True, includes legacy fields (authorName, authorHandle, avatar)
                              for backward compatibility with profile.js
        
    Returns:
        Dictionary with author profile information:
        {
            'user_id': str,
            'username': str,
            'display_name': str,
            'avatar_url': str,
            'bio': str,
            # Legacy fields (if include_legacy_fields=True):
            'authorName': str,
            'authorHandle': str,
            'avatar': str
        }
    """
    if not author_id:
        return _get_default_profile(author_id, include_legacy_fields)
    
    profile_file = project_root / "data" / "users" / author_id / "profile.json"
    
    if not profile_file.exists():
        return _get_default_profile(author_id, include_legacy_fields)
    
    try:
        with open(profile_file, 'r', encoding='utf-8') as f:
            author_profile = json.load(f)
        
        profile = {
            'user_id': author_profile.get('user_id', author_id),
            'username': author_profile.get('username', ''),
            'display_name': author_profile.get('display_name', ''),
            'avatar_url': author_profile.get('avatar_url', ''),
            'bio': author_profile.get('bio', '')
        }
        
        # Add legacy fields for backward compatibility
        if include_legacy_fields:
            profile['authorName'] = profile['display_name']
            profile['authorHandle'] = profile['username']
            profile['avatar'] = profile['avatar_url']
        
        return profile
        
    except Exception as e:
        # Log error and return default profile
        print(f"Error loading author profile for {author_id}: {e}")
        return _get_default_profile(author_id, include_legacy_fields)


def _get_default_profile(author_id: str, include_legacy_fields: bool = False) -> Dict:
    """
    Get default profile when profile file doesn't exist or fails to load.
    
    Args:
        author_id: User ID
        include_legacy_fields: If True, includes legacy fields
        
    Returns:
        Dictionary with default profile information
    """
    # Generate basic info from user_id
    username = author_id.replace('user_', '') if author_id else 'user'
    display_name = username.replace('_', ' ').title()
    
    profile = {
        'user_id': author_id or 'unknown',
        'username': username,
        'display_name': display_name,
        'avatar_url': '',
        'bio': ''
    }
    
    if include_legacy_fields:
        profile['authorName'] = display_name
        profile['authorHandle'] = username
        profile['avatar'] = ''
    
    return profile


def attach_author_to_post(post: Dict, project_root: Path, include_legacy_fields: bool = False) -> None:
    """
    Attach author profile information to a post dictionary (in-place modification).
    
    Args:
        post: Post dictionary (will be modified in place)
        project_root: Project root directory
        include_legacy_fields: If True, includes legacy fields for backward compatibility
    """
    author_id = post.get('author_id')
    if not author_id:
        return
    
    profile = load_author_profile(author_id, project_root, include_legacy_fields)
    post['author'] = profile
    
    # Add legacy fields directly to post if requested (for profile.js compatibility)
    if include_legacy_fields:
        post['authorName'] = profile.get('authorName', '')
        post['authorHandle'] = profile.get('authorHandle', '')
        post['avatar'] = profile.get('avatar', '')

