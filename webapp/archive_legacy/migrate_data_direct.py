#!/usr/bin/env python3
"""
Direct migration - loads data directly from JSON files
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from knowledge_base import KnowledgeBase

def migrate_direct():
    """Direct migration from JSON files"""
    print("🚀 Direct data migration from JSON files...")
    print("=" * 50)
    
    kb = KnowledgeBase(base_dir=project_root)
    
    # Load user interests directly
    interests_file = project_root / 'data' / 'user_interests.json'
    if not interests_file.exists():
        print("❌ user_interests.json not found")
        return 0
    
    with open(interests_file, 'r') as f:
        interests_data = json.load(f)
    
    topics = interests_data.get('topics', {})
    print(f"📊 Found {len(topics)} topics in user_interests.json")
    
    # Filter words to skip
    skip_words = {'what', 'this', 'that', 'the', 'a', 'an', 'is', 'are', 'was', 'were', 
                  'neat', 'cool', 'alrighty', 'here', 'these', 'during', 'sounds', 'common',
                  'explain', 'theory', 'flow.', 'special awareness.', 'insight', 'no-mind',
                  'chinese', 'british', 'eastern', 'absorption', 'orwell', 'big brother is watching you',
                  '10% happier', 'the miracle of mindfulness', 'common', 'sounds'}
    
    migrated = 0
    skipped = 0
    
    for topic, data in topics.items():
        topic_clean = topic.lower().strip()
        
        # Skip conditions
        if (not topic_clean or 
            len(topic_clean) < 3 or 
            topic_clean in skip_words or
            ':' in topic_clean or  # Skip book titles
            topic_clean.startswith('a brief') or
            topic_clean.startswith('relativity')):
            skipped += 1
            continue
        
        # Check if exists
        existing = kb.get_knowledge(topic_clean)
        if existing is None:
            # Get related topics (filtered)
            related = []
            for rt in data.get('related_topics', [])[:15]:
                rt_clean = rt.lower().strip()
                if (rt_clean and 
                    len(rt_clean) > 3 and 
                    rt_clean not in skip_words and
                    ':' not in rt_clean and
                    rt_clean != topic_clean):
                    related.append(rt_clean)
            
            # Add to knowledge base
            try:
                kb.add_knowledge(
                    topic=topic_clean,
                    information={
                        'source': 'user_interest_tracker',
                        'count': data.get('count', 0),
                        'first_seen': data.get('first_seen', ''),
                        'last_seen': data.get('last_seen', ''),
                        'original_topic': topic
                    },
                    connections=related[:10]
                )
                migrated += 1
                if migrated % 10 == 0:
                    print(f"  ... migrated {migrated} topics")
            except Exception as e:
                print(f"  ⚠️  Error with '{topic}': {e}")
    
    kb.save_knowledge()
    print(f"\n✅ Migrated {migrated} topics")
    print(f"   Skipped {skipped} common/short words")
    
    # Final stats
    stats = kb.get_stats()
    print(f"\n📊 Knowledge Base Stats:")
    print(f"   Topics: {stats['total_topics']}")
    print(f"   Facts: {stats['total_facts']}")
    print(f"   Connections: {stats['total_connections']}")
    
    return migrated

if __name__ == '__main__':
    migrate_direct()

