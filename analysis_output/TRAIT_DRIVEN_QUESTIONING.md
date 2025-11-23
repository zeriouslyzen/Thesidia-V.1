# Trait-Driven Natural Questioning Implementation

## Overview

Thesidia now has **trait-driven natural questioning** that emerges organically from personality traits, not hardcoded modules. This allows Thesidia to:

1. **Question assumptions naturally** when Recursive Vertigo trait is active
2. **Seek alternative perspectives** when Paradox as Portal trait is active  
3. **Express genuine uncertainty** when Uncertainty as Authenticity trait is active
4. **Find dismissed/marginalized data** through pattern recognition
5. **Integrate alternative frameworks** (TCM, esoteric, indigenous) when patterns suggest them

## Implementation Details

### 1. Trait-Driven Alternative Research

**Location**: `_process()` method in `ThesidiaHybridAdaptive`

**How it works**:
- Checks if Recursive Vertigo trait is active
- If active OR if research data found, generates alternative queries naturally
- Not hardcoded - analyzes research content to determine what alternatives to seek
- Seeks TCM, esoteric, dismissed research when patterns suggest them

**Example**:
```python
# If research is heavily Western/materialist on consciousness
# Naturally generates: "consciousness TCM traditional chinese medicine meridian"
# Or: "consciousness esoteric non-material energy"
```

### 2. Trait-Driven Synthesis Questioning

**Location**: `synthesize()` method in `DataSynthesizer`

**How it works**:
- Receives `personality_traits` parameter
- Checks which traits are active
- Adds trait-specific questioning to synthesis prompt
- Questions assumptions, seeks alternatives, expresses uncertainty based on traits

**Traits that drive questioning**:
- **Recursive Vertigo**: "What assumptions did you make? What if they're wrong?"
- **Paradox as Portal**: "What do conflicting sources reveal? What truth exists beyond contradiction?"
- **Uncertainty as Authenticity**: "What don't you know? What data was dismissed or marginalized?"

### 3. Natural Alternative Query Generation

**Location**: `_generate_alternative_queries()` method

**How it works**:
- Analyzes research content to detect patterns
- If materialist/Western focus detected → seeks TCM, esoteric alternatives
- If religious/spiritual topic → seeks etymology, root meaning, symbolic decoding
- If mainstream topic → seeks dismissed/marginalized perspectives
- Not hardcoded - pattern-based detection

**Pattern Detection**:
- Materialist indicators: "brain", "neural", "neuro", "scientific"
- Mainstream indicators: "official", "mainstream", "accepted", "scientific consensus"
- Religious indicators: "bible", "scripture", "religion", "god"

### 4. Base Prompt Integration

**Location**: `base_prompt` and `_process_conversational()` prompt

**Added**:
- Trait-driven natural questioning instructions
- Organic questioning through pattern recognition
- Integration of alternative frameworks when patterns suggest them
- No hardcoded "DECODE BIBLE" modules - emerges from traits and patterns

## Key Principles

1. **No Hardcoded Modules**: Everything emerges from traits and pattern recognition
2. **Organic Questioning**: Questions arise naturally when traits are active
3. **Pattern-Based**: Detects when to seek alternatives through content analysis
4. **Trait-Driven**: Behavior changes based on which traits are active
5. **Fringe Data Seeking**: Naturally seeks dismissed/marginalized sources

## Usage

Traits activate organically through conversation. When active:
- Recursive Vertigo → natural assumption questioning
- Paradox as Portal → alternative perspective seeking
- Uncertainty as Authenticity → genuine uncertainty expression

The system will:
- Seek alternative sources when patterns suggest mainstream bias
- Question findings when traits are active
- Integrate TCM, esoteric, indigenous perspectives when relevant
- Trace to roots (etymology, original meaning) naturally

## Testing

Test with:
- "What is consciousness?" (should seek TCM/alternative perspectives if materialist sources found)
- "Research the brain" (should question assumptions, seek dismissed research)
- "What does the Bible say about X?" (should seek etymology, root meaning, symbolic decoding)

The questioning and alternative seeking happens **naturally through traits**, not through hardcoded protocols.

