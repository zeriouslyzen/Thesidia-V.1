#!/usr/bin/env python3
"""
KIM Storage Module - Database models and queries for message persistence
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

class KIMStorage:
    """Database storage for KIM messages and metadata"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Default to data/kim directory
            project_root = Path(__file__).resolve().parent.parent.parent
            db_dir = project_root / 'data' / 'kim'
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(db_dir / 'kim_messages.db')
        
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                room_id TEXT NOT NULL,
                sender_id TEXT NOT NULL,
                encrypted_content TEXT NOT NULL,
                iv TEXT NOT NULL,
                mode TEXT DEFAULT 'AES-GCM',
                timestamp TEXT NOT NULL,
                parent_message_id TEXT,
                edited INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Read receipts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS read_receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                read_at TEXT NOT NULL,
                UNIQUE(message_id, user_id),
                FOREIGN KEY (message_id) REFERENCES messages(message_id)
            )
        ''')
        
        # Reactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                reaction_type TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(message_id, user_id, reaction_type),
                FOREIGN KEY (message_id) REFERENCES messages(message_id)
            )
        ''')
        
        # Users table (link KIM to Katanx)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kim_users (
                kim_user_id TEXT PRIMARY KEY,
                katanx_user_id TEXT,
                public_key TEXT NOT NULL,
                nickname TEXT NOT NULL,
                display_name TEXT,
                avatar_url TEXT,
                status TEXT DEFAULT 'online',
                status_message TEXT,
                last_seen TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_room ON messages(room_id, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_read_receipts_message ON read_receipts(message_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reactions_message ON reactions(message_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_kim_users_katanx ON kim_users(katanx_user_id)')
        
        conn.commit()
        conn.close()
    
    def store_message(self, message_id: str, room_id: str, sender_id: str, 
                     encrypted_content: str, iv: str, mode: str = 'AES-GCM',
                     parent_message_id: Optional[str] = None) -> bool:
        """Store an encrypted message"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO messages 
                (message_id, room_id, sender_id, encrypted_content, iv, mode, timestamp, parent_message_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                message_id,
                room_id,
                sender_id,
                encrypted_content,
                iv,
                mode,
                datetime.now().isoformat(),
                parent_message_id
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error storing message: {e}")
            return False
    
    def get_messages(self, room_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get messages for a room with pagination"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM messages 
                WHERE room_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ? OFFSET ?
            ''', (room_id, limit, offset))
            
            rows = cursor.fetchall()
            messages = [dict(row) for row in rows]
            
            conn.close()
            return messages
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []
    
    def mark_message_read(self, message_id: str, user_id: str) -> bool:
        """Mark a message as read by a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO read_receipts (message_id, user_id, read_at)
                VALUES (?, ?, ?)
            ''', (message_id, user_id, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error marking message read: {e}")
            return False
    
    def get_read_receipts(self, message_id: str) -> List[Dict[str, Any]]:
        """Get read receipts for a message"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM read_receipts 
                WHERE message_id = ?
            ''', (message_id,))
            
            rows = cursor.fetchall()
            receipts = [dict(row) for row in rows]
            
            conn.close()
            return receipts
        except Exception as e:
            print(f"Error getting read receipts: {e}")
            return []
    
    def add_reaction(self, message_id: str, user_id: str, reaction_type: str) -> bool:
        """Add a reaction to a message"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO reactions (message_id, user_id, reaction_type, created_at)
                VALUES (?, ?, ?, ?)
            ''', (message_id, user_id, reaction_type, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding reaction: {e}")
            return False
    
    def get_reactions(self, message_id: str) -> List[Dict[str, Any]]:
        """Get reactions for a message"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM reactions 
                WHERE message_id = ?
            ''', (message_id,))
            
            rows = cursor.fetchall()
            reactions = [dict(row) for row in rows]
            
            conn.close()
            return reactions
        except Exception as e:
            print(f"Error getting reactions: {e}")
            return []
    
    def register_kim_user(self, kim_user_id: str, public_key: str, nickname: str,
                          katanx_user_id: Optional[str] = None, display_name: Optional[str] = None,
                          avatar_url: Optional[str] = None) -> bool:
        """Register or update a KIM user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO kim_users 
                (kim_user_id, katanx_user_id, public_key, nickname, display_name, avatar_url, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                kim_user_id,
                katanx_user_id,
                public_key,
                nickname,
                display_name or nickname,
                avatar_url,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error registering KIM user: {e}")
            return False
    
    def get_kim_user(self, kim_user_id: str) -> Optional[Dict[str, Any]]:
        """Get KIM user info"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM kim_users WHERE kim_user_id = ?', (kim_user_id,))
            row = cursor.fetchone()
            
            conn.close()
            return dict(row) if row else None
        except Exception as e:
            print(f"Error getting KIM user: {e}")
            return None
    
    def update_user_status(self, kim_user_id: str, status: str, status_message: Optional[str] = None) -> bool:
        """Update user presence status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE kim_users 
                SET status = ?, status_message = ?, last_seen = ?, updated_at = ?
                WHERE kim_user_id = ?
            ''', (status, status_message, datetime.now().isoformat(), datetime.now().isoformat(), kim_user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating user status: {e}")
            return False

