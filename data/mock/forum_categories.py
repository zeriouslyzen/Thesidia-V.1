"""
Forum Category Structure
Defines main categories, subcategories, and tag conventions for the forum system.
"""

from typing import Dict, List, Any

# Tag types for threads
TAG_LEVELS = ['beginner', 'intermediate', 'advanced']
TAG_FORMATS = ['guide', 'question', 'study', 'critique', 'discussion', 'resource']
TAG_SOURCING = ['peer-reviewed', 'clinical', 'traditional', 'anecdotal', 'mixed']

# Main categories with subcategories
FORUM_CATEGORIES = {
    'martial-arts-combative': {
        'name': 'Martial Arts & Combative',
        'description': 'Combat systems, movement arts, and training methodologies',
        'subcategories': [
            {
                'id': 'combatives',
                'name': 'Combatives',
                'description': 'Striking, grappling, weapons training'
            },
            {
                'id': 'internal-arts',
                'name': 'Internal Arts',
                'description': 'Taiji/Bagua/Xingyi, Qigong/Neigong'
            },
            {
                'id': 'movement-arts',
                'name': 'Movement Arts',
                'description': 'Dance, parkour, acrobatics, gymnastics, capoeira, flow arts'
            },
            {
                'id': 'conditioning-biomechanics',
                'name': 'Conditioning & Biomechanics',
                'description': 'Physical preparation and movement science'
            },
            {
                'id': 'coaching-pedagogy',
                'name': 'Coaching / Pedagogy',
                'description': 'Teaching methods and instructional design'
            }
        ]
    },
    'visual': {
        'name': 'Visual',
        'description': 'Visual arts, design, and creative expression',
        'subcategories': [
            {
                'id': 'drawing-painting-sculpture',
                'name': 'Drawing/Painting/Sculpture',
                'description': 'Traditional visual arts'
            },
            {
                'id': 'design',
                'name': 'Design',
                'description': 'Graphic, UX/UI, product design'
            },
            {
                'id': 'photo-film-animation',
                'name': 'Photo/Film/Animation',
                'description': 'Moving images and photography'
            },
            {
                'id': 'architecture',
                'name': 'Architecture',
                'description': 'Built environment and spatial design'
            },
            {
                'id': 'crafts-making',
                'name': 'Crafts/Making',
                'description': 'Jewelry, engraving, fabrication'
            }
        ]
    },
    'internal-spiritual': {
        'name': 'Internal / Spiritual',
        'description': 'Contemplative practices and inner work',
        'subcategories': [
            {
                'id': 'meditation-contemplative',
                'name': 'Meditation & Contemplative Practice',
                'description': 'Mindfulness, concentration, and contemplative traditions'
            },
            {
                'id': 'breathwork-pranayama',
                'name': 'Breathwork / Pranayama',
                'description': 'Breathing practices and techniques'
            },
            {
                'id': 'ritual-indigenous-mystical',
                'name': 'Ritual/Indigenous/Mystical Arts',
                'description': 'Traditional and ceremonial practices (with sourcing respect)'
            },
            {
                'id': 'energy-practices',
                'name': 'Energy Practices',
                'description': 'Qigong internal, energy work, subtle body practices'
            },
            {
                'id': 'ethics-safeguarding',
                'name': 'Ethics & Safeguarding',
                'description': 'Ethical frameworks and safety in practice'
            }
        ]
    },
    'healing': {
        'name': 'Healing',
        'description': 'Therapeutic approaches and recovery systems',
        'subcategories': [
            {
                'id': 'clinical-evidence-based',
                'name': 'Clinical & Evidence-Based',
                'description': 'PT, sports med, rehab, evidence-based approaches'
            },
            {
                'id': 'traditional-systems',
                'name': 'Traditional Systems',
                'description': 'TCM, acupuncture, herbalism, traditional medicine'
            },
            {
                'id': 'bodywork-manual-therapies',
                'name': 'Bodywork & Manual Therapies',
                'description': 'Hands-on healing and therapeutic touch'
            },
            {
                'id': 'recovery-longevity',
                'name': 'Recovery & Longevity',
                'description': 'Recovery protocols and longevity practices'
            },
            {
                'id': 'safety-contraindications',
                'name': 'Safety / Contraindications',
                'description': 'Safety protocols and contraindication awareness'
            }
        ]
    },
    'intellectual-science': {
        'name': 'Intellectual / Science',
        'description': 'Academic inquiry and scientific understanding',
        'subcategories': [
            {
                'id': 'philosophy-epistemology',
                'name': 'Philosophy & Epistemology',
                'description': 'Philosophical inquiry and knowledge theory'
            },
            {
                'id': 'neuroscience-cognition',
                'name': 'Neuroscience / Cognition',
                'description': 'Brain science and cognitive processes'
            },
            {
                'id': 'physiology-biomechanics',
                'name': 'Physiology / Biomechanics',
                'description': 'Body systems and movement mechanics'
            },
            {
                'id': 'data-modeling-systems',
                'name': 'Data, Modeling, and Systems Thinking',
                'description': 'Quantitative analysis and systems approaches'
            },
            {
                'id': 'methodology-study-design',
                'name': 'Methodology & Study Design',
                'description': 'Research methods and experimental design'
            }
        ]
    },
    'performance': {
        'name': 'Performance',
        'description': 'Performance arts and stagecraft',
        'subcategories': [
            {
                'id': 'music-voice',
                'name': 'Music & Voice',
                'description': 'Musical performance and vocal arts'
            },
            {
                'id': 'theater-spoken-word',
                'name': 'Theater / Spoken Word / Storytelling',
                'description': 'Dramatic arts and narrative performance'
            },
            {
                'id': 'performance-movement',
                'name': 'Performance Movement',
                'description': 'Wushu performance, stage martial, dance performance'
            },
            {
                'id': 'stagecraft-production',
                'name': 'Stagecraft / Production',
                'description': 'Technical production and stage management'
            },
            {
                'id': 'presence-audience-dynamics',
                'name': 'Presence & Audience Dynamics',
                'description': 'Stage presence and performer-audience interaction'
            }
        ]
    },
    'social-leadership': {
        'name': 'Social / Leadership',
        'description': 'Teaching, facilitation, and group dynamics',
        'subcategories': [
            {
                'id': 'teaching-pedagogy',
                'name': 'Teaching & Pedagogy',
                'description': 'Educational methods and instructional design'
            },
            {
                'id': 'facilitation-community',
                'name': 'Facilitation & Community Building',
                'description': 'Group facilitation and community development'
            },
            {
                'id': 'rhetoric-diplomacy',
                'name': 'Rhetoric & Diplomacy',
                'description': 'Persuasive communication and conflict resolution'
            },
            {
                'id': 'leadership-mentoring',
                'name': 'Leadership & Mentoring',
                'description': 'Leadership development and mentorship'
            },
            {
                'id': 'group-dynamics-psychology',
                'name': 'Group Dynamics / Psychology',
                'description': 'Social psychology and group behavior'
            }
        ]
    },
    'creative-inventive': {
        'name': 'Creative / Inventive',
        'description': 'Innovation, engineering, and creative problem-solving',
        'subcategories': [
            {
                'id': 'invention-engineering',
                'name': 'Invention / Engineering',
                'description': 'Technical innovation and engineering solutions'
            },
            {
                'id': 'programming-tooling',
                'name': 'Programming / Tooling',
                'description': 'Software development and tool creation'
            },
            {
                'id': 'alchemy-metaphor-mechanism',
                'name': 'Alchemy/Metaphor, Mechanism Design',
                'description': 'Creative synthesis and system design'
            },
            {
                'id': 'prototyping-fabrication',
                'name': 'Prototyping / Fabrication',
                'description': 'Rapid prototyping and physical creation'
            },
            {
                'id': 'interaction-design',
                'name': 'Interaction Design',
                'description': 'Human-computer interaction and UX design'
            }
        ]
    },
    'research-evidence': {
        'name': 'Research & Evidence',
        'description': 'Scientific research, analysis, and evidence evaluation',
        'subcategories': [
            {
                'id': 'paper-summaries',
                'name': 'Paper Summaries, Study Discussions',
                'description': 'Research paper summaries and study analysis'
            },
            {
                'id': 'replication-critiques',
                'name': 'Replication, Critiques, and Limitations',
                'description': 'Critical analysis and replication discussions'
            },
            {
                'id': 'protocols-methods',
                'name': 'Protocols and Methods',
                'description': 'Research protocols and methodological discussions'
            },
            {
                'id': 'bibliographies-resources',
                'name': 'Bibliographies / Resource Lists',
                'description': 'Curated resource lists and bibliographies'
            }
        ]
    },
    'meta-guidelines': {
        'name': 'Meta / Guidelines',
        'description': 'Community guidelines, policies, and platform information',
        'subcategories': [
            {
                'id': 'posting-rules',
                'name': 'Posting Rules',
                'description': 'Sourcing, civility, no dogma - community standards'
            },
            {
                'id': 'tagging-conventions',
                'name': 'Tagging Conventions',
                'description': 'How to tag posts for level, format, and sourcing'
            },
            {
                'id': 'moderation-policy',
                'name': 'Moderation Policy',
                'description': 'Community moderation guidelines and processes'
            },
            {
                'id': 'contribute-improve',
                'name': 'How to Contribute / Improve Evidence Quality',
                'description': 'Guidelines for contributing quality content'
            },
            {
                'id': 'changelog-announcements',
                'name': 'Changelog / Announcements',
                'description': 'Platform updates and community announcements'
            }
        ]
    }
}


def get_all_categories() -> Dict[str, Any]:
    """Get all main categories."""
    return FORUM_CATEGORIES


def get_category(category_id: str) -> Dict[str, Any]:
    """Get a specific category by ID."""
    return FORUM_CATEGORIES.get(category_id)


def get_subcategory(category_id: str, subcategory_id: str) -> Dict[str, Any]:
    """Get a specific subcategory."""
    category = FORUM_CATEGORIES.get(category_id)
    if not category:
        return None
    
    for subcat in category.get('subcategories', []):
        if subcat['id'] == subcategory_id:
            return subcat
    
    return None


def get_all_subcategories() -> List[Dict[str, Any]]:
    """Get all subcategories flattened with parent category info."""
    subcategories = []
    for cat_id, cat_data in FORUM_CATEGORIES.items():
        for subcat in cat_data.get('subcategories', []):
            subcategories.append({
                **subcat,
                'parent_category_id': cat_id,
                'parent_category_name': cat_data['name']
            })
    return subcategories


def get_subcategories_for_category(category_id: str) -> List[Dict[str, Any]]:
    """Get all subcategories for a specific category."""
    category = FORUM_CATEGORIES.get(category_id)
    if not category:
        return []
    return category.get('subcategories', [])


def validate_tags(tags: Dict[str, str]) -> tuple[bool, str]:
    """
    Validate tag structure.
    
    Args:
        tags: Dictionary with 'level', 'format', 'sourcing' keys
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(tags, dict):
        return False, "Tags must be a dictionary"
    
    # Level tag (optional)
    if 'level' in tags:
        if tags['level'] not in TAG_LEVELS:
            return False, f"Invalid level tag. Must be one of: {', '.join(TAG_LEVELS)}"
    
    # Format tag (optional)
    if 'format' in tags:
        if tags['format'] not in TAG_FORMATS:
            return False, f"Invalid format tag. Must be one of: {', '.join(TAG_FORMATS)}"
    
    # Sourcing tag (optional)
    if 'sourcing' in tags:
        if tags['sourcing'] not in TAG_SOURCING:
            return False, f"Invalid sourcing tag. Must be one of: {', '.join(TAG_SOURCING)}"
    
    return True, ""


def get_flat_category_list() -> List[str]:
    """
    Get a flat list of all category IDs for backward compatibility.
    Returns both main categories and subcategories.
    """
    categories = []
    for cat_id in FORUM_CATEGORIES.keys():
        categories.append(cat_id)
        for subcat in FORUM_CATEGORIES[cat_id].get('subcategories', []):
            categories.append(f"{cat_id}/{subcat['id']}")
    return categories


# Legacy compatibility: flat list of topics (for mock data generation)
LEGACY_CIRCLE_TOPICS = [
    'martial-arts-combative',
    'visual',
    'internal-spiritual',
    'healing',
    'intellectual-science',
    'performance',
    'social-leadership',
    'creative-inventive',
    'research-evidence',
    'meta-guidelines'
]
