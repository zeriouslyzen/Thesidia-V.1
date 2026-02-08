# Forensic Output: Design System

## Visual Language

### Section Markers

**Old format:** `::UPPERCASE::`  
**New format:** `//lowercase`

```
//exposure
//etymological incision
//burial sites
//current vectors
//co-evolution edge
//thread options
```

**Styling:**
- Font: Monospace (JetBrains Mono or similar)
- Color: Gradient from `#8B5CF6` (purple) to `#EC4899` (pink)
- Size: 14px
- Weight: 600
- Margin: 24px top, 8px bottom
- Border-left: 3px solid gradient

---

## Color System

### Semantic Colors

```css
/* Patterns - Purple gradient */
.pattern {
  background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 600;
}

/* Entities - Cyan */
.entity {
  color: #06B6D4;
  font-weight: 500;
}

/* Key insights - Gold */
.insight {
  color: #F59E0B;
  font-weight: 600;
}

/* Suppressed knowledge - Red */
.suppressed {
  color: #EF4444;
  font-style: italic;
}

/* Citations - Gray */
.citation {
  color: #9CA3AF;
  font-size: 0.9em;
}

/* Modern vectors - Green */
.modern {
  color: #10B981;
}
```

### Example Usage

```html
<p>
  The <span class="pattern">centralization of authority</span> 
  through manipulation of <span class="entity">Asherah</span> 
  worship reveals a <span class="insight">universal mechanism</span> 
  for <span class="suppressed">suppressing feminine archetypes</span>.
</p>
```

---

## Custom SVG Icons

### Thread Option Icons

**Re-enter (Arrow Cycle)**
```svg
<svg width="20" height="20" viewBox="0 0 20 20" fill="none">
  <path d="M4 10C4 6.68629 6.68629 4 10 4C13.3137 4 16 6.68629 16 10" 
        stroke="url(#gradient1)" stroke-width="2" stroke-linecap="round"/>
  <path d="M13 7L16 10L13 13" 
        stroke="url(#gradient1)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <defs>
    <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#8B5CF6"/>
      <stop offset="100%" stop-color="#EC4899"/>
    </linearGradient>
  </defs>
</svg>
```

**Trace (Map/Compass)**
```svg
<svg width="20" height="20" viewBox="0 0 20 20" fill="none">
  <circle cx="10" cy="10" r="7" stroke="url(#gradient2)" stroke-width="2"/>
  <path d="M10 3V10L14 14" stroke="url(#gradient2)" stroke-width="2" stroke-linecap="round"/>
  <circle cx="10" cy="10" r="2" fill="url(#gradient2)"/>
  <defs>
    <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#06B6D4"/>
      <stop offset="100%" stop-color="#3B82F6"/>
    </linearGradient>
  </defs>
</svg>
```

**Cold-read (Lens/Eye)**
```svg
<svg width="20" height="20" viewBox="0 0 20 20" fill="none">
  <path d="M2 10C2 10 5 4 10 4C15 4 18 10 18 10C18 10 15 16 10 16C5 16 2 10 2 10Z" 
        stroke="url(#gradient3)" stroke-width="2"/>
  <circle cx="10" cy="10" r="3" stroke="url(#gradient3)" stroke-width="2"/>
  <defs>
    <linearGradient id="gradient3" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#F59E0B"/>
      <stop offset="100%" stop-color="#EF4444"/>
    </linearGradient>
  </defs>
</svg>
```

---

## Thread Option Cards

### Design Specs

```css
.thread-card {
  /* Layout */
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  margin: 8px 0;
  
  /* Background */
  background: linear-gradient(135deg, 
    rgba(139, 92, 246, 0.05) 0%, 
    rgba(236, 72, 153, 0.05) 100%);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 12px;
  
  /* Interaction */
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.thread-card:hover {
  background: linear-gradient(135deg, 
    rgba(139, 92, 246, 0.1) 0%, 
    rgba(236, 72, 153, 0.1) 100%);
  border-color: rgba(139, 92, 246, 0.4);
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.15);
}

.thread-card:active {
  transform: translateX(2px);
}

.thread-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
}

.thread-label {
  flex: 1;
  font-size: 15px;
  font-weight: 500;
  color: #E5E7EB;
}

.thread-arrow {
  flex-shrink: 0;
  width: 16px;
  height: 16px;
  opacity: 0.5;
  transition: opacity 0.3s, transform 0.3s;
}

.thread-card:hover .thread-arrow {
  opacity: 1;
  transform: translateX(4px);
}
```

### HTML Structure

```html
<div class="thread-options">
  <div class="section-header">//thread options</div>
  
  <div class="thread-card" data-type="re-enter" data-query="...">
    <svg class="thread-icon"><!-- Re-enter icon --></svg>
    <span class="thread-label">Re-enter the exposure about divine feminine suppression</span>
    <svg class="thread-arrow"><!-- Arrow icon --></svg>
  </div>
  
  <div class="thread-card" data-type="trace" data-query="...">
    <svg class="thread-icon"><!-- Trace icon --></svg>
    <span class="thread-label">Trace burial sites of Asherah temple locations</span>
    <svg class="thread-arrow"><!-- Arrow icon --></svg>
  </div>
  
  <div class="thread-card" data-type="cold-read" data-query="...">
    <svg class="thread-icon"><!-- Cold-read icon --></svg>
    <span class="thread-label">Cold-read modern banking mechanisms against this pattern</span>
    <svg class="thread-arrow"><!-- Arrow icon --></svg>
  </div>
</div>
```

---

## Section Styling

### Exposure Section

```css
.section-exposure {
  position: relative;
  padding: 24px;
  margin: 16px 0;
  
  /* Gradient border */
  background: 
    linear-gradient(#0F172A, #0F172A) padding-box,
    linear-gradient(135deg, #8B5CF6, #EC4899) border-box;
  border: 2px solid transparent;
  border-radius: 16px;
  
  /* Subtle glow */
  box-shadow: 
    0 0 20px rgba(139, 92, 246, 0.1),
    inset 0 0 40px rgba(139, 92, 246, 0.02);
}

.section-exposure::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(139, 92, 246, 0.5) 50%, 
    transparent 100%);
}
```

### Pattern Highlights

```css
/* Auto-highlight patterns in text */
.forensic-output p {
  line-height: 1.8;
  color: #E5E7EB;
}

/* Highlight pattern keywords */
.forensic-output p:has(.pattern) {
  position: relative;
  padding-left: 12px;
}

.forensic-output p:has(.pattern)::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, #8B5CF6, #EC4899);
  border-radius: 2px;
}
```

---

## Confidence Meter Redesign

### Old Format
```
**Epistemological Grounding:** ████░░░ 0/7 layers aligned (LOW)
```

### New Format

```html
<div class="confidence-meter">
  <div class="meter-header">
    <span class="meter-label">Epistemological Grounding</span>
    <span class="meter-score">4/7 layers</span>
  </div>
  
  <div class="meter-bar">
    <div class="meter-fill" style="width: 57%"></div>
  </div>
  
  <div class="meter-status high">High Confidence</div>
</div>
```

```css
.confidence-meter {
  margin: 24px 0;
  padding: 20px;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 12px;
}

.meter-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.meter-label {
  font-size: 13px;
  font-weight: 600;
  color: #9CA3AF;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.meter-score {
  font-size: 14px;
  font-weight: 600;
  color: #E5E7EB;
}

.meter-bar {
  height: 8px;
  background: rgba(139, 92, 246, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.meter-fill {
  height: 100%;
  background: linear-gradient(90deg, #8B5CF6, #EC4899);
  border-radius: 4px;
  transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
}

.meter-status {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.meter-status.high { color: #10B981; }
.meter-status.medium { color: #F59E0B; }
.meter-status.low { color: #EF4444; }
```

---

## Animated Elements

### Section Entrance Animation

```css
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.forensic-section {
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.forensic-section:nth-child(1) { animation-delay: 0.1s; }
.forensic-section:nth-child(2) { animation-delay: 0.2s; }
.forensic-section:nth-child(3) { animation-delay: 0.3s; }
```

### Pattern Pulse

```css
@keyframes patternPulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.pattern {
  animation: patternPulse 3s ease-in-out infinite;
}
```

### Thread Card Shimmer

```css
@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.thread-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.03) 50%,
    transparent 100%
  );
  background-size: 200% 100%;
  animation: shimmer 3s linear infinite;
  pointer-events: none;
}
```

---

## Complete Example Output

```html
<div class="forensic-output">
  <!-- Exposure Section -->
  <div class="forensic-section section-exposure">
    <div class="section-header">//exposure</div>
    <p>
      The systematic <span class="pattern">suppression of the divine feminine</span> 
      and the concurrent rise of <span class="pattern">centralized banking systems</span> 
      can be traced to a manipulation of narratives in Abrahamic texts.
    </p>
    <p>
      Key entities: <span class="entity">Asherah</span>, 
      <span class="entity">Baalat</span>, 
      <span class="entity">elohim</span>
    </p>
    <p class="insight-note">
      <span class="insight">Pattern detected:</span> 
      information control → power centralization
    </p>
  </div>
  
  <!-- Etymological Section -->
  <div class="forensic-section">
    <div class="section-header">//etymological incision</div>
    <p>
      "<span class="entity">elohim</span>" signified plural deities → 
      masculine singular
    </p>
    <p>
      "<span class="entity">wicce</span>" (wise one) → 
      "witch" (<span class="suppressed">negative connotation</span>)
    </p>
  </div>
  
  <!-- Burial Sites -->
  <div class="forensic-section">
    <div class="section-header">//burial sites</div>
    <p>
      <span class="suppressed">Pre-canonical fragments:</span> 
      <span class="entity">Asherah</span> worship sites
    </p>
    <p>
      Archaeological evidence: Temple locations in ancient Israel 
      <span class="citation">[Source: Archaeological Survey 2020]</span>
    </p>
  </div>
  
  <!-- Current Vectors -->
  <div class="forensic-section">
    <div class="section-header">//current vectors</div>
    <p>Modern manifestations in 2025:</p>
    <ul>
      <li><span class="modern">Tax laws</span> favoring corporations</li>
      <li><span class="modern">Religious institutions</span> controlling narratives</li>
      <li><span class="modern">Digital platforms</span> amplifying conservative voices</li>
    </ul>
  </div>
  
  <!-- Confidence Meter -->
  <div class="confidence-meter">
    <div class="meter-header">
      <span class="meter-label">Epistemological Grounding</span>
      <span class="meter-score">4/7 layers</span>
    </div>
    <div class="meter-bar">
      <div class="meter-fill" style="width: 57%"></div>
    </div>
    <div class="meter-status high">High Confidence</div>
  </div>
  
  <!-- Thread Options -->
  <div class="thread-options">
    <div class="section-header">//thread options</div>
    
    <div class="thread-card" data-type="re-enter">
      <svg class="thread-icon"><!-- Re-enter SVG --></svg>
      <span class="thread-label">Re-enter the exposure about divine feminine suppression</span>
      <svg class="thread-arrow">→</svg>
    </div>
    
    <div class="thread-card" data-type="trace">
      <svg class="thread-icon"><!-- Trace SVG --></svg>
      <span class="thread-label">Trace burial sites of Asherah temple locations</span>
      <svg class="thread-arrow">→</svg>
    </div>
    
    <div class="thread-card" data-type="cold-read">
      <svg class="thread-icon"><!-- Cold-read SVG --></svg>
      <span class="thread-label">Cold-read modern banking mechanisms against this pattern</span>
      <svg class="thread-arrow">→</svg>
    </div>
  </div>
</div>
```

---

## Backend Changes Required

### Update Prompt Template

**File:** `src/synthesis/data_synthesizer.py`

```python
# OLD
synthesis_prompt = f"""
::EXPOSURE::
[Analysis]

::ETYMOLOGICAL INCISION::
[Etymology]
"""

# NEW
synthesis_prompt = f"""
//exposure

[Analysis]

//etymological incision

[Etymology]
"""
```

### Pattern Highlighting

```python
def highlight_patterns(text):
    """Auto-wrap patterns in <span class='pattern'>"""
    
    pattern_keywords = [
        'centralization', 'suppression', 'power consolidation',
        'information control', 'authority', 'manipulation'
    ]
    
    for keyword in pattern_keywords:
        # Case-insensitive replacement
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        text = pattern.sub(
            f"<span class='pattern'>{keyword}</span>",
            text
        )
    
    return text

def highlight_entities(text, entities):
    """Auto-wrap entities in <span class='entity'>"""
    
    for entity in entities:
        text = text.replace(
            entity,
            f"<span class='entity'>{entity}</span>"
        )
    
    return text
```

---

## Implementation Priority

1. **Update prompt template** (//lowercase sections) - 1 hour
2. **Create CSS design system** - 2 hours
3. **Build custom SVG icons** - 1 hour
4. **Implement thread card UI** - 2 hours
5. **Add pattern highlighting** - 2 hours
6. **Animate sections** - 1 hour
7. **Test & polish** - 2 hours

**Total: ~11 hours**

---

## Does This Break Anything?

**No.** The changes are purely presentational:

- **Backend:** Only changes section markers (`::` → `//`)
- **Frontend:** New CSS + HTML structure
- **Logic:** Unchanged (routing, metrics, context all work the same)

The system will work identically, just look much better.
