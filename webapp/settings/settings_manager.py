#!/usr/bin/env python3
"""
Settings Manager
Load/save user settings, validation, defaults
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from webapp.social.schema import SettingsSchema
from webapp.middleware.security import security_middleware


class SettingsManager:
    """
    Settings Manager
    Manages user settings with validation and defaults
    """
    
    def __init__(self, base_dir: Path = None):
        """
        Initialize settings manager
        
        Args:
            base_dir: Base directory for data storage
        """
        self.base_dir = base_dir or Path(".")
        self.users_dir = self.base_dir / "data" / "users"
        self.schema = SettingsSchema()
    
    def get_settings(self, user_id: str) -> Dict[str, Any]:
        """
        Get user settings
        
        Args:
            user_id: User ID
            
        Returns:
            Settings dictionary
        """
        settings_file = self.users_dir / user_id / "settings.json"
        
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # Validate and migrate if needed
                    return self._migrate_settings(settings)
            except Exception as e:
                print(f"Warning: Could not load settings for {user_id}: {e}")
        
        # Return default settings
        return self.schema.create_default_settings(user_id)
    
    def save_settings(self, user_id: str, settings: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Save user settings
        
        Args:
            user_id: User ID
            settings: Settings dictionary
            
        Returns:
            Tuple of (success, error_message)
        """
        # Validate settings
        is_valid, error = self.schema.validate_settings(settings)
        if not is_valid:
            return False, error
        
        # Ensure user_id matches
        settings["user_id"] = user_id
        settings["updated_at"] = datetime.now().isoformat()
        
        # Save to file
        settings_file = self.users_dir / user_id / "settings.json"
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def update_settings_section(self, user_id: str, section: str, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Update a specific settings section
        
        Args:
            user_id: User ID
            section: Settings section name (account, privacy, notifications, content, security)
            data: Section data dictionary
            
        Returns:
            Tuple of (success, error_message)
        """
        settings = self.get_settings(user_id)
        
        if section not in settings:
            return False, f"Invalid section: {section}"
        
        # Update section
        settings[section].update(data)
        settings["updated_at"] = datetime.now().isoformat()
        
        return self.save_settings(user_id, settings)
    
    def validate_username(self, username: str, current_user_id: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """
        Validate username format and availability
        
        Args:
            username: Username to validate
            current_user_id: Optional current user ID (to allow keeping own username)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        return security_middleware.validate_username(username)
    
    def _migrate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate settings to current schema version
        
        Args:
            settings: Settings dictionary
            
        Returns:
            Migrated settings dictionary
        """
        # Check if migration needed
        schema_version = settings.get("_schema_version", "1.0")
        
        # For now, just ensure all required sections exist
        default = self.schema.create_default_settings(settings.get("user_id", "unknown"))
        
        # Merge with defaults for missing sections
        for section in ["account", "privacy", "notifications", "content", "security"]:
            if section not in settings:
                settings[section] = default[section]
            else:
                # Merge missing keys
                for key, value in default[section].items():
                    if key not in settings[section]:
                        settings[section][key] = value
        
        return settings

