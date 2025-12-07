#!/usr/bin/env python3
"""
Create Sample Posts
Creates 7 sample posts with different users, media, and content
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'webapp'))

from webapp.social.post_manager import PostManager
from webapp.social.schema import ProfileSchema, SocialGraphSchema

# Sample users with different names and avatars
SAMPLE_USERS = [
    {
        "user_id": "user_alex_chen",
        "username": "alexchen",
        "display_name": "Alex Chen",
        "bio": "Creative developer exploring new frontiers",
        "avatar_url": "https://i.pravatar.cc/150?img=1"
    },
    {
        "user_id": "user_sarah_jones",
        "username": "sarahjones",
        "display_name": "Sarah Jones",
        "bio": "Designer & artist | Building beautiful things",
        "avatar_url": "https://i.pravatar.cc/150?img=5"
    },
    {
        "user_id": "user_mike_rodriguez",
        "username": "mikerodriguez",
        "display_name": "Mike Rodriguez",
        "bio": "Tech enthusiast | Coffee addict",
        "avatar_url": "https://i.pravatar.cc/150?img=12"
    },
    {
        "user_id": "user_emma_wilson",
        "username": "emmawilson",
        "display_name": "Emma Wilson",
        "bio": "Photographer capturing moments",
        "avatar_url": "https://i.pravatar.cc/150?img=9"
    },
    {
        "user_id": "user_david_kim",
        "username": "davidkim",
        "display_name": "David Kim",
        "bio": "Musician & producer | Making beats",
        "avatar_url": "https://i.pravatar.cc/150?img=15"
    },
    {
        "user_id": "user_lisa_park",
        "username": "lisapark",
        "display_name": "Lisa Park",
        "bio": "Writer & storyteller | Words matter",
        "avatar_url": "https://i.pravatar.cc/150?img=20"
    },
    {
        "user_id": "user_james_taylor",
        "username": "jamestaylor",
        "display_name": "James Taylor",
        "bio": "Entrepreneur | Building the future",
        "avatar_url": "https://i.pravatar.cc/150?img=33"
    }
]

# Sample posts with content, media, and tags
SAMPLE_POSTS = [
    {
        "author": "user_alex_chen",
        "content": "Just finished building a new feature for the platform. The feeling when everything clicks together is unmatched. 🚀\n\n#coding #webdev #buildinpublic",
        "media": [
            {
                "type": "image",
                "url": "https://images.unsplash.com/photo-1551650975-87deedd944c3?w=800&h=600&fit=crop",
                "thumbnail": "https://images.unsplash.com/photo-1551650975-87deedd944c3?w=400&h=300&fit=crop"
            }
        ],
        "tags": ["coding", "webdev", "buildinpublic"],
        "interactions": {"likes": 42, "comments": 8, "reposts": 3, "views": 156},
        "ai_score": 0.82
    },
    {
        "author": "user_sarah_jones",
        "content": "New design system in progress. Sometimes the best solutions come from stepping back and seeing the bigger picture. ✨",
        "media": [
            {
                "type": "image",
                "url": "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=800&h=600&fit=crop",
                "thumbnail": "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&h=300&fit=crop"
            }
        ],
        "tags": ["design", "ui", "creativity"],
        "interactions": {"likes": 67, "comments": 12, "reposts": 5, "views": 234},
        "ai_score": 0.75
    },
    {
        "author": "user_mike_rodriguez",
        "content": "Morning coffee and code. This is the way. ☕\n\nWhat's everyone working on today?",
        "media": [],
        "tags": ["coffee", "coding", "morning"],
        "interactions": {"likes": 28, "comments": 15, "reposts": 2, "views": 189},
        "ai_score": 0.65
    },
    {
        "author": "user_emma_wilson",
        "content": "Golden hour in the city. Sometimes you just have to stop and appreciate the moment. 📸",
        "media": [
            {
                "type": "image",
                "url": "https://images.unsplash.com/photo-1514565131-fce0801e5785?w=800&h=600&fit=crop",
                "thumbnail": "https://images.unsplash.com/photo-1514565131-fce0801e5785?w=400&h=300&fit=crop"
            }
        ],
        "tags": ["photography", "city", "goldenhour"],
        "interactions": {"likes": 89, "comments": 6, "reposts": 8, "views": 312},
        "ai_score": 0.88
    },
    {
        "author": "user_david_kim",
        "content": "New track dropping soon! Here's a sneak peek of the studio session. 🎵",
        "media": [
            {
                "type": "gif",
                "url": "https://media.giphy.com/media/3o7aCTPPm4OHfRLSH6/giphy.gif",
                "thumbnail": "https://media.giphy.com/media/3o7aCTPPm4OHfRLSH6/giphy.gif"
            }
        ],
        "tags": ["music", "studio", "production"],
        "interactions": {"likes": 124, "comments": 23, "reposts": 12, "views": 567},
        "ai_score": 0.91
    },
    {
        "author": "user_lisa_park",
        "content": "Working on a new story. The blank page is both terrifying and exciting. Every word matters. 📝",
        "media": [
            {
                "type": "image",
                "url": "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=800&h=600&fit=crop",
                "thumbnail": "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=400&h=300&fit=crop"
            }
        ],
        "tags": ["writing", "storytelling", "creativity"],
        "interactions": {"likes": 45, "comments": 9, "reposts": 4, "views": 198},
        "ai_score": 0.79
    },
    {
        "author": "user_james_taylor",
        "content": "Launch day! After months of hard work, we're finally live. Grateful for the team and everyone who believed in this vision. 🎉",
        "media": [
            {
                "type": "image",
                "url": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&h=600&fit=crop",
                "thumbnail": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&h=300&fit=crop"
            }
        ],
        "tags": ["launch", "startup", "entrepreneurship"],
        "interactions": {"likes": 156, "comments": 34, "reposts": 18, "views": 789},
        "ai_score": 0.94
    }
]


def create_user_profiles(base_dir: Path):
    """Create user profiles for sample users"""
    users_dir = base_dir / "data" / "users"
    users_dir.mkdir(parents=True, exist_ok=True)
    
    profile_schema = ProfileSchema()
    social_schema = SocialGraphSchema()
    
    for user_data in SAMPLE_USERS:
        user_id = user_data["user_id"]
        user_path = users_dir / user_id
        user_path.mkdir(parents=True, exist_ok=True)
        
        # Create profile
        profile = profile_schema.create_profile(user_id, user_data["username"])
        profile.update({
            "display_name": user_data["display_name"],
            "bio": user_data["bio"],
            "avatar_url": user_data["avatar_url"]
        })
        
        profile_file = user_path / "profile.json"
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        
        # Create social graph
        social_graph = social_schema.create_social_graph(user_id)
        social_file = user_path / "social.json"
        with open(social_file, 'w', encoding='utf-8') as f:
            json.dump(social_graph, f, indent=2, ensure_ascii=False)
        
        print(f"Created profile for {user_data['display_name']}")


def create_sample_posts(base_dir: Path):
    """Create sample posts"""
    post_manager = PostManager(base_dir=base_dir)
    
    # Create posts with timestamps spread over the last few days
    base_time = datetime.now()
    
    for i, post_data in enumerate(SAMPLE_POSTS):
        # Stagger timestamps
        post_time = base_time - timedelta(hours=i * 3)
        
        # Create post using PostManager
        post = post_manager.create_post(
            author_id=post_data["author"],
            content=post_data["content"],
            media=post_data["media"],
            tags=post_data["tags"],
            visibility="public"
        )
        
        # Update timestamp and interactions
        post["created_at"] = post_time.isoformat()
        post["updated_at"] = post_time.isoformat()
        post["interactions"] = post_data["interactions"]
        post["ai_score"] = post_data["ai_score"]
        post["moderation_status"] = "approved"
        
        # Save updated post
        post_file = base_dir / "data" / "social" / "posts" / f"{post['id']}.json"
        with open(post_file, 'w', encoding='utf-8') as f:
            json.dump(post, f, indent=2, ensure_ascii=False)
        
        # Update indexes
        post_manager._update_indexes(post)
        
        print(f"Created post by {post_data['author']}: {post['id']}")


def main():
    """Main function"""
    base_dir = Path(__file__).resolve().parent.parent
    
    print("Creating sample users...")
    create_user_profiles(base_dir)
    
    print("\nCreating sample posts...")
    create_sample_posts(base_dir)
    
    print("\n✅ Sample posts created successfully!")
    print(f"Created {len(SAMPLE_POSTS)} posts from {len(SAMPLE_USERS)} users")


if __name__ == "__main__":
    main()


