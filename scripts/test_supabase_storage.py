#!/usr/bin/env python3
"""
Test Supabase conversation storage adapter
"""

from pathlib import Path
from dotenv import load_dotenv
import sys
import time

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

load_dotenv()

from webapp.conversations.supabase_storage import SupabaseConversationStore, build_store
from webapp.conversations.storage import ConversationMessage

def test_supabase_store():
    """Test Supabase conversation storage"""
    
    print("="*60)
    print("Supabase Conversation Storage Test")
    print("="*60)
    print()
    
    # Test 1: Create store
    print("🔧 Test 1: Creating Supabase store...")
    try:
        store = SupabaseConversationStore()
        print("   ✅ Store created")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 2: Upsert conversation
    print("\n💾 Test 2: Upserting conversation...")
    test_conv_id = f"test_conv_{int(time.time())}"
    test_user_id = "test_user_123"
    
    messages = [
        ConversationMessage(
            role="user",
            content="Hello Thesidia!",
            ts_ms=int(time.time() * 1000)
        ),
        ConversationMessage(
            role="assistant",
            content="Hello! How can I help you explore today?",
            ts_ms=int(time.time() * 1000) + 1000
        )
    ]
    
    try:
        store.upsert_conversation(
            conversation_id=test_conv_id,
            user_id=test_user_id,
            session_id="test_session",
            title="Test Conversation",
            preview="Testing Supabase storage",
            messages=messages
        )
        print("   ✅ Conversation upserted")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 3: Retrieve conversation
    print("\n📥 Test 3: Retrieving conversation...")
    try:
        conv = store.get_conversation(test_conv_id, test_user_id, None)
        if conv:
            print(f"   ✅ Retrieved: {conv['title']}")
            print(f"      Messages: {len(conv['messages'])}")
        else:
            print("   ❌ Conversation not found")
            return False
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 4: List conversations
    print("\n📋 Test 4: Listing conversations...")
    try:
        convs = store.list_conversations(test_user_id, None, limit=10)
        print(f"   ✅ Found {len(convs)} conversations")
        for c in convs[:3]:
            print(f"      - {c['title']}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 5: Factory auto-detection
    print("\n🏭 Test 5: Testing factory auto-detection...")
    try:
        auto_store = build_store(base_dir=Path("."))
        print(f"   ✅ Factory created: {type(auto_store).__name__}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ All Tests Passed!")
    print("="*60)
    print()
    print("Supabase conversation storage is working correctly.")
    print("You can now use Supabase for production deployment.")
    
    return True

if __name__ == "__main__":
    success = test_supabase_store()
    sys.exit(0 if success else 1)
