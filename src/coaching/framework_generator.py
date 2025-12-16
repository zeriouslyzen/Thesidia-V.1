#!/usr/bin/env python3
"""
Framework Generator - Generates personalized frameworks for users
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime


class FrameworkGenerator:
    """Generates personalized frameworks based on discipline, level, and goals"""
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(__file__).parent.parent.parent
        self.frameworks_dir = self.base_dir / "data" / "coaching_frameworks"
        self.frameworks_dir.mkdir(parents=True, exist_ok=True)
        
        # Framework templates by discipline
        self.framework_templates = self._load_framework_templates()
    
    def _load_framework_templates(self) -> Dict[str, Dict]:
        """Load framework templates for each discipline"""
        return {
            "art": {
                "beginner": {
                    "structure": ["Foundation", "Practice", "Exploration", "Reflection"],
                    "focus_areas": ["Basic techniques", "Color theory", "Composition", "Style development"]
                },
                "intermediate": {
                    "structure": ["Advanced Techniques", "Personal Style", "Cross-Media", "Innovation"],
                    "focus_areas": ["Master techniques", "Develop unique voice", "Experiment with media", "Push boundaries"]
                },
                "advanced": {
                    "structure": ["Mastery", "Innovation", "Teaching", "Legacy"],
                    "focus_areas": ["Perfect craft", "Create new movements", "Mentor others", "Build lasting impact"]
                }
            },
            "health": {
                "beginner": {
                    "structure": ["Assessment", "Foundation", "Habits", "Tracking"],
                    "focus_areas": ["Baseline health", "Basic nutrition", "Simple exercise", "Progress tracking"]
                },
                "intermediate": {
                    "structure": ["Optimization", "Advanced Nutrition", "Performance", "Recovery"],
                    "focus_areas": ["Optimize systems", "Advanced nutrition", "Performance training", "Recovery protocols"]
                },
                "advanced": {
                    "structure": ["Biohacking", "Longevity", "Peak Performance", "Teaching"],
                    "focus_areas": ["Biohacking protocols", "Longevity strategies", "Peak performance", "Share knowledge"]
                }
            },
            "business": {
                "beginner": {
                    "structure": ["Foundation", "Market Research", "MVP", "Launch"],
                    "focus_areas": ["Business basics", "Market understanding", "Product development", "Launch strategy"]
                },
                "intermediate": {
                    "structure": ["Growth", "Optimization", "Scaling", "Systems"],
                    "focus_areas": ["Growth strategies", "Process optimization", "Scale operations", "Build systems"]
                },
                "advanced": {
                    "structure": ["Innovation", "Market Leadership", "Expansion", "Legacy"],
                    "focus_areas": ["Innovate", "Lead market", "Expand", "Build legacy"]
                }
            },
            "fitness": {
                "beginner": {
                    "structure": ["Foundation", "Form", "Consistency", "Progress"],
                    "focus_areas": ["Basic movements", "Proper form", "Regular practice", "Track progress"]
                },
                "intermediate": {
                    "structure": ["Advanced Training", "Periodization", "Nutrition", "Recovery"],
                    "focus_areas": ["Advanced techniques", "Training cycles", "Performance nutrition", "Recovery"]
                },
                "advanced": {
                    "structure": ["Elite Performance", "Specialization", "Coaching", "Innovation"],
                    "focus_areas": ["Elite performance", "Specialize", "Coach others", "Innovate methods"]
                }
            },
            "science": {
                "beginner": {
                    "structure": ["Learning", "Experimentation", "Documentation", "Analysis"],
                    "focus_areas": ["Learn fundamentals", "Simple experiments", "Document everything", "Basic analysis"]
                },
                "intermediate": {
                    "structure": ["Research Design", "Advanced Methods", "Publication", "Collaboration"],
                    "focus_areas": ["Design studies", "Advanced methods", "Publish findings", "Collaborate"]
                },
                "advanced": {
                    "structure": ["Innovation", "Theoretical Development", "Mentorship", "Impact"],
                    "focus_areas": ["Innovate", "Develop theory", "Mentor", "Create impact"]
                }
            },
            "general": {
                "beginner": {
                    "structure": ["Foundation", "Practice", "Learning", "Growth"],
                    "focus_areas": ["Build foundation", "Regular practice", "Continuous learning", "Track growth"]
                },
                "intermediate": {
                    "structure": ["Advanced Skills", "Integration", "Innovation", "Mastery"],
                    "focus_areas": ["Advanced skills", "Integrate knowledge", "Innovate", "Move toward mastery"]
                },
                "advanced": {
                    "structure": ["Mastery", "Teaching", "Innovation", "Legacy"],
                    "focus_areas": ["Achieve mastery", "Teach others", "Innovate", "Build legacy"]
                }
            }
        }
    
    def generate(self, discipline: str, level: str, interests: List[str] = None,
                 goal: Optional[str] = None, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate personalized framework
        
        Args:
            discipline: Discipline name
            level: User level (beginner, intermediate, advanced)
            interests: List of user interests
            goal: Optional specific goal
            context: Optional context from conversation
            
        Returns:
            Framework dictionary
        """
        # Get template for discipline and level
        template = self.framework_templates.get(discipline, self.framework_templates["general"])
        level_template = template.get(level, template.get("intermediate", {}))
        
        structure = level_template.get("structure", ["Foundation", "Practice", "Growth", "Mastery"])
        focus_areas = level_template.get("focus_areas", ["Build skills", "Practice", "Grow", "Master"])
        
        # Personalize based on interests
        if interests:
            focus_areas = self._personalize_focus_areas(focus_areas, interests, discipline)
        
        # Generate actionable steps
        steps = self._generate_steps(structure, focus_areas, level, goal)
        
        framework = {
            "discipline": discipline,
            "level": level,
            "structure": structure,
            "focus_areas": focus_areas,
            "steps": steps,
            "goal": goal,
            "context": context,
            "created_at": datetime.now().isoformat()
        }
        
        return framework
    
    def _personalize_focus_areas(self, focus_areas: List[str], interests: List[str], 
                                 discipline: str) -> List[str]:
        """Personalize focus areas based on user interests"""
        personalized = []
        
        # Map interests to focus areas
        for area in focus_areas:
            # Check if any interest relates to this area
            area_lower = area.lower()
            for interest in interests[:3]:  # Top 3 interests
                interest_lower = interest.lower()
                if any(word in area_lower for word in interest_lower.split()):
                    # Customize area with interest
                    personalized.append(f"{area} (focusing on {interest})")
                    break
            else:
                personalized.append(area)
        
        return personalized[:len(focus_areas)]
    
    def _generate_steps(self, structure: List[str], focus_areas: List[str], 
                       level: str, goal: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generate actionable steps for framework"""
        steps = []
        
        for i, (phase, focus) in enumerate(zip(structure, focus_areas), 1):
            step = {
                "phase": phase,
                "focus": focus,
                "order": i,
                "actions": self._generate_actions_for_phase(phase, focus, level, i)
            }
            steps.append(step)
        
        # Add goal-specific step if provided
        if goal:
            steps.append({
                "phase": "Goal Achievement",
                "focus": goal,
                "order": len(steps) + 1,
                "actions": [f"Define specific milestones for: {goal}",
                           f"Create timeline for achieving: {goal}",
                           f"Track progress toward: {goal}"]
            })
        
        return steps
    
    def _generate_actions_for_phase(self, phase: str, focus: str, level: str, 
                                    phase_number: int) -> List[str]:
        """Generate specific actions for a phase"""
        actions = []
        
        if level == "beginner":
            actions = [
                f"Start with basic {focus.lower()}",
                f"Practice {focus.lower()} daily",
                f"Track your progress in {focus.lower()}",
                f"Seek feedback on {focus.lower()}"
            ]
        elif level == "intermediate":
            actions = [
                f"Deepen your {focus.lower()}",
                f"Experiment with advanced {focus.lower()}",
                f"Connect {focus.lower()} to other areas",
                f"Challenge yourself in {focus.lower()}"
            ]
        else:  # advanced
            actions = [
                f"Master {focus.lower()}",
                f"Innovate in {focus.lower()}",
                f"Teach {focus.lower()} to others",
                f"Create new approaches to {focus.lower()}"
            ]
        
        return actions[:4]  # Limit to 4 actions per phase
