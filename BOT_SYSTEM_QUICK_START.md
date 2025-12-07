# Bot System - Quick Start Guide

## What This Does

Creates realistic bot profiles that:
- Generate synthetic but believable content
- Post at realistic intervals
- Have natural engagement patterns
- Appear as real users
- Use minimal resources (cached templates, simple web scraping)

## Quick Test

### 1. Generate 10 Bots with Activity

```bash
cd "/Users/deshonjackson/thesidia ice"
python3 scripts/generate_bots.py --count 10
```

This will:
- Create 10 bot profiles
- Generate 30 days of activity for each
- Build network connections between bots
- Use cached templates (minimal resource)

### 2. View Bots in Stream

Visit: `https://localhost:5002/stream.html`

You'll see:
- Bot posts with realistic content
- Natural engagement metrics
- Diverse posting patterns

### 3. Generate More Activity

```bash
# Generate activity for specific bot
python3 scripts/generate_bots.py --count 1 --days 7
```

## How It Works

### Content Synthesis

**Templates** (cached in `data/bot_cache/`):
- Observation templates: "Just noticed {topic} is more complex..."
- Question templates: "What do you think about {topic}?"
- Sharing templates: "Found this interesting: {topic}"
- Personal templates: "Working on {topic} today"

**Web Scraping** (intelligent, cached):
- Scrapes DuckDuckGo for topic ideas
- Caches results for 24 hours
- Minimal parsing (just titles)
- Fallback to generated ideas

**Variation**:
- Random emojis (30% chance)
- Hashtags (20% chance)
- Variable length
- Topic-based content

### Bot Profiles

**Generated Data**:
- Realistic names (diverse, international)
- Bios (varied interests)
- Account ages (7-365 days)
- Avatars (DiceBear API)
- Personality types (active/moderate/casual)

### Activity Patterns

**Posting Frequency**:
- Active: 2-5 posts/day
- Moderate: 0.5-2 posts/day
- Casual: 0.1-1 posts/day

**Engagement**:
- Views: 10-500 per post
- Like rate: 2-10% of views
- Comment rate: 10-30% of likes
- Repost rate: 5-15% of likes
- Engagement delay: 1-48 hours

## API Usage

### Generate Bots

```bash
curl -X POST http://localhost:5002/api/bots/generate \
  -H "Content-Type: application/json" \
  -d '{
    "count": 20,
    "bot_types": ["active", "moderate"],
    "generate_activity": true,
    "days_of_activity": 30
  }'
```

### List Bots

```bash
curl http://localhost:5002/api/bots/list
```

## Resource Optimization

- **Caching**: All templates, topics, scraped content cached
- **Simple Scraping**: Only extracts titles, not full content
- **Template-Based**: No LLM calls for content generation
- **Batch Processing**: Small delays to avoid overwhelming system

## Advanced: Enhance with Thesidia

You can enhance bot content by using Thesidia's synthesis:

```python
# In bot_generator.py, enhance synthesize_post():
if use_thesidia:
    # Use Thesidia to generate more sophisticated content
    content = thesidia.synthesize(topic, bot_profile)
else:
    # Use template-based generation (faster, minimal resource)
    content = template_synthesizer.synthesize_post(bot_profile)
```

## Detection Avoidance

The system avoids detection by:
- ✅ Variable posting times
- ✅ Diverse content
- ✅ Natural engagement patterns
- ✅ Realistic account ages
- ✅ Varied network connections
- ✅ Not all posts get engagement

## Example Output

```
🤖 Generating 10 bots...
   Types: active, moderate, casual
   Activity: Yes (30 days)
   Network: Yes

✅ Bot Generation Complete!
📊 Summary:
   - 10 bots created
   - 15 network connections
```

## Next Steps

1. **Test the system**: Run `python3 scripts/generate_bots.py --count 10`
2. **View in stream**: Check `/stream.html` to see bot activity
3. **Customize**: Edit templates in `data/bot_cache/templates.json`
4. **Enhance**: Add Thesidia synthesis for more sophisticated content

