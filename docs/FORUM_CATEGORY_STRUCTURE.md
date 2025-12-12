# Forum Category Structure Documentation

## Overview

The forum uses a hierarchical category system with main categories, subcategories, and a comprehensive tagging system for content organization and discovery.

## Category Hierarchy

### Main Categories

Each main category contains 3-6 subcategories, following the principle of lean organization and single ownership per topic.

#### 1. Martial Arts & Combative
**Description**: Combat systems, movement arts, and training methodologies

**Subcategories**:
- **Combatives**: Striking, grappling, weapons training
- **Internal Arts**: Taiji/Bagua/Xingyi, Qigong/Neigong
- **Movement Arts**: Dance, parkour, acrobatics, gymnastics, capoeira, flow arts
- **Conditioning & Biomechanics**: Physical preparation and movement science
- **Coaching / Pedagogy**: Teaching methods and instructional design

#### 2. Visual
**Description**: Visual arts, design, and creative expression

**Subcategories**:
- **Drawing/Painting/Sculpture**: Traditional visual arts
- **Design**: Graphic, UX/UI, product design
- **Photo/Film/Animation**: Moving images and photography
- **Architecture**: Built environment and spatial design
- **Crafts/Making**: Jewelry, engraving, fabrication

#### 3. Internal / Spiritual
**Description**: Contemplative practices and inner work

**Subcategories**:
- **Meditation & Contemplative Practice**: Mindfulness, concentration, contemplative traditions
- **Breathwork / Pranayama**: Breathing practices and techniques
- **Ritual/Indigenous/Mystical Arts**: Traditional and ceremonial practices (with sourcing respect)
- **Energy Practices**: Qigong internal, energy work, subtle body practices
- **Ethics & Safeguarding**: Ethical frameworks and safety in practice

#### 4. Healing
**Description**: Therapeutic approaches and recovery systems

**Subcategories**:
- **Clinical & Evidence-Based**: PT, sports med, rehab, evidence-based approaches
- **Traditional Systems**: TCM, acupuncture, herbalism, traditional medicine
- **Bodywork & Manual Therapies**: Hands-on healing and therapeutic touch
- **Recovery & Longevity**: Recovery protocols and longevity practices
- **Safety / Contraindications**: Safety protocols and contraindication awareness

#### 5. Intellectual / Science
**Description**: Academic inquiry and scientific understanding

**Subcategories**:
- **Philosophy & Epistemology**: Philosophical inquiry and knowledge theory
- **Neuroscience / Cognition**: Brain science and cognitive processes
- **Physiology / Biomechanics**: Body systems and movement mechanics
- **Data, Modeling, and Systems Thinking**: Quantitative analysis and systems approaches
- **Methodology & Study Design**: Research methods and experimental design

#### 6. Performance
**Description**: Performance arts and stagecraft

**Subcategories**:
- **Music & Voice**: Musical performance and vocal arts
- **Theater / Spoken Word / Storytelling**: Dramatic arts and narrative performance
- **Performance Movement**: Wushu performance, stage martial, dance performance
- **Stagecraft / Production**: Technical production and stage management
- **Presence & Audience Dynamics**: Stage presence and performer-audience interaction

#### 7. Social / Leadership
**Description**: Teaching, facilitation, and group dynamics

**Subcategories**:
- **Teaching & Pedagogy**: Educational methods and instructional design
- **Facilitation & Community Building**: Group facilitation and community development
- **Rhetoric & Diplomacy**: Persuasive communication and conflict resolution
- **Leadership & Mentoring**: Leadership development and mentorship
- **Group Dynamics / Psychology**: Social psychology and group behavior

#### 8. Creative / Inventive
**Description**: Innovation, engineering, and creative problem-solving

**Subcategories**:
- **Invention / Engineering**: Technical innovation and engineering solutions
- **Programming / Tooling**: Software development and tool creation
- **Alchemy/Metaphor, Mechanism Design**: Creative synthesis and system design
- **Prototyping / Fabrication**: Rapid prototyping and physical creation
- **Interaction Design**: Human-computer interaction and UX design

#### 9. Research & Evidence
**Description**: Scientific research, analysis, and evidence evaluation

**Subcategories**:
- **Paper Summaries, Study Discussions**: Research paper summaries and study analysis
- **Replication, Critiques, and Limitations**: Critical analysis and replication discussions
- **Protocols and Methods**: Research protocols and methodological discussions
- **Bibliographies / Resource Lists**: Curated resource lists and bibliographies

#### 10. Meta / Guidelines
**Description**: Community guidelines, policies, and platform information

**Subcategories**:
- **Posting Rules**: Sourcing, civility, no dogma - community standards
- **Tagging Conventions**: How to tag posts for level, format, and sourcing
- **Moderation Policy**: Community moderation guidelines and processes
- **How to Contribute / Improve Evidence Quality**: Guidelines for contributing quality content
- **Changelog / Announcements**: Platform updates and community announcements

## Tagging System

### Tag Types

#### Level Tags
Indicates the skill/knowledge level required:
- `beginner`: Entry-level content, suitable for newcomers
- `intermediate`: Requires some background knowledge
- `advanced`: Requires significant expertise or experience

#### Format Tags
Indicates the type of content:
- `guide`: Instructional or how-to content
- `question`: Questions seeking answers or discussion
- `study`: Research summaries or study analysis
- `critique`: Critical analysis or review
- `discussion`: Open-ended discussion threads
- `resource`: Curated resources, links, or references

#### Sourcing Tags
Indicates the type of evidence or source:
- `peer-reviewed`: Academic or peer-reviewed sources
- `clinical`: Clinical evidence or professional practice
- `traditional`: Traditional knowledge or practices
- `anecdotal`: Personal experience or anecdotal evidence
- `mixed`: Combination of multiple source types

### Tag Usage Guidelines

1. **Single Ownership**: Each thread should belong to one primary category/subcategory
2. **Tag Appropriately**: Use tags that accurately reflect content level, format, and sourcing
3. **Be Specific**: Choose the most specific subcategory that fits
4. **Avoid Cross-Posting**: Don't duplicate threads across categories

## API Structure

### Category Data Format

```json
{
  "category_id": {
    "name": "Category Name",
    "description": "Category description",
    "subcategories": [
      {
        "id": "subcategory-id",
        "name": "Subcategory Name",
        "description": "Subcategory description"
      }
    ]
  }
}
```

### Thread Data Format

```json
{
  "id": "thread_id",
  "title": "Thread Title",
  "body": "Thread content",
  "circle": "category-id/subcategory-id",
  "category_id": "category-id",
  "subcategory_id": "subcategory-id",
  "category_name": "Category Name",
  "subcategory_name": "Subcategory Name",
  "tags": ["category-id/subcategory-id", "level:beginner", "format:guide"],
  "tag_metadata": {
    "level": "beginner",
    "format": "guide",
    "sourcing": "peer-reviewed"
  }
}
```

## API Endpoints

### GET `/api/categories`
Returns the full category structure and tag options.

**Response**:
```json
{
  "categories": { /* category structure */ },
  "tag_options": {
    "levels": ["beginner", "intermediate", "advanced"],
    "formats": ["guide", "question", "study", "critique", "discussion", "resource"],
    "sourcing": ["peer-reviewed", "clinical", "traditional", "anecdotal", "mixed"]
  }
}
```

### GET `/api/sections/circles`
Returns threads and categories (includes both main categories and subcategories).

**Response**:
```json
{
  "threads": [ /* thread objects */ ],
  "categories": [
    {
      "id": "category-id",
      "name": "Category Name",
      "type": "category",
      "has_subcategories": true,
      "thread_count": 10
    },
    {
      "id": "category-id/subcategory-id",
      "name": "Subcategory Name",
      "type": "subcategory",
      "parent_category_id": "category-id",
      "parent_category_name": "Category Name",
      "thread_count": 5
    }
  ]
}
```

## Implementation Files

- **Category Definition**: `data/mock/forum_categories.py`
- **Mock Data Generator**: `data/mock/mock_circles.py`
- **API Endpoints**: `webapp/server.py`

## Best Practices

1. **Category Selection**: Choose the most specific subcategory that fits your content
2. **Tagging**: Always include at least one format tag and sourcing tag when applicable
3. **Level Tags**: Use level tags to help users find appropriate content
4. **Single Ownership**: Avoid cross-posting; choose one primary category
5. **Descriptions**: Use clear, descriptive titles and bodies that reflect the category

## Future Enhancements

- Category-specific moderation rules
- Category subscription/following
- Category-specific UI themes
- Category analytics and trending
- Dynamic category creation (admin only)
- Category merging and reorganization tools
