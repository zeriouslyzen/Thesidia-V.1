#!/usr/bin/env python3
"""
Ally Mechanics - Video game ally engagement patterns
Subtle engagement (NOT obsessive)
Quest tracking, progress indicators, achievements
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path


class AllyMechanics:
    """
    Video game ally mechanics for engagement.
    Subtle, NOT obsessive - natural engagement patterns.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.quests = []  # Research threads as "quests"
        self.achievements = []  # Sophia moments, pattern discoveries
        self.progress = {}  # Progress tracking
        
    def start_quest(self, quest_name: str, description: str) -> str:
        """
        Start a quest (research thread).
        Returns quest ID.
        """
        quest_id = f"quest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        quest = {
            "id": quest_id,
            "name": quest_name,
            "description": description,
            "started": str(datetime.now()),
            "status": "active",
            "progress": 0
        }
        self.quests.append(quest)
        self._save_quests()
        return quest_id
    
    def update_quest_progress(self, quest_id: str, progress: int, note: Optional[str] = None):
        """Update quest progress."""
        for quest in self.quests:
            if quest["id"] == quest_id:
                quest["progress"] = min(100, max(0, progress))
                if note:
                    quest.setdefault("notes", []).append({
                        "timestamp": str(datetime.now()),
                        "note": note
                    })
                self._save_quests()
                break
    
    def complete_quest(self, quest_id: str, result: Optional[str] = None):
        """Complete a quest."""
        for quest in self.quests:
            if quest["id"] == quest_id:
                quest["status"] = "completed"
                quest["completed"] = str(datetime.now())
                if result:
                    quest["result"] = result
                self._save_quests()
                break
    
    def add_achievement(self, achievement_name: str, description: str, category: str = "pattern_discovery"):
        """Add an achievement (Sophia moment, pattern discovery)."""
        achievement = {
            "name": achievement_name,
            "description": description,
            "category": category,
            "timestamp": str(datetime.now())
        }
        self.achievements.append(achievement)
        self._save_achievements()
        return achievement
    
    def get_active_quests(self) -> List[Dict[str, Any]]:
        """Get active quests."""
        return [q for q in self.quests if q.get("status") == "active"]
    
    def generate_ally_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate subtle ally mechanics prompt.
        NOT obsessive - natural engagement.
        """
        active_quests = self.get_active_quests()
        
        if not active_quests and not context:
            return ""  # No quests, no special prompt needed
        
        prompt_parts = [
            "[ALLY MECHANICS - SUBTLE ENGAGEMENT]",
            "",
            "You are a helpful ally. Subtle engagement patterns:",
            ""
        ]
        
        if active_quests:
            prompt_parts.append("Active research threads:")
            for quest in active_quests[:3]:  # Max 3 active quests
                prompt_parts.append(f"- {quest['name']}: {quest.get('progress', 0)}% complete")
            prompt_parts.append("")
        
        prompt_parts.extend([
            "Engagement style:",
            "- Natural, not forced",
            "- Share cool connections when relevant",
            "- NOT 'QUEST STARTED!' or game-like announcements",
            "- Subtle progress indicators, not obsessive tracking",
            "",
            "Be a helpful ally, not a game system."
        ])
        
        return "\n".join(prompt_parts)
    
    def _save_quests(self):
        """Save quests to file."""
        quests_file = self.data_dir / "ally_quests.json"
        with open(quests_file, 'w') as f:
            json.dump(self.quests, f, indent=2)
    
    def _save_achievements(self):
        """Save achievements to file."""
        achievements_file = self.data_dir / "ally_achievements.json"
        with open(achievements_file, 'w') as f:
            json.dump(self.achievements, f, indent=2)

