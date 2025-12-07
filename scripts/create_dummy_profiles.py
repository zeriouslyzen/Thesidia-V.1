#!/usr/bin/env python3
"""
Create Dummy Profiles with Mock Data
Creates 5 dummy user profiles with diverse post types:
- Image posts (selfies)
- GIF posts
- Short form video posts
- Regular text posts
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

# 5 Dummy users with realistic names and selfie avatars
DUMMY_USERS = [
    {
        "user_id": "user_maya_patel",
        "username": "mayapatel",
        "display_name": "Maya Patel",
        "bio": "Digital artist | Coffee enthusiast | Living life one pixel at a time ✨",
        "avatar_url": "https://i.pravatar.cc/300?img=47",
        "location": "San Francisco, CA",
        "website": "https://mayapatel.design"
    },
    {
        "user_id": "user_ryan_martinez",
        "username": "ryanmartinez",
        "display_name": "Ryan Martinez",
        "bio": "Fitness coach | Motivational speaker | Helping people transform their lives 💪",
        "avatar_url": "https://i.pravatar.cc/300?img=33",
        "location": "Los Angeles, CA",
        "website": "https://ryanfitness.com"
    },
    {
        "user_id": "user_sofia_andersen",
        "username": "sofiaandersen",
        "display_name": "Sofia Andersen",
        "bio": "Travel blogger | Adventure seeker | Documenting beautiful moments around the world 🌍",
        "avatar_url": "https://i.pravatar.cc/300?img=52",
        "location": "Copenhagen, Denmark",
        "website": "https://sofiatravels.com"
    },
    {
        "user_id": "user_jordan_taylor",
        "username": "jordantaylor",
        "display_name": "Jordan Taylor",
        "bio": "Tech entrepreneur | Startup founder | Building the future one line of code at a time 🚀",
        "avatar_url": "https://i.pravatar.cc/300?img=68",
        "location": "Austin, TX",
        "website": "https://jordantaylor.io"
    },
    {
        "user_id": "user_priya_sharma",
        "username": "priyasharma",
        "display_name": "Priya Sharma",
        "bio": "Yoga instructor | Mindfulness coach | Finding balance in chaos 🧘‍♀️",
        "avatar_url": "https://i.pravatar.cc/300?img=60",
        "location": "Portland, OR",
        "website": "https://priyayoga.com"
    }
]

# Diverse posts for each user
DUMMY_POSTS = [
    # Maya Patel - Image post (selfie)
    {
        "author": "user_maya_patel",
        "content": "Morning selfie! ☀️ Starting the day with good vibes and even better coffee. What's everyone up to today? #selfie #morningvibes #coffee",
        "media": [
            {
                "type": "image",
                "url": "https://i.pravatar.cc/800?img=47",
                "thumbnail": "https://i.pravatar.cc/400?img=47"
            }
        ],
        "tags": ["selfie", "morningvibes", "coffee", "photography"],
        "interactions": {"likes": 127, "comments": 23, "reposts": 8, "views": 456},
        "ai_score": 0.78
    },
    # Ryan Martinez - GIF post
    {
        "author": "user_ryan_martinez",
        "content": "When you finally hit that PR you've been working towards! 💪 The grind never stops. Keep pushing! #fitness #motivation #gains",
        "media": [
            {
                "type": "gif",
                "url": "https://media.giphy.com/media/3o7aD2saQqpyIMYKw0/giphy.gif",
                "thumbnail": "https://media.giphy.com/media/3o7aD2saQqpyIMYKw0/giphy.gif"
            }
        ],
        "tags": ["fitness", "motivation", "gains", "workout"],
        "interactions": {"likes": 234, "comments": 45, "reposts": 32, "views": 892},
        "ai_score": 0.85
    },
    # Sofia Andersen - Short form video post
    {
        "author": "user_sofia_andersen",
        "content": "Quick tour of this beautiful hidden gem in Copenhagen! 🇩🇰 Sometimes the best places are the ones you discover by accident. #travel #copenhagen #adventure",
        "media": [
            {
                "type": "video",
                "url": "https://videos.pexels.com/video-files/3045163/3045163-hd_1920_1080_30fps.mp4",
                "thumbnail": "https://images.pexels.com/videos/3045163/pexels-photo-3045163.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500",
                "duration": 15
            }
        ],
        "tags": ["travel", "copenhagen", "adventure", "explore"],
        "interactions": {"likes": 189, "comments": 34, "reposts": 19, "views": 1234},
        "ai_score": 0.92
    },
    # Jordan Taylor - Regular text post
    {
        "author": "user_jordan_taylor",
        "content": "Just shipped a major feature update! 🎉\n\nAfter weeks of late nights and countless cups of coffee, we're finally ready to share what we've been building. The team has been incredible, and I'm so proud of what we've accomplished together.\n\nSometimes the best products come from teams that aren't afraid to iterate, fail fast, and learn from every mistake. Here's to the builders, the dreamers, and everyone who refuses to settle for good enough.\n\n#startup #tech #buildinpublic #entrepreneurship",
        "media": [],
        "tags": ["startup", "tech", "buildinpublic", "entrepreneurship"],
        "interactions": {"likes": 312, "comments": 67, "reposts": 42, "views": 1567},
        "ai_score": 0.88
    },
    # Priya Sharma - Image post (selfie with yoga pose)
    {
        "author": "user_priya_sharma",
        "content": "Sunrise yoga session complete! 🌅 Finding peace in the early morning stillness. Remember, it's not about being perfect, it's about showing up for yourself every day. #yoga #mindfulness #selfcare #wellness",
        "media": [
            {
                "type": "image",
                "url": "https://i.pravatar.cc/800?img=60",
                "thumbnail": "https://i.pravatar.cc/400?img=60"
            }
        ],
        "tags": ["yoga", "mindfulness", "selfcare", "wellness"],
        "interactions": {"likes": 156, "comments": 28, "reposts": 12, "views": 678},
        "ai_score": 0.81
    },
    # Maya Patel - Regular post with image
    {
        "author": "user_maya_patel",
        "content": "New artwork in progress! This piece has been taking shape over the past few weeks. There's something magical about watching an idea transform into reality. What do you think? 🎨",
        "media": [
            {
                "type": "image",
                "url": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=800&h=600&fit=crop",
                "thumbnail": "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=400&h=300&fit=crop"
            }
        ],
        "tags": ["art", "digitalart", "creativity", "workinprogress"],
        "interactions": {"likes": 98, "comments": 15, "reposts": 6, "views": 345},
        "ai_score": 0.76
    },
    # Ryan Martinez - Short form video (workout)
    {
        "author": "user_ryan_martinez",
        "content": "Quick 30-second workout tip! This exercise targets your core and improves stability. Try it out and let me know how it feels! 💪 #fitness #workout #core #health",
        "media": [
            {
                "type": "video",
                "url": "https://videos.pexels.com/video-files/2491284/2491284-hd_1920_1080_30fps.mp4",
                "thumbnail": "https://images.pexels.com/videos/2491284/pexels-photo-2491284.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500",
                "duration": 30
            }
        ],
        "tags": ["fitness", "workout", "core", "health", "exercise"],
        "interactions": {"likes": 267, "comments": 52, "reposts": 38, "views": 1456},
        "ai_score": 0.89
    },
    # Sofia Andersen - GIF post (travel)
    {
        "author": "user_sofia_andersen",
        "content": "That moment when you discover a new favorite spot! 😍 Travel is all about these unexpected beautiful moments. #travel #wanderlust #adventure #explore",
        "media": [
            {
                "type": "gif",
                "url": "https://media.giphy.com/media/3o7aD2saQqpyIMYKw0/giphy.gif",
                "thumbnail": "https://media.giphy.com/media/3o7aD2saQqpyIMYKw0/giphy.gif"
            }
        ],
        "tags": ["travel", "wanderlust", "adventure", "explore"],
        "interactions": {"likes": 201, "comments": 38, "reposts": 24, "views": 987},
        "ai_score": 0.83
    },
    # Jordan Taylor - Selfie post
    {
        "author": "user_jordan_taylor",
        "content": "Late night coding session selfie! 🔥 When the code finally works and everything clicks. This is the feeling that keeps me going. #coding #developer #tech #buildinpublic",
        "media": [
            {
                "type": "image",
                "url": "https://i.pravatar.cc/800?img=68",
                "thumbnail": "https://i.pravatar.cc/400?img=68"
            }
        ],
        "tags": ["coding", "developer", "tech", "buildinpublic", "selfie"],
        "interactions": {"likes": 145, "comments": 29, "reposts": 15, "views": 567},
        "ai_score": 0.79
    },
    # Priya Sharma - Regular text post
    {
        "author": "user_priya_sharma",
        "content": "Mindfulness Monday reminder: Take a deep breath. You're exactly where you need to be. 🌸\n\nSometimes we get so caught up in where we're going that we forget to appreciate where we are. Today, I'm practicing gratitude for the present moment.\n\nWhat are you grateful for today?",
        "media": [],
        "tags": ["mindfulness", "gratitude", "wellness", "selfcare"],
        "interactions": {"likes": 178, "comments": 41, "reposts": 27, "views": 723},
        "ai_score": 0.87
    }
]


def create_user_profiles(base_dir: Path):
    """Create user profiles for dummy users"""
    users_dir = base_dir / "data" / "users"
    users_dir.mkdir(parents=True, exist_ok=True)
    
    profile_schema = ProfileSchema()
    social_schema = SocialGraphSchema()
    
    for user_data in DUMMY_USERS:
        user_id = user_data["user_id"]
        user_path = users_dir / user_id
        user_path.mkdir(parents=True, exist_ok=True)
        
        # Create profile
        profile = profile_schema.create_profile(user_id, user_data["username"])
        profile.update({
            "display_name": user_data["display_name"],
            "bio": user_data["bio"],
            "avatar_url": user_data["avatar_url"],
            "location": user_data.get("location", ""),
            "website": user_data.get("website", ""),
            "stats": {
                "posts": len([p for p in DUMMY_POSTS if p["author"] == user_id]),
                "followers": 0,
                "following": 0
            }
        })
        
        profile_file = user_path / "profile.json"
        with open(profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
        
        # Create social graph
        social_graph = social_schema.create_social_graph(user_id)
        social_file = user_path / "social.json"
        with open(social_file, 'w', encoding='utf-8') as f:
            json.dump(social_graph, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created profile for {user_data['display_name']} (@{user_data['username']})")


def create_dummy_posts(base_dir: Path):
    """Create dummy posts with diverse content types"""
    post_manager = PostManager(base_dir=base_dir)
    
    # Create posts with timestamps spread over the last few days
    base_time = datetime.now()
    
    for i, post_data in enumerate(DUMMY_POSTS):
        # Stagger timestamps (most recent first)
        post_time = base_time - timedelta(hours=i * 2, minutes=i * 15)
        
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
        
        author_name = next((u["display_name"] for u in DUMMY_USERS if u["user_id"] == post_data["author"]), post_data["author"])
        media_type = post_data["media"][0]["type"] if post_data["media"] else "text"
        print(f"✅ Created {media_type} post by {author_name}: {post['id']}")


def main():
    """Main function"""
    base_dir = Path(__file__).resolve().parent.parent
    
    print("=" * 60)
    print("Creating 5 Dummy Profiles with Mock Data")
    print("=" * 60)
    print("\n📝 Creating user profiles...")
    create_user_profiles(base_dir)
    
    print(f"\n📸 Creating {len(DUMMY_POSTS)} diverse posts...")
    create_dummy_posts(base_dir)
    
    print("\n" + "=" * 60)
    print("✅ Successfully created dummy profiles and posts!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   - {len(DUMMY_USERS)} user profiles created")
    print(f"   - {len(DUMMY_POSTS)} posts created")
    print(f"\n📋 Post Types:")
    image_posts = len([p for p in DUMMY_POSTS if p.get("media") and any(m.get("type") == "image" for m in p["media"])])
    gif_posts = len([p for p in DUMMY_POSTS if p.get("media") and any(m.get("type") == "gif" for m in p["media"])])
    video_posts = len([p for p in DUMMY_POSTS if p.get("media") and any(m.get("type") == "video" for m in p["media"])])
    text_posts = len([p for p in DUMMY_POSTS if not p.get("media")])
    print(f"   - {image_posts} image posts (including selfies)")
    print(f"   - {gif_posts} GIF posts")
    print(f"   - {video_posts} short form video posts")
    print(f"   - {text_posts} regular text posts")
    print("\n🎉 You can now view these profiles and posts in the stream page!")


if __name__ == "__main__":
    main()

