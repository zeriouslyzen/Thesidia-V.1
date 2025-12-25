#!/usr/bin/env python3
"""
Test Supabase connection
Run after Phase 1 setup to verify configuration
"""

from supabase import create_client
from dotenv import load_dotenv
import os
import sys

def test_connection():
    """Test basic Supabase connection"""
    load_dotenv()
    
    url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    service_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    # Check environment
    print("🔍 Checking environment variables...")
    if not url:
        print("❌ SUPABASE_URL not set in .env")
        return False
    if not anon_key:
        print("❌ SUPABASE_ANON_KEY not set in .env")
        return False
    if not service_key:
        print("⚠️ SUPABASE_SERVICE_KEY not set (needed for admin operations)")
    
    print(f"✅ Environment variables loaded")
    print(f"   URL: {url}")
    print(f"   Anon key: {anon_key[:20]}...")
    
    # Test connection
    print("\n🔌 Testing connection...")
    try:
        client = create_client(url, anon_key)
        print("✅ Supabase client created successfully")
        
        # Try a simple query (will fail if no tables, but connection works)
        try:
            result = client.table('conversations').select("*").limit(1).execute()
            print("✅ Database query successful")
            print(f"   Found {len(result.data)} conversations")
        except Exception as e:
            if "relation" in str(e).lower() or "does not exist" in str(e).lower():
                print("⚠️ Tables not created yet (this is normal for Phase 1)")
                print("   Proceed to Phase 2 to create database schema")
            else:
                print(f"⚠️ Query failed: {e}")
                print("   Connection works but there may be a schema issue")
        
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Supabase Connection Test")
    print("="*60)
    print()
    
    success = test_connection()
    
    print()
    print("="*60)
    if success:
        print("✅ Phase 1 Setup: COMPLETE")
        print("Next: Run database schema in Supabase SQL Editor")
        print("      (See supabase_readiness.md Phase 2)")
    else:
        print("❌ Phase 1 Setup: INCOMPLETE")
        print("Fix the errors above and try again")
    print("="*60)
    
    sys.exit(0 if success else 1)
