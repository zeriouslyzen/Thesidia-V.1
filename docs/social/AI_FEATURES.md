# AI-First Features Documentation

## Overview

Thesidia's social media platform is built with AI at its core. Every post is analyzed, scored, and curated using Thesidia's AI capabilities for quality, relevance, and user experience.

## AI Components

### 1. AI Quality Scorer (`ai_quality_scorer.py`)

**Purpose**: Multi-factor quality scoring for posts using Thesidia AI

**Features**:
- **Spam Detection**: AI-powered spam detection using Thesidia
- **Content Uniqueness**: Analyzes content for originality and repetition
- **Sentiment Analysis**: Detects emotional tone and balance
- **Content Length Scoring**: Optimal length analysis (100-500 chars)
- **Engagement Quality**: Calculates engagement ratios
- **User Reputation**: Tracks author reputation over time

**Integration**: Uses `ThesidiaHybridAdaptive` for deep content analysis

**Usage**:
```python
from webapp.social.ai_quality_scorer import AIQualityScorer

scorer = AIQualityScorer(base_dir=base_dir, thesidia=thesidia_instance)
quality_score = scorer.calculate_quality_score(post, author_data)
```

### 2. AI Content Insights (`ai_content_insights.py`)

**Purpose**: Generate AI-powered insights about posts

**Features**:
- **Summaries**: Generate concise summaries of posts
- **Key Points**: Extract main points from content
- **Sentiment Detection**: Analyze emotional tone
- **Related Topics**: Suggest related hashtags and topics

**API Endpoints**:
- Automatically added to posts via `/api/posts` GET endpoint
- `/api/posts/suggest-hashtags` - Get hashtag suggestions for content

**Usage**:
```python
from webapp.social.ai_content_insights import AIContentInsights

insights = AIContentInsights(base_dir=base_dir, thesidia=thesidia_instance)
summary = insights.generate_summary(post, max_length=150)
key_points = insights.generate_key_points(post)
sentiment = insights.detect_sentiment(post)
topics = insights.suggest_related_topics(post)
```

### 3. AI Recommendations (`ai_recommendations.py`)

**Purpose**: Generate personalized content recommendations

**Features**:
- **Post Recommendations**: Suggest posts based on user interests
- **Content Topic Suggestions**: Suggest topics for users to post about
- **Interest-Based Filtering**: Uses UserInterestTracker for personalization

**API Endpoints**:
- `/api/recommendations` - Get personalized recommendations

**Usage**:
```python
from webapp.social.ai_recommendations import AIRecommendations

recommender = AIRecommendations(base_dir=base_dir, thesidia=thesidia_instance)
recommended_posts = recommender.recommend_posts(user_id, limit=10)
suggested_topics = recommender.suggest_content_topics(user_id)
```

### 4. Enhanced Bot Detection (`bot_detector.py`)

**Purpose**: Detect bots using multi-signal analysis + AI

**Features**:
- **Behavioral Analysis**: Post frequency, engagement patterns
- **Content Analysis**: Repetitive content detection
- **Network Analysis**: Follower/following ratio anomalies
- **AI Analysis**: Deep analysis using Thesidia AI

**Integration**: Uses `ThesidiaHybridAdaptive` for AI-powered bot detection

**Usage**:
```python
from webapp.social.bot_detector import BotDetector

detector = BotDetector(base_dir=base_dir, thesidia=thesidia_instance)
bot_probability, signals = detector.detect_bot(user_id)
```

## AI Integration Points

### Post Creation
- Automatic hashtag extraction from content
- Mention extraction (@username)
- AI quality scoring on creation
- AI moderation check
- Interest tracking for personalized feeds

### Feed Generation
- AI quality scores used in ranking (40% weight)
- User relevance calculated from interests (30% weight)
- Recency with exponential decay (20% weight)
- Diversity factor (10% weight)

### User Interactions
- Likes trigger interest tracking
- Comments analyzed for sentiment
- Reposts tracked for content discovery
- Views used for engagement quality scoring

## Frontend AI Features

### Quality Badges
- Visual indicators showing AI quality scores
- Color-coded: Green (high), Yellow (medium), Red (low)
- Displayed on each post in the feed

### AI Summaries
- Automatically generated summaries displayed below post content
- Helps users quickly scan feed

### Sentiment Indicators
- Visual tags showing post sentiment
- Positive (green), Negative (red), Neutral (gray)

### AI Suggestions Panel
- Displays AI-generated content topic suggestions
- Clickable suggestions populate the compose textarea
- Based on user's tracked interests

### Hashtag Autocomplete
- Real-time hashtag suggestions as user types
- AI-powered based on post content
- Dropdown with clickable suggestions

## Interest Tracking

The platform automatically tracks user interests from:
- Posts they create
- Posts they like
- Posts they comment on
- Posts they repost

Interests are used for:
- Personalized feed ranking
- Content recommendations
- Topic suggestions
- Feed filtering

## API Endpoints

### AI Features
- `GET /api/recommendations` - Get AI-powered recommendations
- `POST /api/posts/suggest-hashtags` - Get hashtag suggestions

### Standard Endpoints (with AI enhancements)
- `GET /api/posts` - Returns posts with AI insights (summary, sentiment)
- `GET /api/feed` - Returns feed with AI-ranked posts
- `POST /api/posts` - Creates post with AI quality scoring

## Configuration

AI features are automatically enabled when:
- Thesidia is available (`thesidia_ready = True`)
- Ollama is running
- `ThesidiaHybridAdaptive` can be initialized

If AI is unavailable, features fall back to heuristic-based methods.

## Performance

- AI analysis is performed asynchronously where possible
- Quality scores are cached with posts
- Feed ranking uses cached scores
- Recommendations are generated on-demand with caching

## Future Enhancements

1. **Real-time AI Analysis**: WebSocket-based live AI insights
2. **Advanced Embeddings**: Use vector embeddings for better similarity
3. **Multi-Model Ensemble**: Combine multiple AI models for better accuracy
4. **User Preference Learning**: Learn from user feedback on recommendations
5. **Content Generation**: AI-assisted post writing

