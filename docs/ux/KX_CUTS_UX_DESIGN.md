# KX Cuts: Masonry Layout UX Design

**Date**: 2025-01-XX  
**Section**: KX Cuts (Short-Form Content)  
**Layout**: Masonry Pinterest-Style Grid  
**Philosophy**: Modular, Efficient, Spacious, Small Fonts

---

## Executive Summary

KX Cuts uses a **masonry Pinterest-style layout** with:
- **Small fonts** (Reddit-style, 11-13px)
- **Modular components** (efficient, reusable)
- **Lots of space** (generous padding, breathing room)
- **No emojis** (clean, professional)
- **Grid-based** (masonry columns, responsive)

---

## Part 1: Layout Structure

### 1.1 Masonry Grid System

**Grid Configuration**:
- **Desktop**: 4-6 columns (responsive)
- **Tablet**: 3-4 columns
- **Mobile**: 2 columns
- **Column Width**: 280-320px (flexible)
- **Gap**: 16px (generous spacing)

**Masonry Behavior**:
- Items flow naturally (no forced heights)
- Staggered layout (Pinterest-style)
- Lazy loading (infinite scroll)
- Smooth transitions

**Container**:
```css
.kx-cuts-masonry {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
    padding: 16px;
    width: 100%;
}
```

### 1.2 Responsive Breakpoints

**Breakpoints**:
- **Mobile**: < 640px → 2 columns
- **Tablet**: 640px - 1024px → 3-4 columns
- **Desktop**: > 1024px → 4-6 columns
- **Large Desktop**: > 1440px → 5-6 columns

---

## Part 2: Cut Card Design

### 2.1 Card Structure (Visual-First)

**Card Components**:
1. **Media Container** (video/image) - PRIMARY, takes 95% of space
2. **Overlay Elements** (on hover/click):
   - Creator info (minimal, overlay)
   - Interactions (floating, overlay)
   - Metadata (corner, overlay)

**Card Dimensions**:
- **Min Height**: Auto (content-driven)
- **Max Width**: 320px
- **Padding**: 0 (no padding, media edge-to-edge)
- **Border**: 1px solid (subtle)
- **Border Radius**: 8px (minimal)
- **Visual-First**: Media is primary, everything else is overlay

### 2.2 Card Spacing

**Internal Spacing**:
- No internal spacing (overlay elements only)
- Overlay elements: Positioned absolutely over media

**External Spacing**:
- Card to card: 16px (grid gap)
- Container padding: 16px

---

## Part 3: Typography System

### 3.1 Font Sizes (Mini, Modular)

**Font Scale**:
- **XXS**: 9px (counts, metadata)
- **XS**: 10px (labels, tags)
- **SM**: 11px (creator name, minimal text)

**Usage**:
- Creator name: 11px (overlay, minimal)
- Domain tags: 10px (overlay, minimal)
- Interaction labels: 10px (overlay, minimal)
- Counts: 9px (overlay, minimal)
- Time/metadata: 9px (overlay, minimal)
- No description text (visual only)

### 3.2 Font Weights

**Weights**:
- **Regular**: 400 (body text)
- **Medium**: 500 (creator names, labels)
- **Semibold**: 600 (headings, if needed)

**Usage**:
- Creator name: 500
- Description: 400
- Domain tags: 500
- Interaction labels: 400
- Counts: 400

### 3.3 Line Heights

**Line Heights**:
- **Tight**: 1.2 (headings)
- **Normal**: 1.4 (body text)
- **Relaxed**: 1.6 (descriptions)

**Usage**:
- Creator name: 1.2
- Description: 1.4
- Domain tags: 1.2
- Interaction labels: 1.2

---

## Part 4: Modular Components

### 4.1 Media Container

**Structure**:
```html
<div class="cut-media">
    <video class="cut-video" src="..." poster="..."></video>
    <div class="cut-media-overlay">
        <!-- Optional overlay content -->
    </div>
</div>
```

**Styling**:
- **Width**: 100%
- **Aspect Ratio**: 16:9 or 9:16 (content-driven)
- **Border Radius**: 8px (top corners only)
- **Object Fit**: Cover
- **Background**: Dark (loading state)

**Responsive**:
- Maintains aspect ratio
- Responsive sizing
- Lazy loading

### 4.2 Creator Info Module (Overlay)

**Structure**:
```html
<div class="cut-creator-overlay">
    <div class="cut-avatar">
        <img src="..." alt="Creator">
    </div>
    <div class="cut-creator-name">@username</div>
</div>
```

**Styling**:
- **Position**: Absolute, top-left corner
- **Avatar**: 20px × 20px (mini)
- **Name**: 11px, 500 weight
- **Background**: Semi-transparent overlay
- **Padding**: 6px 8px
- **Border Radius**: 4px (top-left corner)
- **Gap**: 6px (avatar to name)

**Layout**:
- Horizontal flex
- Overlay on media
- Visible on hover/always (minimal)

### 4.3 Description Module (Removed)

**No Description**:
- Visual-first design
- No text description
- Media speaks for itself
- Optional: Tooltip on hover (if needed)

### 4.4 Domain Tags Module (Overlay, Optional)

**Structure**:
```html
<div class="cut-domains-overlay">
    <span class="cut-domain-tag">Visual Arts</span>
</div>
```

**Styling**:
- **Position**: Absolute, bottom-left corner
- **Font Size**: 10px
- **Font Weight**: 500
- **Padding**: 4px 6px
- **Border Radius**: 4px
- **Background**: Semi-transparent overlay
- **Color**: Primary text
- **Max Tags**: 1 (only primary domain)

**Layout**:
- Single tag (minimal)
- Overlay on media
- Visible on hover/always (minimal)

### 4.5 Interaction Bar Module (Overlay, Floating)

**Structure**:
```html
<div class="cut-interactions-overlay">
    <button class="cut-interaction-btn" data-action="recognize" title="Recognize">
        <span class="interaction-dot"></span>
        <span class="interaction-count">12</span>
    </button>
    <button class="cut-interaction-btn" data-action="growth" title="Growth">
        <span class="interaction-dot"></span>
        <span class="interaction-count">5</span>
    </button>
    <button class="cut-interaction-btn" data-action="connect" title="Connect">
        <span class="interaction-dot"></span>
        <span class="interaction-count">3</span>
    </button>
</div>
```

**Styling**:
- **Position**: Absolute, bottom-right corner
- **Layout**: Vertical stack (column)
- **Gap**: 8px (between buttons)
- **Padding**: 8px
- **Background**: Semi-transparent overlay
- **Border Radius**: 8px (bottom-right corner)
- **Font Size**: 9px (counts only)
- **Visible**: On hover (or always, minimal)

**Button Styling**:
- **Padding**: 4px 6px
- **Border**: None
- **Background**: Transparent
- **Gap**: 4px (dot to count)
- **Hover**: Opacity 0.8
- **Active**: Opacity 0.6
- **No labels** (tooltip only)

**Dot Styling**:
- **Size**: 5px × 5px (smaller)
- **Border Radius**: 50%
- **Colors**: 
  - Recognize: Subtle glow (warm)
  - Growth: Subtle glow (cool)
  - Connect: Subtle glow (neutral)

### 4.6 Metadata Module (Overlay, Corner)

**Structure**:
```html
<div class="cut-metadata-overlay">
    <span class="cut-time">2h</span>
</div>
```

**Styling**:
- **Position**: Absolute, top-right corner
- **Font Size**: 9px
- **Font Weight**: 400
- **Color**: Primary text (with overlay background)
- **Padding**: 4px 6px
- **Background**: Semi-transparent overlay
- **Border Radius**: 4px (top-right corner)
- **Layout**: Single item (time only, minimal)
- **Visible**: Always (minimal, corner)

---

## Part 5: Complete Card Markup

### 5.1 Full Card Structure (Visual-First)

```html
<article class="cut-card" data-cut-id="...">
    <!-- Media (Primary, 95% of space) -->
    <div class="cut-media">
        <video class="cut-video" src="..." poster="..." muted></video>
        
        <!-- Creator Info Overlay (Top-Left) -->
        <div class="cut-creator-overlay">
            <div class="cut-avatar">
                <img src="..." alt="Creator">
            </div>
            <div class="cut-creator-name">@username</div>
        </div>
        
        <!-- Metadata Overlay (Top-Right) -->
        <div class="cut-metadata-overlay">
            <span class="cut-time">2h</span>
        </div>
        
        <!-- Domain Tag Overlay (Bottom-Left, Optional) -->
        <div class="cut-domains-overlay">
            <span class="cut-domain-tag">Visual Arts</span>
        </div>
        
        <!-- Interactions Overlay (Bottom-Right, On Hover) -->
        <div class="cut-interactions-overlay">
            <button class="cut-interaction-btn" data-action="recognize" title="Recognize">
                <span class="interaction-dot"></span>
                <span class="interaction-count">12</span>
            </button>
            <button class="cut-interaction-btn" data-action="growth" title="Growth">
                <span class="interaction-dot"></span>
                <span class="interaction-count">5</span>
            </button>
            <button class="cut-interaction-btn" data-action="connect" title="Connect">
                <span class="interaction-dot"></span>
                <span class="interaction-count">3</span>
            </button>
        </div>
    </div>
</article>
```

---

## Part 6: CSS Implementation

### 6.1 Masonry Container

```css
.kx-cuts-masonry {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
    padding: 16px;
    width: 100%;
    align-items: start;
}

@media (max-width: 640px) {
    .kx-cuts-masonry {
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        padding: 12px;
    }
}

@media (min-width: 1024px) {
    .kx-cuts-masonry {
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    }
}

@media (min-width: 1440px) {
    .kx-cuts-masonry {
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    }
}
```

### 6.2 Cut Card (Visual-First)

```css
.cut-card {
    background: var(--bg-secondary);
    border: var(--border-width-thin) solid var(--border-color);
    border-radius: 8px;
    padding: 0;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s ease;
}

.cut-card:hover {
    border-color: var(--text-secondary);
}

.cut-card:hover .cut-interactions-overlay {
    opacity: 1;
}
```

### 6.3 Media Container (Primary)

```css
.cut-media {
    width: 100%;
    position: relative;
    background: var(--bg-tertiary);
    aspect-ratio: 9 / 16;
    overflow: hidden;
}

.cut-video {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}

/* All overlays positioned absolutely over media */
.cut-creator-overlay,
.cut-metadata-overlay,
.cut-domains-overlay,
.cut-interactions-overlay {
    position: absolute;
    z-index: 10;
    pointer-events: auto;
}
```

### 6.4 Creator Info (Overlay, Top-Left)

```css
.cut-creator-overlay {
    top: 8px;
    left: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 8px;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    border-radius: 4px;
    border-top-left-radius: 8px;
}

.cut-avatar {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    overflow: hidden;
    flex-shrink: 0;
    background: var(--bg-tertiary);
}

.cut-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.cut-creator-name {
    font-size: 11px;
    font-weight: 500;
    color: var(--text-primary);
    line-height: 1.2;
    white-space: nowrap;
}
```

### 6.5 Description (Removed)

```css
/* No description - visual-first design */
```

### 6.6 Domain Tags (Overlay, Bottom-Left, Optional)

```css
.cut-domains-overlay {
    bottom: 8px;
    left: 8px;
    padding: 4px 6px;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    border-radius: 4px;
    border-bottom-left-radius: 8px;
}

.cut-domain-tag {
    font-size: 10px;
    font-weight: 500;
    color: var(--text-primary);
    line-height: 1.2;
    white-space: nowrap;
}
```

### 6.7 Interaction Bar (Overlay, Bottom-Right, On Hover)

```css
.cut-interactions-overlay {
    bottom: 8px;
    right: 8px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 8px;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    border-radius: 8px;
    border-bottom-right-radius: 8px;
    opacity: 0;
    transition: opacity 0.2s ease;
}

.cut-card:hover .cut-interactions-overlay {
    opacity: 1;
}

.cut-interaction-btn {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 6px;
    border: none;
    background: transparent;
    cursor: pointer;
    transition: opacity 0.2s ease;
}

.cut-interaction-btn:hover {
    opacity: 0.8;
}

.cut-interaction-btn:active {
    opacity: 0.6;
}

.interaction-dot {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    flex-shrink: 0;
}

.cut-interaction-btn[data-action="recognize"] .interaction-dot {
    background-color: rgba(255, 255, 255, 0.6);
    box-shadow: 0 0 3px rgba(255, 255, 255, 0.4);
}

.cut-interaction-btn[data-action="growth"] .interaction-dot {
    background-color: rgba(96, 165, 250, 0.6);
    box-shadow: 0 0 3px rgba(96, 165, 250, 0.4);
}

.cut-interaction-btn[data-action="connect"] .interaction-dot {
    background-color: rgba(168, 85, 247, 0.6);
    box-shadow: 0 0 3px rgba(168, 85, 247, 0.4);
}

.interaction-count {
    font-size: 9px;
    font-weight: 400;
    color: var(--text-primary);
    line-height: 1.2;
}
```

### 6.8 Metadata (Overlay, Top-Right)

```css
.cut-metadata-overlay {
    top: 8px;
    right: 8px;
    padding: 4px 6px;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    border-radius: 4px;
    border-top-right-radius: 8px;
}

.cut-time {
    font-size: 9px;
    font-weight: 400;
    color: var(--text-primary);
    line-height: 1.2;
    white-space: nowrap;
}
```

---

## Part 7: Spacing System

### 7.1 Vertical Spacing

**Card Internal Spacing**:
- Media to creator: 12px
- Creator to description: 8px
- Description to tags: 8px
- Tags to interactions: 12px
- Interactions to metadata: 8px

**Card External Spacing**:
- Grid gap: 16px
- Container padding: 16px

### 7.2 Horizontal Spacing

**Component Gaps**:
- Avatar to info: 8px
- Tag to tag: 6px
- Interaction to interaction: 12px
- Metadata items: 8px

---

## Part 8: Responsive Behavior

### 8.1 Mobile (< 640px)

**Changes**:
- 2 columns
- Gap: 12px
- Padding: 12px
- Font sizes: Same (already small)
- Card padding: 10px

### 8.2 Tablet (640px - 1024px)

**Changes**:
- 3-4 columns
- Gap: 16px
- Padding: 16px
- Standard sizing

### 8.3 Desktop (> 1024px)

**Changes**:
- 4-6 columns
- Gap: 16px
- Padding: 16px
- Max column width: 320px

---

## Part 9: Interaction States

### 9.1 Hover States

**Card Hover**:
- Border color: Secondary (lighter)
- No scale/transform (subtle)

**Button Hover**:
- Opacity: 0.8
- No background change

### 9.2 Active States

**Button Active**:
- Opacity: 0.6
- No background change

### 9.3 Focus States

**Button Focus**:
- Outline: 1px solid (subtle)
- No background change

---

## Part 10: Loading States

### 10.1 Skeleton Loading

**Skeleton Card**:
```css
.cut-card-skeleton {
    background: var(--bg-secondary);
    border: var(--border-width-thin) solid var(--border-color);
    border-radius: 8px;
    padding: 12px;
    animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
```

**Skeleton Components**:
- Media: Aspect ratio box with background
- Creator: Avatar circle + text lines
- Description: Text lines
- Tags: Small boxes
- Interactions: Small boxes

---

## Part 11: Infinite Scroll

### 11.1 Scroll Behavior

**Implementation**:
- Intersection Observer API
- Load more when bottom visible
- Smooth loading (no jump)

**Loading Indicator**:
- Small, subtle spinner
- Bottom of grid
- 11px font size
- Tertiary color

---

## Part 12: Performance

### 12.1 Optimizations

**Lazy Loading**:
- Images/videos: `loading="lazy"`
- Intersection Observer for visibility

**Virtual Scrolling**:
- Optional: For very long feeds
- Render visible items only

**Image Optimization**:
- Responsive images
- WebP format
- Proper sizing

---

## Part 13: Accessibility

### 13.1 ARIA Labels

**Card**:
```html
<article class="cut-card" role="article" aria-label="Cut by @username">
```

**Buttons**:
```html
<button class="cut-interaction-btn" aria-label="Recognize this cut">
```

### 13.2 Keyboard Navigation

**Tab Order**:
- Media (if interactive)
- Creator link
- Interaction buttons
- Metadata

**Focus Indicators**:
- Visible outline
- Subtle, not distracting

---

## Part 14: Implementation Notes

### 14.1 JavaScript Requirements

**Functions Needed**:
- Render cut cards
- Handle interactions (recognize, growth, connect)
- Infinite scroll
- Lazy loading
- Responsive grid

### 14.2 Data Structure

**Cut Object**:
```javascript
{
    id: "cut_123",
    media: {
        video_url: "...",
        thumbnail_url: "...",
        type: "video"
    },
    creator: {
        id: "user_123",
        username: "username",
        avatar_url: "...",
        level: "Experienced"
    },
    description: "Description text...",
    domains: ["Visual Arts", "Painting"],
    interactions: {
        recognize: 12,
        growth: 5,
        connect: 3
    },
    metadata: {
        created_at: "...",
        views: 1200
    }
}
```

---

## Part 15: Visual Examples

### 15.1 Card Layout (Visual-First)

```
┌─────────────────────────┐
│ [Avatar] @username  2h  │ ← Overlay (top)
│                         │
│                         │
│      Media (Video)      │
│      (95% of space)     │
│                         │
│                         │
│ [Visual Arts]    • 12   │ ← Overlay (bottom)
│                 • 5     │   (on hover)
│                 • 3     │
└─────────────────────────┘

All text is overlay, minimal, tiny fonts (9-11px)
No dedicated space for metrics - all overlay
```

### 15.2 Grid Layout

```
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│ Cut │ │ Cut │ │ Cut │ │ Cut │
│  1  │ │  2  │ │  3  │ │  4  │
└─────┘ └─────┘ └─────┘ └─────┘
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│ Cut │ │ Cut │ │ Cut │ │ Cut │
│  5  │ │  6  │ │  7  │ │  8  │
└─────┘ └─────┘ └─────┘ └─────┘
```

---

## Part 16: Summary

### 16.1 Key Features

1. **Visual-First**: Media takes 95% of space
2. **Masonry Grid**: Pinterest-style, responsive
3. **Mini Fonts**: 9-11px (ultra-small, modular)
4. **Overlay Elements**: All text/metrics overlay on media
5. **No Dedicated Space**: No space for metrics/text
6. **Modular Components**: Reusable, efficient
7. **Lots of Space**: 16px gaps between cards
8. **No Emojis**: Clean, professional
9. **Interactions**: Recognize, Growth, Connect (overlay, on hover)

### 16.2 Design Principles

- **Visual-First**: Media is primary, everything else is overlay
- **Minimal Text**: Ultra-small fonts (9-11px), only essential
- **No Dedicated Metrics**: All metrics overlay, no space dedicated
- **Modular**: Reusable components, efficient
- **Spacious**: Generous gaps between cards
- **Professional**: No emojis, clean design
- **Hover Interactions**: Metrics appear on hover (or always minimal)

---

**End of Document**

