#!/usr/bin/env python3
"""
Tests for Post Manager
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

from webapp.social.post_manager import PostManager
from webapp.social.schema import PostSchema


class TestPostManager(unittest.TestCase):
    """Test Post Manager"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.post_manager = PostManager(base_dir=self.test_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_create_post(self):
        """Test post creation"""
        post = self.post_manager.create_post(
            author_id="user_test",
            content="Test post content",
            tags=["test"],
            visibility="public"
        )
        
        self.assertIsNotNone(post)
        self.assertEqual(post['author_id'], "user_test")
        self.assertEqual(post['content'], "Test post content")
        self.assertEqual(post['visibility'], "public")
        self.assertIn('id', post)
        self.assertIn('created_at', post)
    
    def test_get_post(self):
        """Test getting a post"""
        post = self.post_manager.create_post(
            author_id="user_test",
            content="Test post"
        )
        
        retrieved = self.post_manager.get_post(post['id'])
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['id'], post['id'])
        self.assertEqual(retrieved['content'], "Test post")
    
    def test_update_post(self):
        """Test updating a post"""
        post = self.post_manager.create_post(
            author_id="user_test",
            content="Original content"
        )
        
        updated = self.post_manager.update_post(
            post['id'],
            "user_test",
            {'content': 'Updated content'}
        )
        
        self.assertIsNotNone(updated)
        self.assertEqual(updated['content'], "Updated content")
    
    def test_delete_post(self):
        """Test deleting a post"""
        post = self.post_manager.create_post(
            author_id="user_test",
            content="Test post"
        )
        
        success = self.post_manager.delete_post(post['id'], "user_test")
        self.assertTrue(success)
        
        retrieved = self.post_manager.get_post(post['id'])
        self.assertIsNone(retrieved)


if __name__ == '__main__':
    unittest.main()

