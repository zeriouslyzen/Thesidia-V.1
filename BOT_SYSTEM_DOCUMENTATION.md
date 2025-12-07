# Intelligent Bot System - Documentation

## Overview

A minimal-resource bot generation system that creates realistic social media activity by:
1. **Synthesizing content** from templates and patterns
2. **Web scraping** for topic ideas (cached, minimal resource)
3. **Generating realistic profiles** with diverse personalities
4. **Creating natural activity patterns** (posting frequency, engagement)
5. **Building social networks** between bots

## How It Works

### 1. Content Synthesis (Minimal Resource)

**Templates System**:
- Cached templates in `data/bot_cache/templates.json`
- Multiple template types: observations, questions, sharing, personal
- Topic-based content generation
- Realistic variation (emojis, hashtags, length)

**Web Scraping** (Intelligent, Cached):
- Scrapes DuckDuckGo HTML search (no API key needed)
- Caches results for 24 hours
- Extracts titles/headlines for topic ideas
- Minimal parsing (just titles, not full content)
- Fallback to generated ideas if scraping fails

**Example Synthesis**:
```
Template: "Just noticed {topic} is more complex than I thought"
Topic: "AI research"
Result: "Just noticed AI research is more complex than I thought 🤔"
```

### 2. Bot Profile Generation

**Realistic Profiles**:
- Diverse names (gender-neutral, international)
- Realistic bios (varied interests)
- Account ages (7-365 days old)
- Avatar URLs (DiceBear API - free)
- Personality types: active, moderate, casual

**Profile Data** (Cached):
- Names, bios, interests cached in `data/bots/profile_data.json`
- Can be updated/scraped for more diversity

### 3. Activity Generation

**Realistic Patterns**:
- **Posting Frequency**: Varies by bot type
  - Active: 2-5 posts/day
  - Moderate: 0.5-2 posts/day
  - Casual: 0.1-1 posts/day
- **Timing**: Distributed throughout day (6am-11pm)
- **Engagement**: Realistic rates
  - Views: 10-500 per post
  - Like rate: 2-10% of views
  - Comment rate: 10-30% of likes
  - Repost rate: 5-15% of likes
- **Engagement Delay**: 1-48 hours after post (realistic)

### 4. Anti-Detection Features

**Variability**:
- Random posting times
- Variable content length
- Diverse engagement rates
- Natural network connections
- Account age variation

**Realistic Behavior**:
- Not all posts get engagement (30% don't)
- Engagement happens over time (not instant)
- Natural follower/following ratios
- Varied content types

## Usage

### Command Line

```bash
# Generate 10 bots with activity
python scripts/generate_bots.py --count 10

# Generate only active bots
python scripts/generate_bots.py --count 20 --types active

# Generate bots without activity
python scripts/generate_bots.py --count 5 --no-activity

# Generate 30 days of activity
python scripts/generate_bots.py --count 10 --days 30
```

### API Endpoint

```bash
# Generate bots via API
curl -X POST http://localhost:5002/api/bots/generate \
  -H "Content-Type: application/json" \
  -d '{
    "count": 10,
    "bot_types": ["active", "moderate"],
    "generate_activity": true,
    "days_of_activity": 30
  }'

# List all bots
curl http://localhost:5002/api/bots/list

# Generate activity for specific bot
curl -X POST http://localhost:5002/api/bots/generate-activity \
  -H "Content-Type: application/json" \
  -d '{
    "bot_id": "bot_abc123",
    "days": 7,
    "posts_per_day_min": 1,
    "posts_per_day_max": 3
  }'
```

## Resource Optimization

### Caching Strategy

1. **Templates**: Cached in `data/bot_cache/templates.json`
2. **Topics**: Cached in `data/bot_cache/topics.json`
3. **Scraped Content**: Cached per topic for 24 hours
4. **Profile Data**: Cached in `data/bots/profile_data.json`
5. **Patterns**: Cached in `data/bot_cache/patterns.json`

### Minimal Resource Usage

- **No Heavy Parsing**: Only extracts titles, not full content
- **Batch Processing**: Small delays between operations
- **Cached Results**: Reuses scraped data for 24 hours
- **Template-Based**: No LLM calls for content generation
- **Simple Requests**: Lightweight HTTP requests

## How Social Media Platforms Do This

### Industry Patterns

1. **Content Farms**: Generate content from templates + web scraping
2. **Synthetic Profiles**: Use name generators, avatar APIs
3. **Behavioral Patterns**: Model real user activity patterns
4. **Network Building**: Connect bots to each other and real users
5. **Engagement Simulation**: Generate realistic engagement metrics

### Our Implementation

✅ **Content Synthesis**: Templates + topic variation  
✅ **Web Scraping**: DuckDuckGo HTML (no API key)  
✅ **Profile Generation**: Realistic names, bios, avatars  
✅ **Activity Patterns**: Variable posting, realistic timing  
✅ **Engagement Simulation**: Natural engagement rates  
✅ **Network Building**: Bot-to-bot connections  
✅ **Minimal Resources**: Caching, templates, simple scraping  

## Advanced Features (Future)

1. **LLM-Enhanced Content**: Use Thesidia to generate more sophisticated posts
2. **Trend Following**: Scrape trending topics and generate related content
3. **Image Generation**: Generate/synthesize images for posts
4. **Comment Generation**: Generate realistic comments on posts
5. **Interaction Patterns**: More sophisticated engagement patterns
6. **Time Zone Awareness**: Post at appropriate times for bot's "location"

## Detection Avoidance

The system is designed to avoid bot detection by:

1. **Variability**: Random timing, content, engagement
2. **Realistic Patterns**: Mimics human behavior
3. **Account Age**: Bots have varied account ages
4. **Natural Networks**: Realistic follower/following ratios
5. **Content Diversity**: Varied topics, lengths, styles
6. **Engagement Timing**: Engagement happens over time, not instantly

## Files

- `webapp/social/bot_generator.py` - Main bot generation system
- `scripts/generate_bots.py` - CLI tool for bot generation
- `data/bot_cache/` - Cached templates, topics, scraped content
- `data/bots/` - Bot profiles

## Example Output

```json
{
  "bots_created": 10,
  "bots": [
    {
      "bot_id": "bot_abc123",
      "username": "alexchen456",
      "display_name": "Alex Chen",
      "bot_type": "active"
    }
  ],
  "network_connections": 15
}
```

## Performance

- **Generation Speed**: ~0.2 seconds per bot
- **Activity Generation**: ~0.1 seconds per post
- **Resource Usage**: Minimal (cached data, simple requests)
- **Scalability**: Can generate hundreds of bots efficiently

