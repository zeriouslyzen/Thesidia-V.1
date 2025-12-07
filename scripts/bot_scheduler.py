#!/usr/bin/env python3
"""
Bot Real-Time Posting Scheduler
Makes bots post in real-time at realistic intervals
"""

import sys
import time
import random
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'webapp'))

import requests


def post_as_bot(base_url: str = "https://localhost:5002", verify: bool = False):
    """Make a bot post right now"""
    try:
        response = requests.post(
            f"{base_url}/api/bots/post-now",
            json={},
            verify=verify,
            timeout=10
        )
        if response.ok:
            data = response.json()
            bot_id = data.get('bot_id', 'unknown')
            post_id = data.get('post', {}).get('id', 'unknown')
            has_media = len(data.get('post', {}).get('media', [])) > 0
            print(f"✅ Bot {bot_id[:20]} posted: {post_id[:20]} {'(with media)' if has_media else ''}")
            return True
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error posting: {e}")
        return False


def run_scheduler(interval_min: int = 5, interval_max: int = 30, base_url: str = "https://localhost:5002"):
    """
    Run continuous bot posting scheduler
    
    Args:
        interval_min: Minimum minutes between posts
        interval_max: Maximum minutes between posts
        base_url: Base URL of the API
    """
    print("=" * 60)
    print("Bot Real-Time Posting Scheduler")
    print("=" * 60)
    print(f"Posting interval: {interval_min}-{interval_max} minutes")
    print(f"API URL: {base_url}")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    verify_ssl = False  # For self-signed certs
    
    try:
        while True:
            # Post now
            post_as_bot(base_url, verify=verify_ssl)
            
            # Calculate next post time
            interval_seconds = random.randint(interval_min * 60, interval_max * 60)
            next_post = datetime.now() + timedelta(seconds=interval_seconds)
            
            print(f"⏰ Next post in {interval_seconds // 60} minutes ({next_post.strftime('%H:%M:%S')})")
            print()
            
            # Wait
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\n\n✅ Scheduler stopped")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Bot real-time posting scheduler')
    parser.add_argument('--interval-min', type=int, default=5, help='Minimum minutes between posts')
    parser.add_argument('--interval-max', type=int, default=30, help='Maximum minutes between posts')
    parser.add_argument('--url', type=str, default='https://localhost:5002', help='API base URL')
    
    args = parser.parse_args()
    
    run_scheduler(
        interval_min=args.interval_min,
        interval_max=args.interval_max,
        base_url=args.url
    )

