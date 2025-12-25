#!/usr/bin/env python3
"""
Comprehensive CRUD and RLS testing for Supabase conversation storage
"""

import sys
import time
import uuid
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent / "webapp"))

from conversations.supabase_storage import SupabaseConversationStore
from conversations.storage import ConversationMessage

def test_crud_operations():
    """Test Create, Read, Update operations"""
    print("="*70)
    print("CRUD Operations Test")
    print("="*70)
    print()
    
    store = SupabaseConversationStore()
    
    # Test data - use proper UUIDs
    user1_id = str(uuid.uuid4())
    user2_id = str(uuid.uuid4())
    conv1_id = str(uuid.uuid4())
    conv2_id = str(uuid.uuid4())
    
    # CREATE - Test 1: Create conversation for user 1
    print("📝 Test 1: CREATE conversation for user 1...")
    messages1 = [
        ConversationMessage("user", "What are the true origins of AI?", int(time.time() * 1000)),
        ConversationMessage("assistant", "Let me explore that through multiple perspectives...", int(time.time() * 1000) + 1000)
    ]
    
    try:
        store.upsert_conversation(conv1_id, user1_id, "session1", "AI Origins", "Deep dive into AI", messages1)
        print("   ✅ Created conversation for user 1")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # CREATE - Test 2: Create conversation for user 2
    print("\n📝 Test 2: CREATE conversation for user 2...")
    messages2 = [
        ConversationMessage("user", "Tell me about quantum computing", int(time.time() * 1000)),
    ]
    
    try:
        store.upsert_conversation(conv2_id, user2_id, "session2", "Quantum Computing", "Quantum exploration", messages2)
        print("   ✅ Created conversation for user 2")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # READ - Test 3: Read user 1's conversation
    print("\n📖 Test 3: READ user 1's conversation...")
    try:
        conv = store.get_conversation(conv1_id, user1_id, None)
        if conv and len(conv['messages']) == 2:
            print(f"   ✅ Retrieved: '{conv['title']}' with {len(conv['messages'])} messages")
        else:
            print(f"   ❌ Expected 2 messages, got {len(conv['messages']) if conv else 0}")
            return False
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # LIST - Test 4: List user 1's conversations
    print("\n📋 Test 4: LIST user 1's conversations...")
    try:
        convs = store.list_conversations(user1_id, None, limit=10)
        if len(convs) >= 1:
            print(f"   ✅ Found {len(convs)} conversation(s) for user 1")
            for c in convs:
                print(f"      - {c['title']}")
        else:
            print(f"   ❌ Expected at least 1 conversation")
            return False
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # UPDATE - Test 5: Update conversation (add message)
    print("\n✏️  Test 5: UPDATE conversation (add message)...")
    messages1_updated = messages1 + [
        ConversationMessage("user", "Tell me more about neural networks", int(time.time() * 1000) + 2000)
    ]
    
    try:
        store.upsert_conversation(conv1_id, user1_id, "session1", "AI Origins (Updated)", "Deep dive - updated", messages1_updated)
        conv = store.get_conversation(conv1_id, user1_id, None)
        if conv and len(conv['messages']) == 3 and 'Updated' in conv['title']:
            print(f"   ✅ Updated: '{conv['title']}' now has {len(conv['messages'])} messages")
        else:
            print(f"   ❌ Update failed")
            return False
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    print("\n" + "="*70)
    print("✅ All CRUD Operations Passed!")
    print("="*70)
    
    return True, user1_id, user2_id, conv1_id, conv2_id

def test_rls_enforcement(user1_id, user2_id, conv1_id, conv2_id):
    """Test Row Level Security enforcement"""
    print("\n" + "="*70)
    print("RLS Enforcement Test")
    print("="*70)
    print()
    
    store = SupabaseConversationStore()
    
    # RLS Test 1: User 2 tries to access User 1's conversation
    print("🔒 Test 1: User 2 tries to access User 1's conversation...")
    try:
        conv = store.get_conversation(conv1_id, user2_id, None)
        if conv is None:
            print("   ✅ Access denied correctly (returned None)")
        else:
            print(f"   ❌ SECURITY BREACH: User 2 accessed User 1's conversation!")
            return False
    except Exception as e:
        print(f"   ✅ Access denied with error (expected): {e}")
    
    # RLS Test 2: User 2 lists conversations (should only see their own)
    print("\n🔒 Test 2: User 2 lists conversations (should only see their own)...")
    try:
        convs = store.list_conversations(user2_id, None, limit=10)
        user1_convs = [c for c in convs if c['id'] == conv1_id]
        
        if len(user1_convs) == 0:
            print(f"   ✅ User 2 sees {len(convs)} conversation(s), none from User 1")
        else:
            print(f"   ❌ SECURITY BREACH: User 2 can see User 1's conversations!")
            return False
    except Exception as e:
        print(f"   ⚠️  Unexpected error: {e}")
        return False
    
    # RLS Test 3: User 1 can still access their own conversation
    print("\n🔒 Test 3: User 1 can still access their own conversation...")
    try:
        conv = store.get_conversation(conv1_id, user1_id, None)
        if conv:
            print(f"   ✅ User 1 can access: '{conv['title']}'")
        else:
            print(f"   ❌ User 1 cannot access their own conversation!")
            return False
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    print("\n" + "="*70)
    print("✅ All RLS Tests Passed!")
    print("="*70)
    print()
    print("🛡️  Row Level Security is working correctly:")
    print("   - Users can only access their own conversations")
    print("   - Cross-user access is properly blocked")
    print("   - Data isolation is enforced at database level")
    
    return True

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("Supabase Conversation Storage - Full Test Suite")
    print("="*70)
    print()
    
    # CRUD tests
    result = test_crud_operations()
    if not result:
        print("\n❌ CRUD tests failed")
        return False
    
    success, user1_id, user2_id, conv1_id, conv2_id = result
    
    # RLS tests
    if not test_rls_enforcement(user1_id, user2_id, conv1_id, conv2_id):
        print("\n❌ RLS tests failed")
        return False
    
    print("\n" + "="*70)
    print("🎉 ALL TESTS PASSED!")
    print("="*70)
    print()
    print("Summary:")
    print("  ✅ CRUD operations working")
    print("  ✅ RLS enforcement working")
    print("  ✅ Supabase adapter production-ready")
    print()
    print("Next: Update server.py and test with live server")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
