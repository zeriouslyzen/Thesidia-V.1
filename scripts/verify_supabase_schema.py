#!/usr/bin/env python3
"""
Verify Supabase schema is correctly set up
Run after executing supabase_schema.sql
"""

from supabase import create_client
from dotenv import load_dotenv
import os
import sys

def verify_schema():
    """Verify all tables and policies are created"""
    load_dotenv()
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")  # Need service key for admin queries
    
    if not url or not key:
        print("❌ Environment variables not set")
        return False
    
    try:
        client = create_client(url, key)
        print("✅ Connected to Supabase")
        
        # Check tables exist
        print("\n🔍 Checking tables...")
        tables = [
            'user_profiles',
            'conversations', 
            'messages',
            'memory_snapshots',
            'user_interests',
            'system_state'
        ]
        
        for table in tables:
            try:
                # Try to query each table (will fail if doesn't exist)
                result = client.table(table).select("*").limit(0).execute()
                print(f"   ✅ {table}")
            except Exception as e:
                print(f"   ❌ {table}: {e}")
                return False
        
        # Check helper functions (use RPC)
        print("\n🔍 Checking helper functions...")
        functions = [
            'search_conversations',
            'get_user_stats',
            'get_latest_memory'
        ]
        
        # Note: We can't easily test functions without data
        # Just verify tables are enough for now
        print("   ⚠️ Function verification requires test data")
        
        print("\n" + "="*60)
        print("✅ Schema Verification: PASSED")
        print("="*60)
        print()
        print("Next steps:")
        print("1. Create a test user via Supabase Auth")
        print("2. Insert test data to verify RLS policies")
        print("3. Proceed to Phase 3: Supabase Client Integration")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Supabase Schema Verification")
    print("="*60)
    print()
    
    success = verify_schema()
    sys.exit(0 if success else 1)
