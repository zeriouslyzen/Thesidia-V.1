#!/usr/bin/env python3
"""
Migrate historical data to populate new pages
Loads data from previous runs into knowledge base and interest tracker
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
from user_interest_tracker import UserInterestTracker

def migrate_user_interests_to_knowledge_base():
    """Migrate user interests to knowledge base as patterns"""
    print("📊 Migrating user interests to knowledge base...")
    
    kb = KnowledgeBase(base_dir=project_root)
    tracker = UserInterestTracker(base_dir=project_root)
    
    interests = tracker.get_user_interests()
    topics = interests.get('topics', {})
    
    migrated_count = 0
    skipped_count = 0
    
    # Filter out very short or common words
    skip_words = {'what', 'this', 'that', 'the', 'a', 'an', 'is', 'are', 'was', 'were', 
                  'neat', 'cool', 'alrighty', 'here', 'these', 'during', 'sounds', 'common'}
    
    for topic, data in topics.items():
        topic_clean = topic.lower().strip()
        
        # Skip very short topics, common words, and empty
        if (not topic_clean or 
            len(topic_clean) < 3 or 
            topic_clean in skip_words or
            topic_clean.startswith('relativity:') or  # Skip book titles
            topic_clean.startswith('a brief')):
            skipped_count += 1
            continue
        
        try:
            # Check if already exists (use lowercase for comparison)
            existing = kb.get_knowledge(topic_clean)
            # get_knowledge returns None if not found, or a dict if found
            if existing is None:
                # Get related topics (filter out skip words)
                related = [t.lower().strip() for t in data.get('related_topics', []) 
                          if t.lower().strip() not in skip_words and len(t.strip()) > 3][:10]
                
                # Add as pattern
                kb.add_knowledge(
                    topic=topic_clean,
                    information={
                        'source': 'user_interest_tracker',
                        'count': data.get('count', 0),
                        'first_seen': data.get('first_seen', ''),
                        'last_seen': data.get('last_seen', ''),
                        'original_topic': topic
                    },
                    connections=related
                )
                migrated_count += 1
                if migrated_count % 10 == 0:
                    print(f"  ... migrated {migrated_count} topics so far")
        except Exception as e:
            print(f"  ⚠️  Error migrating topic '{topic}': {e}")
    
    kb.save_knowledge()
    print(f"✅ Migrated {migrated_count} topics from user interests to knowledge base")
    print(f"   (Skipped {skipped_count} common/short words)")
    return migrated_count

def migrate_state_interactions():
    """Extract topics from state file interactions"""
    print("📝 Extracting topics from state file interactions...")
    
    state_file = project_root / 'data' / 'thesidia_hybrid_adaptive_state.json'
    if not state_file.exists():
        print("  ⚠️  State file not found")
        return 0
    
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        interactions = state.get('interactions', [])
        kb = KnowledgeBase(base_dir=project_root)
        tracker = UserInterestTracker(base_dir=project_root)
        
        migrated_count = 0
        for interaction in interactions[-50:]:  # Last 50 interactions
            user_input = interaction.get('input', '')
            output = interaction.get('output', '')
            
            if user_input:
                # Track in interest tracker
                try:
                    tracker.track_topic(user_input, output)
                except:
                    pass
                
                # Extract main topic from input
                words = user_input.split()[:3]
                if words:
                    topic = ' '.join(words).lower().strip('?.,!')
                    if len(topic) > 3:
                        try:
                            existing = kb.get_knowledge(topic)
                            if not existing:
                                kb.add_knowledge(
                                    topic=topic,
                                    information={
                                        'source': 'state_file',
                                        'input': user_input[:200],
                                        'timestamp': interaction.get('timestamp', datetime.now().isoformat())
                                    }
                                )
                                migrated_count += 1
                        except:
                            pass
    except Exception as e:
        print(f"  ⚠️  Error reading state file: {e}")
        return 0
    
    kb.save_knowledge()
    print(f"✅ Extracted {migrated_count} topics from state interactions")
    return migrated_count

if __name__ == '__main__':
    print("🚀 Starting data migration...")
    print("=" * 50)
    
    total = 0
    total += migrate_user_interests_to_knowledge_base()
    total += migrate_state_interactions()
    
    print("=" * 50)
    print(f"✅ Migration complete! Total topics migrated: {total}")
    
    # Show final stats
    kb = KnowledgeBase(base_dir=project_root)
    stats = kb.get_stats()
    print(f"\n📊 Knowledge Base Stats:")
    print(f"   Topics: {stats['total_topics']}")
    print(f"   Facts: {stats['total_facts']}")
    print(f"   Connections: {stats['total_connections']}")

