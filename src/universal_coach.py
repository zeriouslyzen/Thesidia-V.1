#!/usr/bin/env python3
"""
Universal Coach - Comprehensive coaching system across all disciplines
Knows all disciplines, personalizes to each user, generates frameworks and creative ideas
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict

try:
    from .coaching.framework_generator import FrameworkGenerator
    from .coaching.idea_generator import IdeaGenerator
    from .coaching.progress_tracker import ProgressTracker
except ImportError:
    from src.coaching.framework_generator import FrameworkGenerator
    from src.coaching.idea_generator import IdeaGenerator
    from src.coaching.progress_tracker import ProgressTracker


class UniversalCoach:
    """
    Universal coaching system that provides personalized coaching across all disciplines.
    Integrates with existing systems (HealthCoach, UserInterestTracker, etc.)
    """
    
    def __init__(self, base_dir: Path = None, user_memory_manager=None, 
                 user_interest_tracker=None, technical_journey_detector=None):
        """
        Initialize Universal Coach
        
        Args:
            base_dir: Base directory for data storage
            user_memory_manager: UserMemoryManager instance for user history
            user_interest_tracker: UserInterestTracker instance for interests
            technical_journey_detector: TechnicalJourneyDetector instance for domain detection
        """
        self.base_dir = base_dir or Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.coaching_dir = self.data_dir / "coaching_profiles"
        self.coaching_dir.mkdir(parents=True, exist_ok=True)
        
        self.user_memory_manager = user_memory_manager
        self.user_interest_tracker = user_interest_tracker
        self.technical_journey_detector = technical_journey_detector
        
        # Initialize sub-components
        self.framework_generator = FrameworkGenerator(base_dir=base_dir)
        self.idea_generator = IdeaGenerator(base_dir=base_dir)
        self.progress_tracker = ProgressTracker(base_dir=base_dir)
        
        # Discipline detection patterns
        self.discipline_patterns = self._load_discipline_patterns()
        
        # Import discipline-specific coaches
        self.discipline_coaches = {}
        self._load_discipline_coaches()
    
    def _load_discipline_patterns(self) -> Dict[str, Dict]:
        """Load patterns for detecting disciplines"""
        return {
            "art": {
                "keywords": ["art", "artist", "painting", "drawing", "color", "palette", "composition", 
                           "design", "creative", "visual", "aesthetic", "style", "technique", "canvas",
                           "brush", "sketch", "illustration", "digital art", "photography"],
                "coach_module": "art_coach"
            },
            "health": {
                "keywords": ["health", "wellness", "fitness", "exercise", "nutrition", "diet", "supplement",
                           "bioelectric", "energy", "body", "physical", "mental health", "wellbeing"],
                "coach_module": "health_coach"  # Uses existing HealthCoach
            },
            "business": {
                "keywords": ["business", "company", "startup", "entrepreneur", "strategy", "marketing",
                           "sales", "growth", "revenue", "profit", "market", "customer", "product",
                           "brand", "management", "leadership"],
                "coach_module": "business_coach"
            },
            "fitness": {
                "keywords": ["fitness", "workout", "training", "exercise", "gym", "strength", "cardio",
                           "muscle", "endurance", "athletic", "sport", "performance", "recovery",
                           "training program", "workout plan", "fitness routine", "physical training"],
                "coach_module": "fitness_coach"
            },
            "science": {
                "keywords": ["science", "research", "experiment", "hypothesis", "study", "analysis",
                           "data", "methodology", "theory", "physics", "chemistry", "biology", "lab"],
                "coach_module": "science_coach"
            },
            "coding": {
                "keywords": ["code", "programming", "software", "developer", "algorithm", "function",
                           "debug", "framework", "library", "api", "syntax", "language"],
                "coach_module": "general_coach"  # Uses general coach for coding
            }
        }
    
    def _load_discipline_coaches(self):
        """Lazy-load discipline-specific coaches"""
        try:
            try:
                from .coaching.art_coach import ArtCoach
            except ImportError:
                from src.coaching.art_coach import ArtCoach
            self.discipline_coaches["art"] = ArtCoach()
        except ImportError:
            pass
        
        try:
            try:
                from .coaching.business_coach import BusinessCoach
            except ImportError:
                from src.coaching.business_coach import BusinessCoach
            self.discipline_coaches["business"] = BusinessCoach()
        except ImportError:
            pass
        
        try:
            try:
                from .coaching.fitness_coach import FitnessCoach
            except ImportError:
                from src.coaching.fitness_coach import FitnessCoach
            self.discipline_coaches["fitness"] = FitnessCoach()
        except ImportError:
            pass
        
        try:
            try:
                from .coaching.science_coach import ScienceCoach
            except ImportError:
                from src.coaching.science_coach import ScienceCoach
            self.discipline_coaches["science"] = ScienceCoach()
        except ImportError:
            pass
        
        try:
            try:
                from .coaching.general_coach import GeneralCoach
            except ImportError:
                from src.coaching.general_coach import GeneralCoach
            self.discipline_coaches["general"] = GeneralCoach()
        except ImportError:
            pass
    
    def detect_discipline(self, query: str) -> str:
        """
        Detect which discipline the query relates to
        
        Args:
            query: User's query
            
        Returns:
            Discipline name (art, health, business, fitness, science, coding, general)
        """
        query_lower = query.lower()
        discipline_scores = defaultdict(int)
        
        # Score each discipline based on keyword matches
        for discipline, patterns in self.discipline_patterns.items():
            for keyword in patterns["keywords"]:
                if keyword in query_lower:
                    discipline_scores[discipline] += 1
        
        # Also check technical journey detector if available
        if self.technical_journey_detector:
            tech_domain = self.technical_journey_detector.detect_technical_domain(query)
            if tech_domain and tech_domain != "general technical inquiry":
                if tech_domain == "code_cracking":
                    discipline_scores["coding"] += 2
                elif tech_domain in ["chemistry", "physics"]:
                    discipline_scores["science"] += 2
        
        # Return highest scoring discipline, or "general" if no match
        if discipline_scores:
            return max(discipline_scores.items(), key=lambda x: x[1])[0]
        
        return "general"
    
    def get_user_coaching_profile(self, user_id: Optional[str] = None, 
                                  session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get or create user's coaching profile
        
        Args:
            user_id: Optional user ID
            session_id: Optional session ID
            
        Returns:
            User coaching profile dictionary
        """
        # Use user_id or session_id to determine profile file
        profile_id = user_id or session_id or "default"
        profile_file = self.coaching_dir / f"{profile_id}.json"
        
        if profile_file.exists():
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Create default profile
        profile = {
            "user_id": user_id,
            "session_id": session_id,
            "disciplines": {},
            "cross_disciplinary_patterns": [],
            "growth_areas": [],
            "preferred_coaching_style": "balanced",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        # Enhance with user interest tracker data if available
        if self.user_interest_tracker:
            interests = self.user_interest_tracker.get_user_interests()
            if interests.get("primary_focus"):
                profile["growth_areas"].append(interests["primary_focus"])
            if interests.get("top_topics"):
                for topic_data in interests["top_topics"][:5]:
                    topic = topic_data["topic"]
                    # Map topics to disciplines
                    discipline = self.detect_discipline(topic)
                    if discipline not in profile["disciplines"]:
                        profile["disciplines"][discipline] = {
                            "level": "beginner",
                            "interests": [],
                            "completed_frameworks": [],
                            "challenges_completed": [],
                            "goals": []
                        }
                    if topic not in profile["disciplines"][discipline]["interests"]:
                        profile["disciplines"][discipline]["interests"].append(topic)
        
        # Save profile
        self._save_coaching_profile(profile_id, profile)
        
        return profile
    
    def _save_coaching_profile(self, profile_id: str, profile: Dict[str, Any]):
        """Save coaching profile to file"""
        profile["last_updated"] = datetime.now().isoformat()
        profile_file = self.coaching_dir / f"{profile_id}.json"
        try:
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            print(f"Warning: Failed to save coaching profile: {e}")
    
    def generate_framework(self, discipline: str, user_profile: Dict[str, Any], 
                          goal: Optional[str] = None, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate personalized framework for user
        
        Args:
            discipline: Discipline name
            user_profile: User's coaching profile
            goal: Optional specific goal
            context: Optional context from conversation
            
        Returns:
            Framework dictionary with structure, steps, and guidance
        """
        discipline_profile = user_profile.get("disciplines", {}).get(discipline, {})
        level = discipline_profile.get("level", "beginner")
        interests = discipline_profile.get("interests", [])
        
        # Use framework generator
        framework = self.framework_generator.generate(
            discipline=discipline,
            level=level,
            interests=interests,
            goal=goal,
            context=context
        )
        
        return framework
    
    def generate_creative_idea(self, discipline: str, user_profile: Dict[str, Any],
                              context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate creative idea for user
        
        Args:
            discipline: Discipline name
            user_profile: User's coaching profile
            context: Optional context from conversation
            
        Returns:
            Creative idea dictionary with description, approach, and examples
        """
        discipline_profile = user_profile.get("disciplines", {}).get(discipline, {})
        interests = discipline_profile.get("interests", [])
        completed = discipline_profile.get("completed_frameworks", [])
        
        # Use idea generator
        idea = self.idea_generator.generate(
            discipline=discipline,
            interests=interests,
            completed_items=completed,
            context=context
        )
        
        return idea
    
    def create_challenge(self, discipline: str, user_profile: Dict[str, Any],
                        level: Optional[str] = None) -> Dict[str, Any]:
        """
        Create growth challenge for user
        
        Args:
            discipline: Discipline name
            user_profile: User's coaching profile
            level: Optional challenge level (beginner, intermediate, advanced)
            
        Returns:
            Challenge dictionary with description, steps, and success criteria
        """
        discipline_profile = user_profile.get("disciplines", {}).get(discipline, {})
        current_level = level or discipline_profile.get("level", "beginner")
        
        # Get discipline-specific coach if available
        coach = self.discipline_coaches.get(discipline) or self.discipline_coaches.get("general")
        
        if coach and hasattr(coach, 'create_challenge'):
            return coach.create_challenge(current_level, discipline_profile)
        
        # Fallback: use progress tracker
        return self.progress_tracker.create_challenge(discipline, current_level)
    
    def track_progress(self, user_id: Optional[str], discipline: str, milestone: str):
        """
        Track user progress
        
        Args:
            user_id: User ID
            discipline: Discipline name
            milestone: Milestone achieved
        """
        profile = self.get_user_coaching_profile(user_id=user_id)
        self.progress_tracker.track_milestone(profile, discipline, milestone)
        self._save_coaching_profile(user_id or "default", profile)
    
    def analyze_coaching_need(self, query: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze what kind of coaching the user needs
        
        Args:
            query: User's query
            user_profile: User's coaching profile
            
        Returns:
            Analysis dictionary with coaching_type, discipline, and recommendations
        """
        discipline = self.detect_discipline(query)
        
        # Determine coaching type
        query_lower = query.lower()
        coaching_type = "framework"
        
        if any(word in query_lower for word in ["new", "creative", "idea", "different", "novel", "unique"]):
            coaching_type = "idea"
        elif any(word in query_lower for word in ["challenge", "push", "improve", "grow", "next level"]):
            coaching_type = "challenge"
        elif any(word in query_lower for word in ["framework", "structure", "plan", "approach", "method"]):
            coaching_type = "framework"
        
        return {
            "coaching_type": coaching_type,
            "discipline": discipline,
            "recommendations": self._get_recommendations(discipline, user_profile, coaching_type)
        }
    
    def _get_recommendations(self, discipline: str, user_profile: Dict[str, Any], 
                            coaching_type: str) -> List[str]:
        """Get coaching recommendations"""
        recommendations = []
        
        discipline_profile = user_profile.get("disciplines", {}).get(discipline, {})
        level = discipline_profile.get("level", "beginner")
        
        if coaching_type == "idea":
            recommendations.append(f"Generate creative {discipline} ideas based on your {level} level")
        elif coaching_type == "challenge":
            recommendations.append(f"Create {level} challenges to push your {discipline} skills")
        else:
            recommendations.append(f"Build a personalized {discipline} framework for your goals")
        
        return recommendations
