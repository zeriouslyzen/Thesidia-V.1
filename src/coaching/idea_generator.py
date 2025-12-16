#!/usr/bin/env python3
"""
Idea Generator - Generates creative ideas for users across disciplines
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import random
from datetime import datetime


class IdeaGenerator:
    """Generates creative ideas based on discipline, interests, and context"""
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(__file__).parent.parent.parent
        
        # Idea templates by discipline
        self.idea_templates = self._load_idea_templates()
    
    def _load_idea_templates(self) -> Dict[str, Dict]:
        """Load idea generation templates for each discipline"""
        return {
            "art": {
                "color": [
                    "Create a palette using only colors you've never used together",
                    "Generate colors based on emotions you want to evoke",
                    "Use complementary colors in unexpected ways",
                    "Create a monochromatic series with texture variation",
                    "Mix digital and traditional color techniques"
                ],
                "technique": [
                    "Combine two techniques you've never combined",
                    "Use unconventional tools for your medium",
                    "Experiment with scale (micro or macro)",
                    "Blend digital and analog processes",
                    "Create art that changes over time"
                ],
                "concept": [
                    "Explore a concept from a new angle",
                    "Create work that challenges your assumptions",
                    "Make art about something you've never explored",
                    "Combine personal experience with universal themes",
                    "Create interactive or participatory art"
                ]
            },
            "health": {
                "bioelectric": [
                    "Optimize your bioelectric field through specific frequencies",
                    "Create a daily bioelectric reset routine",
                    "Experiment with grounding techniques",
                    "Use light therapy to enhance bioelectric health",
                    "Track bioelectric patterns and optimize"
                ],
                "nutrition": [
                    "Create a nutrition framework based on your unique biochemistry",
                    "Experiment with timing of meals for optimal energy",
                    "Try elimination protocols to identify sensitivities",
                    "Optimize micronutrient intake based on genetic factors",
                    "Create personalized meal timing for your circadian rhythm"
                ],
                "movement": [
                    "Design a movement practice that combines multiple modalities",
                    "Create a recovery protocol specific to your needs",
                    "Experiment with movement patterns you've never tried",
                    "Develop a practice that adapts to your daily energy",
                    "Combine strength, mobility, and breathwork"
                ]
            },
            "business": {
                "strategy": [
                    "Create a business model that combines multiple revenue streams",
                    "Develop a unique value proposition in your market",
                    "Build a framework for rapid iteration and learning",
                    "Create systems that scale without you",
                    "Design a business that serves multiple customer segments"
                ],
                "growth": [
                    "Develop a growth framework specific to your stage",
                    "Create a customer acquisition system",
                    "Build partnerships that accelerate growth",
                    "Design a retention strategy that creates advocates",
                    "Create a framework for entering new markets"
                ],
                "innovation": [
                    "Combine ideas from different industries",
                    "Create a new approach to an old problem",
                    "Build something that doesn't exist yet",
                    "Design a business model that disrupts the status quo",
                    "Create a framework for continuous innovation"
                ]
            },
            "fitness": {
                "training": [
                    "Create a training program that combines multiple modalities",
                    "Design periodization based on your specific goals",
                    "Develop a program that adapts to your recovery",
                    "Create a framework for skill acquisition",
                    "Design training that prevents injury while maximizing gains"
                ],
                "nutrition": [
                    "Create a nutrition plan that supports your training",
                    "Develop meal timing strategies for performance",
                    "Design a framework for optimizing body composition",
                    "Create a recovery nutrition protocol",
                    "Develop a nutrition system that adapts to training load"
                ],
                "performance": [
                    "Create a framework for peak performance",
                    "Design a system for tracking and optimizing metrics",
                    "Develop protocols for competition preparation",
                    "Create a recovery framework for high performance",
                    "Design a system for long-term athletic development"
                ]
            },
            "science": {
                "research": [
                    "Design an experiment that tests a novel hypothesis",
                    "Create a research framework that combines multiple methods",
                    "Develop a study that bridges disciplines",
                    "Design research that addresses real-world problems",
                    "Create a framework for reproducible research"
                ],
                "experimentation": [
                    "Develop a new experimental protocol",
                    "Create a framework for systematic exploration",
                    "Design experiments that test multiple variables",
                    "Develop methods for measuring previously unmeasurable phenomena",
                    "Create a framework for iterative experimentation"
                ],
                "analysis": [
                    "Develop new analytical frameworks",
                    "Create methods for synthesizing complex data",
                    "Design visualization techniques for your data",
                    "Develop frameworks for pattern recognition",
                    "Create analytical approaches that reveal hidden insights"
                ]
            },
            "general": {
                "learning": [
                    "Create a learning framework that accelerates mastery",
                    "Develop a system for connecting concepts across domains",
                    "Design a practice routine that builds expertise",
                    "Create a framework for teaching what you learn",
                    "Develop methods for retaining and applying knowledge"
                ],
                "growth": [
                    "Design a personal growth framework",
                    "Create systems for tracking progress",
                    "Develop challenges that push your boundaries",
                    "Create a framework for continuous improvement",
                    "Design a system for achieving long-term goals"
                ],
                "innovation": [
                    "Combine ideas from different fields",
                    "Create new approaches to old problems",
                    "Develop frameworks that others can use",
                    "Design systems that create value",
                    "Create something that didn't exist before"
                ]
            }
        }
    
    def generate(self, discipline: str, interests: List[str] = None,
                 completed_items: List[str] = None, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate creative idea
        
        Args:
            discipline: Discipline name
            interests: List of user interests
            completed_items: List of previously completed items (to avoid repetition)
            context: Optional context from conversation
            
        Returns:
            Idea dictionary with description, approach, and examples
        """
        # Get templates for discipline
        templates = self.idea_templates.get(discipline, self.idea_templates["general"])
        
        # Determine idea category based on interests or context
        category = self._determine_category(interests, context, templates)
        
        # Get ideas for category
        category_ideas = templates.get(category, templates.get(list(templates.keys())[0], []))
        
        # Filter out completed ideas
        available_ideas = [idea for idea in category_ideas 
                          if not any(completed in idea.lower() for completed in (completed_items or []))]
        
        if not available_ideas:
            available_ideas = category_ideas
        
        # Select and personalize idea
        base_idea = random.choice(available_ideas) if available_ideas else "Explore new approaches"
        
        # Personalize based on interests
        personalized_idea = self._personalize_idea(base_idea, interests, context)
        
        # Generate approach and examples
        approach = self._generate_approach(personalized_idea, discipline, category)
        examples = self._generate_examples(personalized_idea, discipline)
        
        idea = {
            "discipline": discipline,
            "category": category,
            "idea": personalized_idea,
            "approach": approach,
            "examples": examples,
            "context": context,
            "created_at": datetime.now().isoformat()
        }
        
        return idea
    
    def _determine_category(self, interests: List[str], context: Optional[str], 
                           templates: Dict) -> str:
        """Determine which category of idea to generate"""
        if context:
            context_lower = context.lower()
            for category in templates.keys():
                if category in context_lower:
                    return category
        
        if interests:
            for interest in interests[:2]:
                interest_lower = interest.lower()
                for category in templates.keys():
                    if category in interest_lower or interest_lower in category:
                        return category
        
        # Default to first category
        return list(templates.keys())[0] if templates else "general"
    
    def _personalize_idea(self, idea: str, interests: List[str], 
                         context: Optional[str]) -> str:
        """Personalize idea based on user interests"""
        if interests:
            # Try to incorporate top interest
            top_interest = interests[0] if interests else None
            if top_interest and top_interest.lower() not in idea.lower():
                # Add interest context
                return f"{idea} (focusing on {top_interest})"
        
        return idea
    
    def _generate_approach(self, idea: str, discipline: str, category: str) -> List[str]:
        """Generate approach steps for implementing the idea"""
        approaches = {
            "art": [
                "Research and gather inspiration",
                "Experiment with small studies",
                "Develop your unique approach",
                "Create a series exploring the idea",
                "Reflect and iterate"
            ],
            "health": [
                "Research the science behind the approach",
                "Start with small experiments",
                "Track your results",
                "Adjust based on data",
                "Share what you learn"
            ],
            "business": [
                "Validate the idea with research",
                "Create a small test or MVP",
                "Gather feedback",
                "Iterate and improve",
                "Scale what works"
            ],
            "fitness": [
                "Research best practices",
                "Start with low intensity",
                "Track performance metrics",
                "Gradually increase challenge",
                "Optimize based on results"
            ],
            "science": [
                "Review existing literature",
                "Design your experiment",
                "Execute systematically",
                "Analyze results",
                "Draw conclusions and share"
            ],
            "general": [
                "Research the concept",
                "Start with small steps",
                "Track your progress",
                "Iterate and improve",
                "Share your learnings"
            ]
        }
        
        return approaches.get(discipline, approaches["general"])
    
    def _generate_examples(self, idea: str, discipline: str) -> List[str]:
        """Generate examples of the idea"""
        examples = {
            "art": [
                "Create a color study exploring emotional resonance",
                "Combine digital and traditional techniques in one piece",
                "Make art that responds to viewer interaction"
            ],
            "health": [
                "Design a bioelectric optimization protocol",
                "Create a personalized nutrition framework",
                "Develop a movement practice that adapts to your needs"
            ],
            "business": [
                "Build a business model with multiple revenue streams",
                "Create a growth framework for your stage",
                "Design systems that scale automatically"
            ],
            "fitness": [
                "Develop a training program that combines modalities",
                "Create a nutrition plan that supports performance",
                "Design a recovery protocol for your specific needs"
            ],
            "science": [
                "Design an experiment that tests novel hypotheses",
                "Create a research framework combining methods",
                "Develop analytical approaches for complex data"
            ],
            "general": [
                "Create a learning framework for mastery",
                "Develop systems for continuous improvement",
                "Design approaches that create value"
            ]
        }
        
        return examples.get(discipline, examples["general"])
