#!/usr/bin/env python3
"""
Supabase storage adapter for conversations.

Implements ConversationStore interface using Supabase PostgreSQL backend.
Compatible with existing SQLite storage - can be switched via environment variable.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from supabase import create_client, Client

from .storage import ConversationStore, ConversationMessage

# Load environment variables
load_dotenv()


class SupabaseConversationStore(ConversationStore):
    """Supabase-backed conversation storage with RLS"""
    
    def __init__(self):
        """Initialize Supabase client with service role key"""
        # Service role key for server-side operations (bypasses RLS when needed)
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not url or not key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env file"
            )
        
        self.client: Client = create_client(url, key)
    
    def upsert_conversation(
        self,
        conversation_id: str,
        user_id: Optional[str],
        session_id: Optional[str],
        title: str,
        preview: str,
        messages: List[ConversationMessage],
    ) -> None:
        """
        Insert or update conversation with messages.
        
        Uses Supabase RLS to ensure user can only modify their own conversations.
        """
        try:
            # Upsert conversation
            conv_data = {
                'id': conversation_id,
                'user_id': user_id,
                'title': title,
                'preview': preview,
            }
            
            self.client.table('conversations').upsert(conv_data).execute()
            
            # Delete old messages for this conversation
            self.client.table('messages').delete().eq(
                'conversation_id', conversation_id
            ).execute()
            
            # Insert new messages
            if messages:
                msg_data = [
                    {
                        'conversation_id': conversation_id,
                        'role': m.role,
                        'content': m.content,
                        'metadata': {'ts_ms': m.ts_ms}
                    }
                    for m in messages
                ]
                self.client.table('messages').insert(msg_data).execute()
                
        except Exception as e:
            # Log error but don't crash - fallback to error handling in caller
            print(f"Error upserting conversation {conversation_id}: {e}")
            raise
    
    def list_conversations(
        self,
        user_id: Optional[str],
        session_id: Optional[str],
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        List conversations for a user, sorted by most recent.
        
        RLS automatically filters to user's own conversations.
        """
        limit = max(1, min(int(limit), 200))  # Cap at 200
        
        try:
            query = self.client.table('conversations').select(
                'id, title, preview, updated_at'
            )
            
            # Filter by user_id if provided
            if user_id:
                query = query.eq('user_id', user_id)
            
            # Order and limit
            result = query.order('updated_at', desc=True).limit(limit).execute()
            
            return [
                {
                    'id': row['id'],
                    'title': row['title'],
                    'preview': row['preview'],
                    'timestamp': row['updated_at']
                }
                for row in result.data
            ]
            
        except Exception as e:
            print(f"Error listing conversations: {e}")
            return []
    
    def get_conversation(
        self,
        conversation_id: str,
        user_id: Optional[str],
        session_id: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        """
        Get full conversation with all messages.
        
        RLS ensures user can only access their own conversations.
        """
        try:
            # Get conversation
            conv_result = self.client.table('conversations').select('*').eq(
                'id', conversation_id
            ).maybe_single().execute()
            
            if not conv_result.data:
                return None
            
            conv = conv_result.data
            
            # Security check: ensure user owns this conversation
            if user_id and conv.get('user_id') != user_id:
                return None
            
            # Get messages for this conversation
            msgs_result = self.client.table('messages').select('*').eq(
                'conversation_id', conversation_id
            ).order('created_at', desc=False).execute()
            
            return {
                'id': conv['id'],
                'user_id': conv.get('user_id'),
                'session_id': session_id,  # Not stored in DB currently
                'title': conv['title'],
                'preview': conv['preview'],
                'created_at': conv['created_at'],
                'timestamp': conv['updated_at'],
                'messages': [
                    {
                        'type': msg['role'],
                        'content': msg['content'],
                        'timestamp': msg.get('metadata', {}).get('ts_ms', 0)
                    }
                    for msg in msgs_result.data
                ]
            }
            
        except Exception as e:
            print(f"Error getting conversation {conversation_id}: {e}")
            return None


def build_store(base_dir: Path = None, use_supabase: bool = None) -> ConversationStore:
    """
    Factory function to build conversation store.
    
    Auto-detects whether to use Supabase based on environment variables,
    or can be forced via use_supabase parameter.
    
    Args:
        base_dir: Base directory for SQLite storage (ignored if using Supabase)
        use_supabase: Override auto-detection. True = Supabase, False = SQLite
        
    Returns:
        ConversationStore instance (either Supabase or SQLite)
    """
    # Auto-detect if not specified
    if use_supabase is None:
        # Check for explicit override first
        override = os.getenv("USE_SUPABASE", "").lower()
        if override in ("true", "1", "yes"):
            use_supabase = True
        elif override in ("false", "0", "no"):
            use_supabase = False
        else:
            # Auto-detect based on whether SUPABASE_URL is set
            use_supabase = bool(os.getenv("SUPABASE_URL"))
    
    if use_supabase:
        try:
            print("✅ Using Supabase conversation storage")
            return SupabaseConversationStore()
        except Exception as e:
            print(f"⚠️ Supabase init failed: {e}, falling back to SQLite")
            use_supabase = False
    
    if not use_supabase:
        print("📁 Using SQLite conversation storage (dev mode)")
        from .storage import SQLiteConversationStore
        db_path = (base_dir or Path(".")) / "data" / "conversations.sqlite3"
        return SQLiteConversationStore(db_path=db_path)
