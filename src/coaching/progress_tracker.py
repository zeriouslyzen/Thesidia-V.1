#!/usr/bin/env python3
"""
Progress Tracker - Tracks user progress across disciplines
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime
from collections import defaultdict


class ProgressTracker:
    """Tracks user progress, milestones, and challenges"""
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(__file__).parent.parent.parent
        self.progress_dir = self.base_dir / "data" / "coaching_progress"
        self.progress_dir.mkdir(parents=True, exist_ok=True)
        
        # Challenge templates by discipline and level
        self.challenge_templates = self._load_challenge_templates()
    
    def _load_challenge_templates(self) -> Dict[str, Dict]:
        """Load challenge templates for each discipline and level"""
        return {
            "art": {
                "beginner": [
                    "Create 10 pieces using only primary colors",
                    "Draw the same subject 5 times with different techniques",
                    "Complete a color theory study",
                    "Create art in a style you've never tried"
                ],
                "intermediate": [
                    "Create a series exploring one concept deeply",
                    "Combine 3 different mediums in one piece",
                    "Create art that tells a story",
                    "Experiment with scale (very large or very small)"
                ],
                "advanced": [
                    "Create a body of work that defines your style",
                    "Teach your technique to someone else",
                    "Create art that challenges conventions",
                    "Build a portfolio that tells your artistic journey"
                ]
            },
            "health": {
                "beginner": [
                    "Track your health metrics for 30 days",
                    "Implement one new health habit",
                    "Complete a basic health assessment",
                    "Try a new form of movement"
                ],
                "intermediate": [
                    "Optimize one health system (sleep, nutrition, movement)",
                    "Complete a 30-day bioelectric optimization protocol",
                    "Design a personalized nutrition framework",
                    "Create a recovery protocol"
                ],
                "advanced": [
                    "Achieve peak bioelectric health",
                    "Design a longevity protocol",
                    "Optimize all health systems simultaneously",
                    "Mentor someone in health optimization"
                ]
            },
            "business": {
                "beginner": [
                    "Validate a business idea",
                    "Create a basic business plan",
                    "Launch an MVP",
                    "Get your first customer"
                ],
                "intermediate": [
                    "Scale to 10x revenue",
                    "Build systems that run without you",
                    "Enter a new market",
                    "Create a framework for growth"
                ],
                "advanced": [
                    "Build a market-leading business",
                    "Create a business that generates multiple revenue streams",
                    "Design a business model others copy",
                    "Mentor other entrepreneurs"
                ]
            },
            "fitness": {
                "beginner": [
                    "Establish a consistent training routine",
                    "Learn proper form for basic movements",
                    "Complete a 30-day movement challenge",
                    "Track your progress metrics"
                ],
                "intermediate": [
                    "Achieve a specific performance goal",
                    "Complete a periodized training cycle",
                    "Optimize your nutrition for performance",
                    "Design a recovery protocol"
                ],
                "advanced": [
                    "Achieve elite-level performance",
                    "Specialize in a specific area",
                    "Coach others to achieve their goals",
                    "Develop new training methodologies"
                ]
            },
            "science": {
                "beginner": [
                    "Complete a basic experiment",
                    "Document your research process",
                    "Learn a new research method",
                    "Analyze data from an experiment"
                ],
                "intermediate": [
                    "Design and execute a research study",
                    "Publish your findings",
                    "Collaborate on research",
                    "Develop new analytical methods"
                ],
                "advanced": [
                    "Make a significant discovery",
                    "Develop new theoretical frameworks",
                    "Mentor other researchers",
                    "Create lasting impact in your field"
                ]
            },
            "general": {
                "beginner": [
                    "Establish a consistent practice",
                    "Learn the fundamentals",
                    "Track your progress",
                    "Complete a basic challenge"
                ],
                "intermediate": [
                    "Achieve an intermediate milestone",
                    "Integrate multiple skills",
                    "Create something new",
                    "Push your boundaries"
                ],
                "advanced": [
                    "Achieve mastery",
                    "Teach others",
                    "Innovate in your field",
                    "Create lasting impact"
                ]
            }
        }
    
    def track_milestone(self, user_profile: Dict[str, Any], discipline: str, milestone: str):
        """
        Track a milestone achievement
        
        Args:
            user_profile: User's coaching profile
            discipline: Discipline name
            milestone: Milestone achieved
        """
        if discipline not in user_profile.get("disciplines", {}):
            user_profile.setdefault("disciplines", {})[discipline] = {
                "level": "beginner",
                "interests": [],
                "completed_frameworks": [],
                "challenges_completed": [],
                "goals": [],
                "milestones": []
            }
        
        discipline_data = user_profile["disciplines"][discipline]
        
        if "milestones" not in discipline_data:
            discipline_data["milestones"] = []
        
        milestone_entry = {
            "milestone": milestone,
            "timestamp": datetime.now().isoformat()
        }
        
        discipline_data["milestones"].append(milestone_entry)
        
        # Update level based on milestones
        self._update_level(user_profile, discipline)
    
    def _update_level(self, user_profile: Dict[str, Any], discipline: str):
        """Update user level based on milestones and challenges completed"""
        discipline_data = user_profile.get("disciplines", {}).get(discipline, {})
        milestones = discipline_data.get("milestones", [])
        challenges = discipline_data.get("challenges_completed", [])
        
        total_achievements = len(milestones) + len(challenges)
        
        if total_achievements < 3:
            discipline_data["level"] = "beginner"
        elif total_achievements < 10:
            discipline_data["level"] = "intermediate"
        else:
            discipline_data["level"] = "advanced"
    
    def create_challenge(self, discipline: str, level: str) -> Dict[str, Any]:
        """
        Create a challenge for the user
        
        Args:
            discipline: Discipline name
            level: User level
            
        Returns:
            Challenge dictionary
        """
        templates = self.challenge_templates.get(discipline, self.challenge_templates["general"])
        level_challenges = templates.get(level, templates.get("intermediate", []))
        
        if not level_challenges:
            level_challenges = ["Complete a challenge in this discipline"]
        
        import random
        challenge_description = random.choice(level_challenges)
        
        challenge = {
            "discipline": discipline,
            "level": level,
            "description": challenge_description,
            "steps": self._generate_challenge_steps(challenge_description, discipline, level),
            "success_criteria": self._generate_success_criteria(discipline, level),
            "created_at": datetime.now().isoformat()
        }
        
        return challenge
    
    def _generate_challenge_steps(self, description: str, discipline: str, level: str) -> List[str]:
        """Generate steps for completing the challenge"""
        steps = []
        
        if level == "beginner":
            steps = [
                "Break down the challenge into small steps",
                "Start with the first step",
                "Practice consistently",
                "Track your progress",
                "Complete and reflect"
            ]
        elif level == "intermediate":
            steps = [
                "Plan your approach",
                "Set up systems for tracking",
                "Execute systematically",
                "Adjust based on results",
                "Complete and analyze outcomes"
            ]
        else:  # advanced
            steps = [
                "Design an innovative approach",
                "Execute with precision",
                "Document your process",
                "Share your learnings",
                "Create lasting impact"
            ]
        
        return steps
    
    def _generate_success_criteria(self, discipline: str, level: str) -> List[str]:
        """Generate success criteria for the challenge"""
        criteria = []
        
        if level == "beginner":
            criteria = [
                "Complete the challenge",
                "Learn something new",
                "Track your progress",
                "Reflect on what you learned"
            ]
        elif level == "intermediate":
            criteria = [
                "Complete the challenge with quality",
                "Achieve measurable improvement",
                "Document your process",
                "Apply learnings to future work"
            ]
        else:  # advanced
            criteria = [
                "Exceed expectations",
                "Create something innovative",
                "Share knowledge with others",
                "Build on this for future challenges"
            ]
        
        return criteria
    
    def get_progress_summary(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary of user's progress across all disciplines"""
        summary = {
            "total_milestones": 0,
            "total_challenges": 0,
            "disciplines": {},
            "overall_level": "beginner"
        }
        
        disciplines = user_profile.get("disciplines", {})
        
        for discipline, data in disciplines.items():
            milestones = len(data.get("milestones", []))
            challenges = len(data.get("challenges_completed", []))
            level = data.get("level", "beginner")
            
            summary["total_milestones"] += milestones
            summary["total_challenges"] += challenges
            
            summary["disciplines"][discipline] = {
                "level": level,
                "milestones": milestones,
                "challenges": challenges
            }
        
        # Determine overall level
        total_achievements = summary["total_milestones"] + summary["total_challenges"]
        if total_achievements >= 20:
            summary["overall_level"] = "advanced"
        elif total_achievements >= 5:
            summary["overall_level"] = "intermediate"
        
        return summary
