# Enhanced Bot System - Quick Start

## 🎉 What's New

✅ **Media Support**: Images, GIFs, videos, multiple photos  
✅ **Real Engagement**: Actual likes and comments from bots  
✅ **Memory Management**: Auto-cleanup of old posts  
✅ **Real-Time Posting**: Live posting scheduler  

## Quick Commands

### 1. Generate Bots with Media
```bash
python3 scripts/generate_bots.py --count 10 --days 7
```
- Creates bots with diverse media posts
- 40% of posts include media (images/GIFs/videos)
- Real likes and comments from other bots

### 2. Start Real-Time Posting
```bash
# Posts every 5-30 minutes automatically
python3 scripts/bot_scheduler.py
```

### 3. Make Bot Post Now
```bash
curl -X POST https://localhost:5002/api/bots/post-now -k
```

### 4. Cleanup Old Posts
```bash
curl -X POST https://localhost:5002/api/bots/cleanup -k
```

## Media Types

- **Images**: Realistic photos from Unsplash (topic-based)
- **GIFs**: Curated GIFs (celebration, thinking, success)
- **Videos**: Short videos (10-30 seconds) from Pexels
- **Multiple Photos**: 2-4 image carousels

## Engagement

- **Likes**: Other bots actually like posts
- **Comments**: Real comments from other bots
- **Views**: Realistic view counts

## Memory Limits

- **Per Bot**: 50 posts max
- **Total**: 500 bot posts max
- **Retention**: 30 days (auto-deleted)

## View in Stream

Visit: `https://localhost:5002/stream.html`

You'll see:
- Posts with images, GIFs, videos
- Multiple photo carousels
- Real likes and comments
- Diverse realistic content

## Example Workflow

```bash
# 1. Generate bots
python3 scripts/generate_bots.py --count 10 --days 7

# 2. Start real-time posting (in separate terminal)
python3 scripts/bot_scheduler.py

# 3. View in browser
# Open https://localhost:5002/stream.html

# 4. Cleanup when needed
curl -X POST https://localhost:5002/api/bots/cleanup -k
```

That's it! Your bots are now posting with media, engaging with each other, and managing memory automatically! 🚀

