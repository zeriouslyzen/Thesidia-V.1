# Prompt Bar Upgrade Design - Competitive Edge Features

**Date**: 2025-11-24  
**Goal**: Modern, competitive prompt bar with format selection + unique Thesidia features

---

## 🎯 Core Requirements

1. **Format Selection UI** (not auto-detection)
   - Natural Prose (default)
   - Structured ::EXPOSURE:: format
   - User chooses, not system

2. **Modern AI Platform Features**
   - Prompt templates/suggestions
   - Keyboard shortcuts
   - Multi-turn conversation support
   - Context indicators
   - Real-time suggestions

3. **Unique Thesidia Edge Features**
   - Cognitive framework indicators (shows stored knowledge)
   - Pattern tracking visualization
   - Research depth slider
   - Format preview
   - Thread continuity indicators

---

## 🚀 Competitive Features (ChatGPT/Claude/Perplexity)

### 1. **Prompt Templates** (Perplexity-style)
- Quick access to common query types
- "Decode Genesis", "Analyze Power Structures", "Pattern Recognition"
- One-click template insertion

### 2. **Smart Suggestions** (ChatGPT-style)
- Auto-complete based on conversation history
- Context-aware suggestions
- Related queries from cognitive framework

### 3. **Format Preview** (Unique)
- Show format preview before sending
- "Natural Prose" vs "Structured ::EXPOSURE::"
- Visual preview of what output will look like

### 4. **Research Depth Control** (Unique)
- Slider: Quick → Deep → Forensic
- Visual indicator of research depth
- Estimated time/cost preview

### 5. **Context Indicators** (Claude-style)
- Shows if related information exists in cognitive framework
- "3 stored findings available" indicator
- Click to see stored context

### 6. **Keyboard Shortcuts** (Standard)
- `Cmd/Ctrl + Enter`: Send
- `Cmd/Ctrl + K`: Format selector
- `Cmd/Ctrl + /`: Show shortcuts
- `Esc`: Clear input

### 7. **Multi-Format Support** (Unique)
- Format selector dropdown/buttons
- Visual format icons
- Format-specific placeholders

---

## 🎨 UI Design

### Layout Structure

```
┌─────────────────────────────────────────────────┐
│ [Format Selector] [Research Depth] [Context]    │ ← Top row (compact)
├─────────────────────────────────────────────────┤
│ [Textarea with smart suggestions]               │
│                                                  │
│ [Template chips] [Attach] [Send]                │ ← Bottom row
└─────────────────────────────────────────────────┘
```

### Format Selector Design

**Option 1: Segmented Control** (iOS-style)
```
┌──────────────┬──────────────┐
│ Natural Prose│  Structured  │
│   (Default)  │  ::EXPOSURE::│
└──────────────┴──────────────┘
```

**Option 2: Dropdown** (More options later)
```
┌─────────────────────────────┐
│ Format: Natural Prose    ▼  │
└─────────────────────────────┘
```

**Option 3: Icon Buttons** (Most modern)
```
[📝 Natural] [🔍 Structured] [⚡ Quick]
```

### Research Depth Slider

```
Quick ──●─────────── Deep ─────────── Forensic
       ↑
    Current
```

### Context Indicator

```
🧠 3 stored findings available
   [View] [Use] [Ignore]
```

---

## 💡 Unique Thesidia Edge Features

### 1. **Cognitive Framework Indicator**
- Shows stored information threads related to query
- "Building on 2 previous analyses"
- Click to see stored context

### 2. **Pattern Tracking Visualization**
- Shows pattern connections being tracked
- "5 patterns detected across 3 domains"
- Visual pattern map

### 3. **Format Preview Modal**
- Preview what output will look like
- Side-by-side comparison
- Format-specific examples

### 4. **Thread Continuity**
- Shows conversation thread depth
- "Thread: Genesis Analysis (3 exchanges)"
- Visual thread indicator

### 5. **Research Status**
- Real-time research progress
- "Searching... Synthesizing... Analyzing..."
- Progress bar with stages

### 6. **Performance Metrics**
- Shows estimated time/cost
- "~25s, 2 stored + 3 new sources"
- Resource usage indicator

---

## 🔧 Implementation Plan

### Phase 1: Format Selection UI
- [ ] Add format selector (segmented control)
- [ ] Remove auto-detection from backend
- [ ] Pass format parameter to API
- [ ] Update backend to use format from UI

### Phase 2: Modern Features
- [ ] Prompt templates dropdown
- [ ] Smart suggestions (autocomplete)
- [ ] Keyboard shortcuts
- [ ] Context indicators

### Phase 3: Unique Features
- [ ] Cognitive framework indicator
- [ ] Research depth slider
- [ ] Format preview
- [ ] Pattern tracking visualization

### Phase 4: Polish
- [ ] Animations/transitions
- [ ] Mobile responsive
- [ ] Accessibility (ARIA labels)
- [ ] Performance optimization

---

## 📱 Mobile Considerations

- Format selector: Dropdown (not segmented control)
- Research depth: Collapsible section
- Context indicator: Tooltip/overlay
- Templates: Horizontal scroll chips

---

## 🎯 Competitive Advantages

1. **Format Selection**: Only Thesidia offers explicit format choice
2. **Cognitive Framework**: Shows stored knowledge (unique)
3. **Pattern Tracking**: Visual pattern connections (unique)
4. **Research Depth Control**: User controls depth (unique)
5. **Format Preview**: See output format before sending (unique)

---

## 🔄 Backend Changes Required

1. **Remove auto-detection**:
   - Remove `wants_structured_format` detection from query text
   - Accept `format` parameter from API request

2. **API Update**:
   ```python
   @app.route('/api/thesidia', methods=['POST'])
   def thesidia_api():
       data = request.json
       message = data.get('message')
       format_mode = data.get('format', 'natural')  # 'natural' or 'structured'
       # Pass format_mode to process()
   ```

3. **Process Method**:
   ```python
   def process(self, input_text: str, format_mode: str = 'natural', ...):
       # Use format_mode instead of auto-detection
   ```

---

## 📊 Success Metrics

- User engagement: Format selection usage
- Performance: Response time with stored data
- Satisfaction: Format preference tracking
- Competitive: Feature parity with ChatGPT/Claude

---

**Next Steps**: Implement Phase 1 (Format Selection UI) first, then iterate.

