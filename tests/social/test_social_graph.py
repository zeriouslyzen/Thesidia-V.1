#!/usr/bin/env python3
"""
Tests for Social Graph
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'webapp'))

from webapp.social.social_graph import SocialGraph


class TestSocialGraph(unittest.TestCase):
    """Test Social Graph"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.social_graph = SocialGraph(base_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_follow_user(self):
        """Test following a user"""
        success = self.social_graph.follow_user("user1", "user2")
        self.assertTrue(success)
        
        self.assertTrue(self.social_graph.is_following("user1", "user2"))
        self.assertIn("user1", self.social_graph.get_followers("user2"))
    
    def test_unfollow_user(self):
        """Test unfollowing a user"""
        self.social_graph.follow_user("user1", "user2")
        self.social_graph.unfollow_user("user1", "user2")
        
        self.assertFalse(self.social_graph.is_following("user1", "user2"))
    
    def test_block_user(self):
        """Test blocking a user"""
        self.social_graph.follow_user("user1", "user2")
        self.social_graph.block_user("user1", "user2")
        
        self.assertTrue(self.social_graph.is_blocked("user1", "user2"))
        self.assertFalse(self.social_graph.is_following("user1", "user2"))


if __name__ == '__main__':
    unittest.main()

