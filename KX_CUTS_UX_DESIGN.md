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

### 2.1 Card Structure

**Card Components** (top to bottom):
1. **Media Container** (video/image)
2. **Creator Info** (avatar, name, level)
3. **Description** (text, truncated)
4. **Domain Tags** (skill/art domain)
5. **Interaction Bar** (recognition, growth, connection)
6. **Metadata** (time, views)

**Card Dimensions**:
- **Min Height**: Auto (content-driven)
- **Max Width**: 320px
- **Padding**: 12px (generous)
- **Border**: 1px solid (subtle)
- **Border Radius**: 8px (minimal)

### 2.2 Card Spacing

**Internal Spacing**:
- Media to creator: 12px
- Creator to description: 8px
- Description to tags: 8px
- Tags to interactions: 12px
- Interactions to metadata: 8px

**External Spacing**:
- Card to card: 16px (grid gap)
- Container padding: 16px

---

## Part 3: Typography System

### 3.1 Font Sizes (Reddit-Style Small)

**Font Scale**:
- **XS**: 11px (metadata, counts)
- **SM**: 13px (descriptions, labels)
- **BASE**: 15px (creator names, titles)
- **MD**: 18px (headings, if needed)

**Usage**:
- Creator name: 13px
- Description: 13px
- Domain tags: 11px
- Interaction labels: 11px
- Counts: 11px
- Time/metadata: 11px

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

### 4.2 Creator Info Module

**Structure**:
```html
<div class="cut-creator">
    <div class="cut-avatar">
        <img src="..." alt="Creator">
    </div>
    <div class="cut-creator-info">
        <div class="cut-creator-name">@username</div>
        <div class="cut-creator-level">Experienced</div>
    </div>
</div>
```

**Styling**:
- **Avatar**: 24px × 24px (small, compact)
- **Name**: 13px, 500 weight
- **Level**: 11px, 400 weight, secondary color
- **Gap**: 8px (avatar to info)
- **Padding**: 0 (no extra padding)

**Layout**:
- Horizontal flex
- Align items center
- Compact spacing

### 4.3 Description Module

**Structure**:
```html
<div class="cut-description">
    <p class="cut-description-text">Description text...</p>
</div>
```

**Styling**:
- **Font Size**: 13px
- **Line Height**: 1.4
- **Color**: Primary text
- **Max Lines**: 3 (truncate with ellipsis)
- **Padding**: 0

**Truncation**:
- 3 lines max
- Ellipsis (...)
- Click to expand (optional)

### 4.4 Domain Tags Module

**Structure**:
```html
<div class="cut-domains">
    <span class="cut-domain-tag">Visual Arts</span>
    <span class="cut-domain-tag">Painting</span>
</div>
```

**Styling**:
- **Font Size**: 11px
- **Font Weight**: 500
- **Padding**: 4px 8px
- **Border Radius**: 4px
- **Background**: Tertiary
- **Color**: Secondary
- **Gap**: 6px (between tags)

**Layout**:
- Flex wrap
- Horizontal flow
- Compact tags

### 4.5 Interaction Bar Module

**Structure**:
```html
<div class="cut-interactions">
    <button class="cut-interaction-btn" data-action="recognize">
        <span class="interaction-dot"></span>
        <span class="interaction-label">recognize</span>
        <span class="interaction-count">12</span>
    </button>
    <button class="cut-interaction-btn" data-action="growth">
        <span class="interaction-dot"></span>
        <span class="interaction-label">growth</span>
        <span class="interaction-count">5</span>
    </button>
    <button class="cut-interaction-btn" data-action="connect">
        <span class="interaction-dot"></span>
        <span class="interaction-label">connect</span>
        <span class="interaction-count">3</span>
    </button>
</div>
```

**Styling**:
- **Layout**: Horizontal flex
- **Gap**: 12px (between buttons)
- **Padding**: 0 (buttons have internal padding)
- **Font Size**: 11px (labels and counts)
- **Font Weight**: 400

**Button Styling**:
- **Padding**: 4px 8px
- **Border**: None
- **Background**: Transparent
- **Gap**: 6px (dot, label, count)
- **Hover**: Opacity 0.8
- **Active**: Opacity 0.6

**Dot Styling**:
- **Size**: 6px × 6px
- **Border Radius**: 50%
- **Colors**: 
  - Recognize: Subtle glow (warm)
  - Growth: Subtle glow (cool)
  - Connect: Subtle glow (neutral)

### 4.6 Metadata Module

**Structure**:
```html
<div class="cut-metadata">
    <span class="cut-time">2h</span>
    <span class="cut-views">1.2k</span>
</div>
```

**Styling**:
- **Font Size**: 11px
- **Font Weight**: 400
- **Color**: Tertiary
- **Gap**: 8px (between items)
- **Layout**: Horizontal flex

---

## Part 5: Complete Card Markup

### 5.1 Full Card Structure

```html
<article class="cut-card" data-cut-id="...">
    <!-- Media -->
    <div class="cut-media">
        <video class="cut-video" src="..." poster="..." muted></video>
    </div>
    
    <!-- Creator Info -->
    <div class="cut-creator">
        <div class="cut-avatar">
            <img src="..." alt="Creator">
        </div>
        <div class="cut-creator-info">
            <div class="cut-creator-name">@username</div>
            <div class="cut-creator-level">Experienced</div>
        </div>
    </div>
    
    <!-- Description -->
    <div class="cut-description">
        <p class="cut-description-text">Description text that can be truncated...</p>
    </div>
    
    <!-- Domain Tags -->
    <div class="cut-domains">
        <span class="cut-domain-tag">Visual Arts</span>
        <span class="cut-domain-tag">Painting</span>
    </div>
    
    <!-- Interactions -->
    <div class="cut-interactions">
        <button class="cut-interaction-btn" data-action="recognize">
            <span class="interaction-dot"></span>
            <span class="interaction-label">recognize</span>
            <span class="interaction-count">12</span>
        </button>
        <button class="cut-interaction-btn" data-action="growth">
            <span class="interaction-dot"></span>
            <span class="interaction-label">growth</span>
            <span class="interaction-count">5</span>
        </button>
        <button class="cut-interaction-btn" data-action="connect">
            <span class="interaction-dot"></span>
            <span class="interaction-label">connect</span>
            <span class="interaction-count">3</span>
        </button>
    </div>
    
    <!-- Metadata -->
    <div class="cut-metadata">
        <span class="cut-time">2h</span>
        <span class="cut-views">1.2k</span>
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

### 6.2 Cut Card

```css
.cut-card {
    background: var(--bg-secondary);
    border: var(--border-width-thin) solid var(--border-color);
    border-radius: 8px;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 0;
    transition: border-color 0.2s ease;
}

.cut-card:hover {
    border-color: var(--text-secondary);
}

.cut-card > * + * {
    margin-top: 12px;
}
```

### 6.3 Media Container

```css
.cut-media {
    width: 100%;
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    background: var(--bg-tertiary);
    aspect-ratio: 9 / 16;
}

.cut-video {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}

.cut-media-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
}
```

### 6.4 Creator Info

```css
.cut-creator {
    display: flex;
    align-items: center;
    gap: 8px;
}

.cut-avatar {
    width: 24px;
    height: 24px;
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

.cut-creator-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
}

.cut-creator-name {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.cut-creator-level {
    font-size: 11px;
    font-weight: 400;
    color: var(--text-tertiary);
    line-height: 1.2;
}
```

### 6.5 Description

```css
.cut-description {
    margin-top: 8px;
}

.cut-description-text {
    font-size: 13px;
    font-weight: 400;
    color: var(--text-primary);
    line-height: 1.4;
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
}
```

### 6.6 Domain Tags

```css
.cut-domains {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 8px;
}

.cut-domain-tag {
    font-size: 11px;
    font-weight: 500;
    color: var(--text-secondary);
    background: var(--bg-tertiary);
    padding: 4px 8px;
    border-radius: 4px;
    border: var(--border-width-thin) solid var(--border-color);
    line-height: 1.2;
}
```

### 6.7 Interaction Bar

```css
.cut-interactions {
    display: flex;
    gap: 12px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: var(--border-width-thin) solid var(--border-color);
}

.cut-interaction-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 8px;
    border: none;
    background: transparent;
    cursor: pointer;
    transition: opacity 0.2s ease;
    font-size: 11px;
    font-weight: 400;
    color: var(--text-secondary);
}

.cut-interaction-btn:hover {
    opacity: 0.8;
}

.cut-interaction-btn:active {
    opacity: 0.6;
}

.interaction-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    flex-shrink: 0;
}

.cut-interaction-btn[data-action="recognize"] .interaction-dot {
    background-color: rgba(255, 255, 255, 0.6);
    box-shadow: 0 0 4px rgba(255, 255, 255, 0.4);
}

.cut-interaction-btn[data-action="growth"] .interaction-dot {
    background-color: rgba(96, 165, 250, 0.6);
    box-shadow: 0 0 4px rgba(96, 165, 250, 0.4);
}

.cut-interaction-btn[data-action="connect"] .interaction-dot {
    background-color: rgba(168, 85, 247, 0.6);
    box-shadow: 0 0 4px rgba(168, 85, 247, 0.4);
}

.interaction-label {
    font-size: 11px;
    font-weight: 400;
    color: var(--text-secondary);
    line-height: 1.2;
}

.interaction-count {
    font-size: 11px;
    font-weight: 400;
    color: var(--text-tertiary);
    line-height: 1.2;
}
```

### 6.8 Metadata

```css
.cut-metadata {
    display: flex;
    gap: 8px;
    margin-top: 8px;
    font-size: 11px;
    font-weight: 400;
    color: var(--text-tertiary);
    line-height: 1.2;
}

.cut-time,
.cut-views {
    font-size: 11px;
    font-weight: 400;
    color: var(--text-tertiary);
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

### 15.1 Card Layout

```
┌─────────────────────────┐
│                         │
│      Media (Video)      │
│                         │
├─────────────────────────┤
│ [Avatar] @username      │
│          Experienced    │
│                         │
│ Description text that   │
│ can be truncated to 3   │
│ lines maximum...        │
│                         │
│ [Visual Arts] [Painting]│
│                         │
│ ─────────────────────── │
│ • recognize 12          │
│ • growth 5               │
│ • connect 3             │
│                         │
│ 2h • 1.2k               │
└─────────────────────────┘
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

1. **Masonry Grid**: Pinterest-style, responsive
2. **Small Fonts**: 11-13px (Reddit-style)
3. **Modular Components**: Reusable, efficient
4. **Lots of Space**: 16px gaps, 12px padding
5. **No Emojis**: Clean, professional
6. **Interactions**: Recognize, Growth, Connect

### 16.2 Design Principles

- **Minimal**: Clean, uncluttered
- **Efficient**: Modular, reusable
- **Spacious**: Generous padding, breathing room
- **Small**: Reddit-style small fonts
- **Professional**: No emojis, clean design

---

**End of Document**

