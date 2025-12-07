#!/usr/bin/env python3
"""
Interaction Manager
Likes, comments, reposts, views
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class InteractionManager:
    """
    Interaction Manager
    Manages likes, comments, reposts, and views
    """
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize interaction manager
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir or Path(".")
        self.interactions_dir = self.base_dir / "data" / "social" / "interactions"
        # Try to create directory, but handle read-only filesystem (e.g., Vercel)
        try:
            self.interactions_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            # On read-only filesystem (Vercel), use in-memory storage
            print(f"Warning: Cannot create interactions directory (read-only filesystem): {e}")
            print("Using in-memory interaction storage (not persistent)")
    
    def _get_interaction_file(self, post_id: str) -> Path:
        """Get interaction file path for post"""
        return self.interactions_dir / f"{post_id}_interactions.json"
    
    def _load_interactions(self, post_id: str) -> Dict[str, Any]:
        """Load interactions for a post"""
        interaction_file = self._get_interaction_file(post_id)
        
        base: Dict[str, Any] = {
            "post_id": post_id,
            "likes": [],
            "comments": [],
            "reposts": [],
            "views": [],
            # Mastery / utility layer interactions
            # High-signal actions that encode rigor and utility rather than vanity
            "validations": [],          # user_ids who validated this post
            "references": [],           # list of {user_id, context, created_at}
            "contributions": [],        # list of {user_id, content, created_at}
            "availability_signals": []  # list of {user_id, created_at, window}
        }
        
        if interaction_file.exists():
            try:
                with open(interaction_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Backwards compatibility: ensure all expected keys exist
                    for key, default_value in base.items():
                        if key not in data:
                            data[key] = default_value
                    return data
            except Exception:
                # Fall back to base structure if file is corrupt
                pass
        
        return base
    
    def _save_interactions(self, post_id: str, interactions: Dict[str, Any]):
        """Save interactions for a post"""
        interaction_file = self._get_interaction_file(post_id)
        interactions['updated_at'] = datetime.now().isoformat()
        
        with open(interaction_file, 'w', encoding='utf-8') as f:
            json.dump(interactions, f, indent=2, ensure_ascii=False)
    
    def like_post(self, post_id: str, user_id: str) -> bool:
        """
        Like a post
        
        Args:
            post_id: Post ID
            user_id: User ID liking the post
            
        Returns:
            True if liked, False if unliked
        """
        interactions = self._load_interactions(post_id)
        
        if user_id in interactions['likes']:
            # Unlike
            interactions['likes'].remove(user_id)
            self._save_interactions(post_id, interactions)
            return False
        else:
            # Like
            interactions['likes'].append(user_id)
            self._save_interactions(post_id, interactions)
            return True
    
    def comment_post(self, post_id: str, user_id: str, content: str) -> Dict[str, Any]:
        """
        Comment on a post
        
        Args:
            post_id: Post ID
            user_id: User ID commenting
            content: Comment content
            
        Returns:
            Comment data dictionary
        """
        interactions = self._load_interactions(post_id)
        
        comment = {
            "id": f"comment_{datetime.now().timestamp()}",
            "user_id": user_id,
            "content": content,
            "created_at": datetime.now().isoformat()
        }
        
        interactions['comments'].append(comment)
        self._save_interactions(post_id, interactions)
        
        return comment
    
    def repost(self, post_id: str, user_id: str) -> bool:
        """
        Repost a post
        
        Args:
            post_id: Post ID
            user_id: User ID reposting
            
        Returns:
            True if reposted, False if unreposted
        """
        interactions = self._load_interactions(post_id)
        
        if user_id in interactions['reposts']:
            # Unrepost
            interactions['reposts'].remove(user_id)
            self._save_interactions(post_id, interactions)
            return False
        else:
            # Repost
            interactions['reposts'].append(user_id)
            self._save_interactions(post_id, interactions)
            return True
    
    def view_post(self, post_id: str, user_id: Optional[str] = None):
        """
        Record a post view
        
        Args:
            post_id: Post ID
            user_id: Optional user ID viewing
        """
        interactions = self._load_interactions(post_id)
        
        view = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        
        interactions['views'].append(view)
        self._save_interactions(post_id, interactions)
    
    def get_interactions(self, post_id: str) -> Dict[str, Any]:
        """
        Get all interactions for a post
        
        Args:
            post_id: Post ID
            
        Returns:
            Interactions dictionary with counts
        """
        interactions = self._load_interactions(post_id)
        
        # Basic engagement metrics
        likes = len(interactions['likes'])
        comments = len(interactions['comments'])
        reposts = len(interactions['reposts'])
        views = len(interactions['views'])
        
        # Mastery / utility metrics
        validations = len(interactions.get('validations', []))
        references = len(interactions.get('references', []))
        contributions = len(interactions.get('contributions', []))
        availability_signals = len(interactions.get('availability_signals', []))
        
        return {
            "likes": likes,
            "comments": comments,
            "reposts": reposts,
            "views": views,
            "liked_by": interactions['likes'],
            "comments_list": interactions['comments'],
            "reposted_by": interactions['reposts'],
            # Mastery / utility layer
            "validations": validations,
            "validated_by": interactions.get('validations', []),
            "references": references,
            "references_list": interactions.get('references', []),
            "contributions": contributions,
            "contributions_list": interactions.get('contributions', []),
            "availability_signals": availability_signals,
            "availability_list": interactions.get('availability_signals', [])
        }
    
    # ------------------------------------------------------------------
    # Mastery / utility interactions
    # ------------------------------------------------------------------
    
    def validate_post(self, post_id: str, user_id: str) -> bool:
        """
        Validate (or un-validate) a post.
        
        This is a high-signal action: the user is confirming the rigor /
        correctness of the content. We implement it as a toggle to keep
        UX simple while still allowing reversals.
        
        Returns:
            True if validated, False if validation was removed.
        """
        interactions = self._load_interactions(post_id)
        validators: List[str] = interactions.get("validations", [])
        
        if user_id in validators:
            validators.remove(user_id)
            validated = False
        else:
            validators.append(user_id)
            validated = True
        
        interactions["validations"] = validators
        self._save_interactions(post_id, interactions)
        return validated
    
    def reference_post(self, post_id: str, user_id: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Reference a post (utility signal).
        
        This is the equivalent of "save / cite": the user declares that
        this post is useful enough to be referenced in their own work.
        """
        interactions = self._load_interactions(post_id)
        references: List[Dict[str, Any]] = interactions.get("references", [])
        
        ref = {
            "id": f"ref_{datetime.now().timestamp()}",
            "user_id": user_id,
            "context": context or "",
            "created_at": datetime.now().isoformat()
        }
        references.append(ref)
        interactions["references"] = references
        self._save_interactions(post_id, interactions)
        return ref
    
    def contribute_to_post(self, post_id: str, user_id: str, content: str) -> Dict[str, Any]:
        """
        Register a contribution to a post.
        
        This is a small peer-review style addition or correction, distinct
        from a general comment. It can be surfaced differently in the UI.
        """
        interactions = self._load_interactions(post_id)
        contributions: List[Dict[str, Any]] = interactions.get("contributions", [])
        
        contribution = {
            "id": f"contrib_{datetime.now().timestamp()}",
            "user_id": user_id,
            "content": content,
            "created_at": datetime.now().isoformat()
        }
        contributions.append(contribution)
        interactions["contributions"] = contributions
        self._save_interactions(post_id, interactions)
        return contribution
    
    def signal_availability(self, post_id: str, user_id: str, window: Optional[str] = None) -> bool:
        """
        Signal availability to act on this post in the real world.
        
        Implemented as a toggle: the user can turn their availability
        signal on/off for a given post.
        """
        interactions = self._load_interactions(post_id)
        availability: List[Dict[str, Any]] = interactions.get("availability_signals", [])
        
        # Check if user already has a signal
        existing_index = next((i for i, sig in enumerate(availability) if sig.get("user_id") == user_id), None)
        
        if existing_index is not None:
            # Remove existing signal
            availability.pop(existing_index)
            active = False
        else:
            availability.append({
                "user_id": user_id,
                "window": window or "",
                "created_at": datetime.now().isoformat()
            })
            active = True
        
        interactions["availability_signals"] = availability
        self._save_interactions(post_id, interactions)
        return active
    
    def has_liked(self, post_id: str, user_id: str) -> bool:
        """Check if user has liked post"""
        interactions = self._load_interactions(post_id)
        return user_id in interactions['likes']
    
    def has_reposted(self, post_id: str, user_id: str) -> bool:
        """Check if user has reposted"""
        interactions = self._load_interactions(post_id)
        return user_id in interactions['reposts']

