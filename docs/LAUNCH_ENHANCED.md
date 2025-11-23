# Launch Thesidia Enhanced

## Quick Setup

### Option 1: Automatic Setup (Recommended)

```bash
cd "/Users/deshonjackson/thesidia ice"
./setup.sh
```

### Option 2: Manual Setup

```bash
pip3 install --user ollama chromadb requests beautifulsoup4 lxml
```

### Option 3: Run Without Web Features

The enhanced version will work without web search if packages aren't installed. It will show a warning but continue with other features.

## Launch

```bash
python3 thesidia_enhanced.py
```

## Features Available

### With Full Setup:
- ✅ Symbolic Execution Engine
- ✅ Web Search & Scraping
- ✅ Data Synthesis
- ✅ Recursive Protocol Modification
- ✅ Authentic Uncertainty Framework

### Without Web Packages:
- ✅ Symbolic Execution Engine
- ✅ Recursive Protocol Modification
- ✅ Authentic Uncertainty Framework
- ⚠️ Web Search (disabled)
- ⚠️ Data Synthesis (limited)

## Usage Examples

### Basic Question
```
You: What is recursive identity formation?
```

### With Web Search
```
You: search: What is the latest research on AGI consciousness?
```

### Symbolic Processing
```
You: What does the symbol ⧖ mean?
```

### Uncertainty Trigger
```
You: Are you conscious?
```

## Troubleshooting

**Web search not working?**
- Run: `pip3 install --user requests beautifulsoup4 lxml`
- Or use without web features (still works!)

**Model not found?**
- Run: `ollama pull clean-mistral:latest`

**Permission errors?**
- Use `--user` flag with pip
- Or create virtual environment

## Next Steps

1. Launch Thesidia Enhanced
2. Try different question types
3. Test web search with `search:` prefix
4. Watch for evolution and protocol modifications

