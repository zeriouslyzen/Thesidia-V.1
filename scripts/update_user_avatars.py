#!/usr/bin/env python3
"""
Update User Avatars with Stock Selfie Pictures
Updates all sample user profiles with realistic stock selfie photos
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Updated user avatars with stock selfie pictures
USER_AVATARS = {
    "user_alex_chen": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=faces",
    "user_sarah_jones": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&h=150&fit=crop&crop=faces",
    "user_mike_rodriguez": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=faces",
    "user_emma_wilson": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=faces",
    "user_david_kim": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&h=150&fit=crop&crop=faces",
    "user_lisa_park": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=faces",
    "user_james_taylor": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=faces"
}


def update_user_avatars():
    """Update user profiles with stock selfie pictures"""
    users_dir = project_root / "data" / "users"
    
    updated_count = 0
    for user_id, avatar_url in USER_AVATARS.items():
        profile_file = users_dir / user_id / "profile.json"
        
        if profile_file.exists():
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                
                profile['avatar_url'] = avatar_url
                
                with open(profile_file, 'w', encoding='utf-8') as f:
                    json.dump(profile, f, indent=2, ensure_ascii=False)
                
                print(f"Updated avatar for {profile.get('display_name', user_id)}")
                updated_count += 1
            except Exception as e:
                print(f"Error updating {user_id}: {e}")
        else:
            print(f"Profile not found for {user_id}")
    
    print(f"\n✅ Updated {updated_count} user avatars with stock selfie pictures")


if __name__ == "__main__":
    update_user_avatars()


