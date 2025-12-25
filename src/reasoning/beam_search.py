#!/usr/bin/env python3
"""
Parallel Beam Search
====================

M1-optimized candidate generation with quality scoring.
Generates multiple response candidates and selects the best.

Part of Phase 1: Advanced Reasoning implementation.

M1 Constraints:
- Batch size: 2 (not 4) due to unified memory limits
- Single model instance, multiple prompts
- Fallback to sequential if batching fails
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add sibling directories to path for imports
_src_dir = Path(__file__).resolve().parent.parent
for subdir in ['core', 'reasoning', 'research', 'support']:
    subdir_path = str(_src_dir / subdir)
    if subdir_path not in sys.path:
        sys.path.insert(0, subdir_path)

# Import dependencies
try:
    from model_client import ModelClient
except ImportError:
    ModelClient = None

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# MLX support (Apple Silicon optimization)
try:
    import mlx.core as mx
    from mlx_lm import load, generate
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False


@dataclass
class Candidate:
    """A single response candidate"""
    perspective: str
    prompt: str
    response: str = ""
    generation_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScoredCandidate:
    """A candidate with quality scores"""
    candidate: Candidate
    quality_score: float = 0.0
    coherence_score: float = 0.0
    depth_score: float = 0.0
    combined_score: float = 0.0


class ParallelBeamSearch:
    """
    M1-optimized parallel candidate generation and selection.
    
    Generates multiple response candidates from different perspectives,
    scores them, and selects the best or combines insights.
    
    Optimized for Apple Silicon:
    - Batch size limited to 2 (unified memory constraint)
    - Uses MLX when available for efficient batching
    - Falls back to Ollama + threading if MLX unavailable
    """
    
    # Default perspectives for beam search
    DEFAULT_PERSPECTIVES = [
        "analytical",      # Logical, structured analysis
        "creative",        # Novel connections, insights
        "critical",        # Skeptical, questioning
        "integrative"      # Connecting multiple domains
    ]
    
    # M1 memory constraint
    MAX_BATCH_SIZE = 2
    
    def __init__(
        self,
        model: str = "clean-mistral:latest",
        model_client: Optional[ModelClient] = None,
        use_mlx: bool = True
    ):
        self.model = model
        self.model_client = model_client
        self.use_mlx = use_mlx and MLX_AVAILABLE
        self.generation_history = []
        
        # MLX model (loaded lazily)
        self._mlx_model = None
        self._mlx_tokenizer = None
    
    def _ensure_mlx_loaded(self):
        """Lazy load MLX model"""
        if self.use_mlx and self._mlx_model is None:
            try:
                # Load MLX-compatible model
                self._mlx_model, self._mlx_tokenizer = load("mlx-community/Mistral-7B-v0.3")
                print("✅ MLX model loaded for beam search")
            except Exception as e:
                print(f"⚠️ MLX model load failed: {e}, falling back to Ollama")
                self.use_mlx = False
    
    def generate_candidates(
        self,
        query: str,
        perspectives: List[str] = None,
        max_tokens: int = 500,
        system_prompt: str = None
    ) -> List[Candidate]:
        """
        Generate multiple response candidates from different perspectives.
        
        Args:
            query: The query to respond to
            perspectives: List of perspectives to explore (default: analytical, creative, critical, integrative)
            max_tokens: Maximum tokens per candidate
            system_prompt: Optional system prompt to use
            
        Returns:
            List of Candidate objects with generated responses
        """
        perspectives = perspectives or self.DEFAULT_PERSPECTIVES[:self.MAX_BATCH_SIZE * 2]  # Limit to 4
        
        # Create candidates
        candidates = []
        for perspective in perspectives:
            prompt = self._build_perspective_prompt(query, perspective, system_prompt)
            candidates.append(Candidate(
                perspective=perspective,
                prompt=prompt,
                metadata={"query": query}
            ))
        
        # Generate responses
        if self.use_mlx:
            candidates = self._generate_mlx_batched(candidates, max_tokens)
        else:
            candidates = self._generate_ollama_parallel(candidates, max_tokens)
        
        # Record history
        self.generation_history.append({
            "query": query,
            "candidates": len(candidates),
            "timestamp": datetime.now().isoformat()
        })
        
        return candidates
    
    def _build_perspective_prompt(self, query: str, perspective: str, system_prompt: str = None) -> str:
        """Build prompt for a specific perspective"""
        perspective_instructions = {
            "analytical": "Analyze this systematically. Break down into components. Identify structure, patterns, and logical relationships.",
            "creative": "Explore novel angles. Make unexpected connections. Look for insights that aren't immediately obvious.",
            "critical": "Question assumptions. Identify weaknesses. What's missing? What could be wrong?",
            "integrative": "Connect across domains. How does this relate to other fields? What universal patterns appear?"
        }
        
        instruction = perspective_instructions.get(perspective, f"Explore from a {perspective} perspective.")
        
        base_prompt = f"""Perspective: {perspective.upper()}

{instruction}

Query: {query}

Respond thoughtfully from this perspective. Be specific and insightful."""

        if system_prompt:
            base_prompt = f"{system_prompt}\n\n{base_prompt}"
        
        return base_prompt
    
    def _generate_mlx_batched(self, candidates: List[Candidate], max_tokens: int) -> List[Candidate]:
        """Generate responses using MLX batch processing (M1 optimized)"""
        self._ensure_mlx_loaded()
        
        if not self._mlx_model:
            # Fallback to Ollama if MLX failed to load
            return self._generate_ollama_parallel(candidates, max_tokens)
        
        # Process in batches of MAX_BATCH_SIZE
        for i in range(0, len(candidates), self.MAX_BATCH_SIZE):
            batch = candidates[i:i + self.MAX_BATCH_SIZE]
            
            try:
                start_time = time.time()
                
                # Generate for batch (MLX handles this efficiently on unified memory)
                for candidate in batch:
                    response = generate(
                        self._mlx_model,
                        self._mlx_tokenizer,
                        prompt=candidate.prompt,
                        max_tokens=max_tokens,
                        verbose=False
                    )
                    candidate.response = response
                    candidate.generation_time = time.time() - start_time
                    
            except Exception as e:
                print(f"⚠️ MLX batch generation error: {e}")
                # Fall back to sequential for this batch
                for candidate in batch:
                    candidate.response = self._generate_single_ollama(candidate.prompt, max_tokens)
        
        return candidates
    
    def _generate_ollama_parallel(self, candidates: List[Candidate], max_tokens: int) -> List[Candidate]:
        """Generate responses using Ollama with threading"""
        with ThreadPoolExecutor(max_workers=min(len(candidates), 4)) as executor:
            future_to_candidate = {
                executor.submit(self._generate_single_ollama, c.prompt, max_tokens): c
                for c in candidates
            }
            
            for future in as_completed(future_to_candidate, timeout=120):
                candidate = future_to_candidate[future]
                try:
                    start_time = time.time()
                    candidate.response = future.result()
                    candidate.generation_time = time.time() - start_time
                except Exception as e:
                    candidate.response = f"Error: {e}"
                    candidate.metadata["error"] = str(e)
        
        return candidates
    
    def _generate_single_ollama(self, prompt: str, max_tokens: int) -> str:
        """Generate a single response using Ollama or ModelClient"""
        if self.model_client:
            response = self.model_client.chat(
                model=self.model,
                input_text=prompt,
                options={
                    "temperature": 0.8,
                    "num_predict": max_tokens,
                    "top_p": 0.9
                }
            )
            return response.get('message', {}).get('content', '')
        elif OLLAMA_AVAILABLE:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": 0.8,
                    "num_predict": max_tokens,
                    "top_p": 0.9
                }
            )
            return response.message.content if hasattr(response, 'message') else str(response)
        else:
            return "No model available for generation"
    
    def score_candidates(self, candidates: List[Candidate]) -> List[ScoredCandidate]:
        """
        Score candidates on quality, coherence, and depth.
        
        Returns candidates sorted by combined score (highest first).
        """
        scored = []
        
        for candidate in candidates:
            if "Error" in candidate.response[:50]:
                scored.append(ScoredCandidate(
                    candidate=candidate,
                    quality_score=0.0,
                    coherence_score=0.0,
                    depth_score=0.0,
                    combined_score=0.0
                ))
                continue
            
            quality = self._score_quality(candidate.response)
            coherence = self._score_coherence(candidate.response)
            depth = self._score_depth(candidate.response, candidate.perspective)
            
            # Weighted combination
            combined = quality * 0.35 + coherence * 0.35 + depth * 0.30
            
            scored.append(ScoredCandidate(
                candidate=candidate,
                quality_score=quality,
                coherence_score=coherence,
                depth_score=depth,
                combined_score=combined
            ))
        
        # Sort by combined score
        scored.sort(key=lambda x: x.combined_score, reverse=True)
        return scored
    
    def _score_quality(self, response: str) -> float:
        """Score response quality"""
        score = 0.5
        
        # Length (not too short, not too long)
        length = len(response)
        if 200 <= length <= 1500:
            score += 0.2
        elif length > 1500:
            score += 0.1
        
        # Specificity
        specificity = ["specifically", "for example", "such as", "in particular"]
        for marker in specificity:
            if marker in response.lower():
                score += 0.05
        
        return min(1.0, score)
    
    def _score_coherence(self, response: str) -> float:
        """Score response coherence and structure"""
        score = 0.5
        
        # Sentence structure
        sentences = response.split('.')
        if len(sentences) >= 3:
            score += 0.1
        
        # Logical connectors
        connectors = ["therefore", "because", "however", "additionally", "furthermore"]
        for connector in connectors:
            if connector in response.lower():
                score += 0.05
        
        # Paragraph structure
        paragraphs = response.split('\n\n')
        if len(paragraphs) >= 2:
            score += 0.1
        
        return min(1.0, score)
    
    def _score_depth(self, response: str, perspective: str) -> float:
        """Score depth relative to perspective"""
        score = 0.5
        response_lower = response.lower()
        
        perspective_keywords = {
            "analytical": ["structure", "component", "pattern", "relationship", "systematic"],
            "creative": ["novel", "unexpected", "connection", "insight", "imagine"],
            "critical": ["question", "assumption", "weakness", "missing", "problem"],
            "integrative": ["domain", "connect", "relate", "universal", "across"]
        }
        
        keywords = perspective_keywords.get(perspective, [])
        for keyword in keywords:
            if keyword in response_lower:
                score += 0.06
        
        return min(1.0, score)
    
    def select_best(self, candidates: List[Candidate]) -> str:
        """Select the best candidate response"""
        scored = self.score_candidates(candidates)
        if scored:
            return scored[0].candidate.response
        return ""
    
    def combine_insights(
        self,
        candidates: List[Candidate],
        query: str,
        max_tokens: int = 1500
    ) -> str:
        """
        Combine insights from multiple candidates into a unified response.
        
        Uses the top candidates and synthesizes them together.
        """
        scored = self.score_candidates(candidates)
        
        # Take top 3 candidates
        top_candidates = scored[:3]
        
        # Build combination prompt
        insights = []
        for i, sc in enumerate(top_candidates, 1):
            insights.append(f"""
**{sc.candidate.perspective.upper()}** (score: {sc.combined_score:.2f})
{sc.candidate.response[:800]}
""")
        
        combine_prompt = f"""Combine these perspectives into a unified response:

Query: {query}

{chr(10).join(insights)}

TASK:
1. Extract the key insights from each perspective
2. Identify complementary ideas
3. Create a coherent synthesis that includes the best from each
4. Resolve any tensions or contradictions

Write a unified response that draws from all perspectives. Be comprehensive but coherent."""

        # Generate combination
        return self._generate_single_ollama(combine_prompt, max_tokens)
    
    def search_and_select(
        self,
        query: str,
        perspectives: List[str] = None,
        combine: bool = False,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """
        Convenience method: generate candidates and select/combine best.
        
        Args:
            query: The query to respond to
            perspectives: Perspectives to explore
            combine: If True, combine insights; if False, just select best
            max_tokens: Max tokens per candidate
            
        Returns:
            Dictionary with candidates, scores, and final response
        """
        start_time = time.time()
        
        # Generate
        candidates = self.generate_candidates(query, perspectives, max_tokens)
        
        # Score
        scored = self.score_candidates(candidates)
        
        # Select or combine
        if combine:
            final_response = self.combine_insights(candidates, query)
        else:
            final_response = self.select_best(candidates)
        
        elapsed = time.time() - start_time
        
        return {
            "query": query,
            "candidates": [
                {
                    "perspective": sc.candidate.perspective,
                    "response": sc.candidate.response,
                    "score": sc.combined_score
                }
                for sc in scored
            ],
            "final_response": final_response,
            "method": "combined" if combine else "best_selected",
            "elapsed_seconds": elapsed,
            "timestamp": datetime.now().isoformat()
        }


# Export for modular imports
__all__ = ['ParallelBeamSearch', 'Candidate', 'ScoredCandidate', 'MLX_AVAILABLE']
