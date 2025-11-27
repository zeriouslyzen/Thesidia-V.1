#!/usr/bin/env python3
"""
Moderation Manager
AI-powered content filtering, user reporting, automatic flagging
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from webapp.social.ai_quality_scorer import AIQualityScorer
from webapp.social.bot_detector import BotDetector
from webapp.social.post_manager import PostManager


class ModerationManager:
    """
    Moderation Manager
    Handles content moderation, user reporting, and automatic flagging
    """
    
    def __init__(self, base_dir: Path = None, quality_scorer: Optional[Any] = None, bot_detector: Optional[Any] = None):
        """
        Initialize moderation manager
        
        Args:
            base_dir: Base directory for data storage
            quality_scorer: Optional AIQualityScorer instance (with AI)
            bot_detector: Optional BotDetector instance (with AI)
        """
        self.base_dir = base_dir or Path(".")
        self.moderation_dir = self.base_dir / "data" / "social" / "moderation"
        self.moderation_dir.mkdir(parents=True, exist_ok=True)
        self.quality_scorer = quality_scorer or AIQualityScorer(base_dir=base_dir)
        self.bot_detector = bot_detector or BotDetector(base_dir=base_dir)
        self.post_manager = PostManager(base_dir=base_dir)
    
    def moderate_post(self, post_id: str) -> Dict[str, Any]:
        """
        Moderate a post (AI scoring and bot detection)
        
        Args:
            post_id: Post ID
            
        Returns:
            Moderation result dictionary
        """
        post = self.post_manager.get_post(post_id)
        if not post:
            return {"status": "error", "message": "Post not found"}
        
        # Calculate quality score
        quality_score = self.quality_scorer.calculate_quality_score(post)
        
        # Check bot probability
        author_id = post.get('author_id')
        bot_probability, bot_signals = self.bot_detector.detect_bot(author_id)
        
        # Determine moderation status
        if quality_score < 0.3 or bot_probability > 0.7:
            status = "flagged"
        elif quality_score < 0.5 or bot_probability > 0.5:
            status = "review"
        else:
            status = "approved"
        
        # Update post with AI score
        post['ai_score'] = quality_score
        self.post_manager.update_post(post_id, author_id, {'ai_score': quality_score, 'moderation_status': status})
        
        # Save moderation data
        moderation_data = {
            "post_id": post_id,
            "quality_score": quality_score,
            "bot_probability": bot_probability,
            "bot_signals": bot_signals,
            "status": status,
            "moderated_at": datetime.now().isoformat()
        }
        
        self._save_moderation_data(post_id, moderation_data)
        
        return moderation_data
    
    def report_post(self, post_id: str, user_id: str, reason: str) -> bool:
        """
        Report a post
        
        Args:
            post_id: Post ID
            user_id: User ID reporting
            reason: Reason for reporting
            
        Returns:
            True if reported successfully
        """
        flagged_file = self.moderation_dir / "flagged_posts.json"
        
        if flagged_file.exists():
            with open(flagged_file, 'r', encoding='utf-8') as f:
                flagged_data = json.load(f)
        else:
            flagged_data = {"flagged_posts": []}
        
        # Check if already reported
        for report in flagged_data['flagged_posts']:
            if report.get('post_id') == post_id and report.get('reporter_id') == user_id:
                return False  # Already reported
        
        # Add report
        report = {
            "post_id": post_id,
            "reporter_id": user_id,
            "reason": reason,
            "reported_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        flagged_data['flagged_posts'].append(report)
        
        with open(flagged_file, 'w', encoding='utf-8') as f:
            json.dump(flagged_data, f, indent=2, ensure_ascii=False)
        
        return True
    
    def get_flagged_posts(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get flagged posts
        
        Args:
            status: Optional status filter (pending, reviewed, resolved)
            
        Returns:
            List of flagged post data
        """
        flagged_file = self.moderation_dir / "flagged_posts.json"
        
        if not flagged_file.exists():
            return []
        
        with open(flagged_file, 'r', encoding='utf-8') as f:
            flagged_data = json.load(f)
        
        posts = flagged_data.get('flagged_posts', [])
        
        if status:
            posts = [p for p in posts if p.get('status') == status]
        
        return posts
    
    def _save_moderation_data(self, post_id: str, data: Dict[str, Any]):
        """Save moderation data"""
        scores_file = self.moderation_dir / "ai_scores.json"
        
        if scores_file.exists():
            with open(scores_file, 'r', encoding='utf-8') as f:
                scores_data = json.load(f)
        else:
            scores_data = {"scores": {}}
        
        scores_data['scores'][post_id] = data
        
        with open(scores_file, 'w', encoding='utf-8') as f:
            json.dump(scores_data, f, indent=2, ensure_ascii=False)

