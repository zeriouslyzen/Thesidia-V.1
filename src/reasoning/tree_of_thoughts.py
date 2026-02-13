#!/usr/bin/env python3
"""
Tree of Thoughts
================

Multi-path reasoning engine that explores queries from multiple perspectives simultaneously.
Enables deeper analysis by exploring historical, pattern, etymological, and cross-domain paths.

Part of Phase 1: Advanced Reasoning implementation.
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
    from model_router import ModelRouter
except ImportError:
    ModelRouter = None

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    ollama = None
    OLLAMA_AVAILABLE = False


@dataclass
class ThoughtPath:
    """Represents a single exploration path in the tree"""
    perspective: str
    prompt: str
    response: str = ""
    score: float = 0.0
    depth: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScoredPath:
    """A thought path with evaluation score"""
    path: ThoughtPath
    quality_score: float = 0.0
    relevance_score: float = 0.0
    depth_score: float = 0.0
    combined_score: float = 0.0


class TreeOfThoughts:
    """
    Multi-path reasoning engine for deep analysis.
    
    Explores queries from 4 perspectives:
    1. Historical - Origins, evolution, timeline
    2. Pattern - Recurring themes, connections
    3. Etymological - Language roots, meaning shifts
    4. Cross-domain - Connections to other fields
    """
    
    DEFAULT_PERSPECTIVES = [
        {
            "name": "historical",
            "description": "Origins, evolution, timeline analysis",
            "prompt_template": """Explore this query from a HISTORICAL perspective:

Query: {query}

Focus on:
- What are the origins and earliest traces?
- How has this evolved over time?
- What historical events or periods are relevant?
- What was lost or transformed through history?

{sources_context}

Provide deep historical analysis. Be specific with dates, periods, and transformations."""
        },
        {
            "name": "pattern",
            "description": "Recurring themes, connections, cycles",
            "prompt_template": """Explore this query from a PATTERN RECOGNITION perspective:

Query: {query}

Focus on:
- What patterns repeat across cultures, times, or domains?
- What cycles or rhythms appear?
- What connections exist that aren't immediately obvious?
- What structural similarities emerge?

{sources_context}

Identify patterns that reveal deeper truths. Connect disparate elements."""
        },
        {
            "name": "etymological",
            "description": "Language roots, semantic shifts, meaning archaeology",
            "prompt_template": """Explore this query from an ETYMOLOGICAL perspective:

Query: {query}

Focus on:
- What are the root words and their original meanings?
- How have meanings shifted over time?
- What do different languages reveal about this concept?
- What was encoded in the original language that was lost?

{sources_context}

Trace words to their roots. Show how language preserves hidden truths."""
        },
        {
            "name": "cross_domain",
            "description": "Connections across fields, interdisciplinary insights",
            "prompt_template": """Explore this query from a CROSS-DOMAIN perspective:

Query: {query}

Focus on:
- What connections exist to other fields (science, philosophy, art, etc.)?
- What insights from unrelated domains apply here?
- What universal principles emerge?
- How do different disciplines view this?

{sources_context}

Bridge domains. Show how knowledge in one area illuminates another."""
        }
    ]
    
    def __init__(self, model: str = "clean-mistral:latest", model_client: Optional[ModelClient] = None):
        self.model = model
        self.model_client = model_client
        self.model_router = ModelRouter() if ModelRouter else None
        self.perspectives = self.DEFAULT_PERSPECTIVES.copy()
        self.exploration_history = []
    
    def explore_paths(
        self,
        query: str,
        sources: List[Dict[str, Any]] = None,
        num_paths: int = 4,
        parallel: bool = True,
        max_tokens: int = 2000
    ) -> List[ThoughtPath]:
        """
        Explore query from multiple perspectives.
        
        Args:
            query: The question or topic to explore
            sources: Optional source documents for context
            num_paths: Number of perspectives to explore (1-4)
            parallel: Whether to explore paths in parallel
            max_tokens: Maximum tokens per path response
            
        Returns:
            List of ThoughtPath objects with exploration results
        """
        # Limit paths to available perspectives
        num_paths = min(num_paths, len(self.perspectives))
        selected_perspectives = self.perspectives[:num_paths]
        
        # Build sources context
        sources_context = self._build_sources_context(sources) if sources else ""
        
        # Create thought paths
        paths = []
        for perspective in selected_perspectives:
            prompt = perspective["prompt_template"].format(
                query=query,
                sources_context=sources_context
            )
            paths.append(ThoughtPath(
                perspective=perspective["name"],
                prompt=prompt,
                metadata={"description": perspective["description"]}
            ))
        
        # Explore paths
        if parallel and len(paths) > 1:
            paths = self._explore_parallel(paths, max_tokens)
        else:
            paths = self._explore_sequential(paths, max_tokens)
        
        # Record history
        self.exploration_history.append({
            "query": query,
            "paths": len(paths),
            "timestamp": datetime.now().isoformat()
        })
        
        return paths
    
    def _explore_parallel(self, paths: List[ThoughtPath], max_tokens: int) -> List[ThoughtPath]:
        """Explore multiple paths in parallel using thread pool"""
        with ThreadPoolExecutor(max_workers=min(len(paths), 4)) as executor:
            future_to_path = {
                executor.submit(self._generate_response, path, max_tokens): path
                for path in paths
            }
            
            completed_paths = []
            for future in as_completed(future_to_path, timeout=120):
                path = future_to_path[future]
                try:
                    response = future.result()
                    path.response = response
                    completed_paths.append(path)
                except Exception as e:
                    path.response = f"Error exploring {path.perspective}: {e}"
                    path.metadata["error"] = str(e)
                    completed_paths.append(path)
        
        return completed_paths
    
    def _explore_sequential(self, paths: List[ThoughtPath], max_tokens: int) -> List[ThoughtPath]:
        """Explore paths one at a time"""
        for path in paths:
            try:
                path.response = self._generate_response(path, max_tokens)
            except Exception as e:
                path.response = f"Error exploring {path.perspective}: {e}"
                path.metadata["error"] = str(e)
        return paths
    
    def _generate_response(self, path: ThoughtPath, max_tokens: int) -> str:
        """Generate response for a single path"""
        if self.model_client:
            response = self.model_client.chat(
                model=self.model,
                input_text=path.prompt,
                enhanced_base=f"You are exploring from a {path.perspective} perspective. Be thorough and insightful.",
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
                messages=[
                    {"role": "system", "content": f"You are exploring from a {path.perspective} perspective. Be thorough and insightful."},
                    {"role": "user", "content": path.prompt}
                ],
                options={
                    "temperature": 0.8,
                    "num_predict": max_tokens,
                    "top_p": 0.9
                }
            )
            return response['message']['content'] if isinstance(response, dict) and 'message' in response else (response.message.content if hasattr(response, 'message') else str(response))
        else:
            return f"No model available for {path.perspective} exploration"
    
    def _build_sources_context(self, sources: List[Dict[str, Any]]) -> str:
        """Build context string from source documents"""
        if not sources:
            return ""
        
        context_parts = ["Available source information:"]
        for i, source in enumerate(sources[:5], 1):  # Limit to 5 sources
            title = source.get("title", "Unknown")
            content = source.get("content", source.get("snippet", ""))[:500]
            if content:
                context_parts.append(f"[Source {i}] {title}: {content}")
        
        return "\n".join(context_parts)
    
    def evaluate_paths(self, paths: List[ThoughtPath]) -> List[ScoredPath]:
        """
        Evaluate and score each exploration path.
        
        Scoring criteria:
        - Quality: Depth, specificity, accuracy
        - Relevance: How well it addresses the query
        - Depth: Level of insight and analysis
        """
        scored_paths = []
        
        for path in paths:
            # Skip paths with errors
            if "Error" in path.response[:50]:
                scored_paths.append(ScoredPath(
                    path=path,
                    quality_score=0.0,
                    relevance_score=0.0,
                    depth_score=0.0,
                    combined_score=0.0
                ))
                continue
            
            # Heuristic scoring (can be enhanced with LLM-based evaluation)
            quality_score = self._score_quality(path.response)
            relevance_score = self._score_relevance(path)
            depth_score = self._score_depth(path.response)
            
            # Combined score (weighted average)
            combined_score = (quality_score * 0.4 + relevance_score * 0.3 + depth_score * 0.3)
            
            scored_paths.append(ScoredPath(
                path=path,
                quality_score=quality_score,
                relevance_score=relevance_score,
                depth_score=depth_score,
                combined_score=combined_score
            ))
        
        # Sort by combined score (highest first)
        scored_paths.sort(key=lambda x: x.combined_score, reverse=True)
        return scored_paths
    
    def _score_quality(self, response: str) -> float:
        """Score response quality based on heuristics"""
        score = 0.5
        
        # Length indicates depth (but not too long)
        length = len(response)
        if length > 500:
            score += 0.1
        if length > 1000:
            score += 0.1
        if length > 2000:
            score += 0.1
        
        # Specificity indicators
        specificity_markers = ["specifically", "for example", "such as", "in particular", "notably"]
        for marker in specificity_markers:
            if marker in response.lower():
                score += 0.05
        
        # Evidence indicators
        evidence_markers = ["evidence", "research", "study", "data", "source"]
        for marker in evidence_markers:
            if marker in response.lower():
                score += 0.05
        
        return min(1.0, score)
    
    def _score_relevance(self, path: ThoughtPath) -> float:
        """Score how well path addresses its perspective"""
        score = 0.5
        response = path.response.lower()
        
        perspective_keywords = {
            "historical": ["origin", "history", "century", "ancient", "evolved", "began", "period"],
            "pattern": ["pattern", "recurring", "cycle", "similar", "connection", "theme"],
            "etymological": ["root", "etymology", "language", "word", "meaning", "derives"],
            "cross_domain": ["domain", "field", "discipline", "science", "philosophy", "art"]
        }
        
        keywords = perspective_keywords.get(path.perspective, [])
        for keyword in keywords:
            if keyword in response:
                score += 0.07
        
        return min(1.0, score)
    
    def _score_depth(self, response: str) -> float:
        """Score depth of analysis"""
        score = 0.5
        
        # Paragraph count indicates thorough exploration
        paragraphs = response.split('\n\n')
        if len(paragraphs) >= 3:
            score += 0.1
        if len(paragraphs) >= 5:
            score += 0.1
        
        # Analysis indicators
        analysis_markers = ["because", "therefore", "suggests", "implies", "reveals", "indicates"]
        for marker in analysis_markers:
            if marker in response.lower():
                score += 0.05
        
        # Critical thinking indicators
        critical_markers = ["however", "although", "but", "alternatively", "on the other hand"]
        for marker in critical_markers:
            if marker in response.lower():
                score += 0.05
        
        return min(1.0, score)
    
    def synthesize_paths(
        self,
        paths: List[ThoughtPath],
        query: str,
        max_tokens: int = 4000
    ) -> str:
        """
        Synthesize multiple exploration paths into a coherent response.
        
        Args:
            paths: List of explored thought paths
            query: Original query for context
            max_tokens: Maximum tokens for synthesis
            
        Returns:
            Synthesized response combining insights from all paths
        """
        # Evaluate paths first
        scored_paths = self.evaluate_paths(paths)
        
        # Build synthesis prompt
        path_summaries = []
        for i, sp in enumerate(scored_paths, 1):
            path_summaries.append(f"""
**{sp.path.perspective.upper()} PERSPECTIVE** (score: {sp.combined_score:.2f})
{sp.path.response[:1500]}
""")
        
        synthesis_prompt = f"""Synthesize these multi-perspective explorations into a comprehensive response.

Original Query: {query}

EXPLORATIONS:
{''.join(path_summaries)}

SYNTHESIS TASK:
1. Identify the key insights from each perspective
2. Find connections and patterns across perspectives
3. Resolve any contradictions or tensions
4. Build a unified narrative that integrates all perspectives
5. Highlight the most important revelations

Write a comprehensive synthesis that weaves together historical origins, patterns, etymological insights, and cross-domain connections. Make the connections explicit. Show how different perspectives illuminate each other.

Write naturally, not as a list. Aim for deep, flowing prose that reveals deeper truths through synthesis."""

        # Generate synthesis
        if self.model_client:
            response = self.model_client.chat(
                model=self.model,
                input_text=synthesis_prompt,
                enhanced_base="You are a master synthesizer. Weave multiple perspectives into unified understanding.",
                options={
                    "temperature": 0.85,
                    "num_predict": max_tokens,
                    "top_p": 0.9
                }
            )
            return response.get('message', {}).get('content', '')
        elif OLLAMA_AVAILABLE:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a master synthesizer. Weave multiple perspectives into unified understanding."},
                    {"role": "user", "content": synthesis_prompt}
                ],
                options={
                    "temperature": 0.85,
                    "num_predict": max_tokens,
                    "top_p": 0.9
                }
            )
            return response['message']['content'] if isinstance(response, dict) and 'message' in response else (response.message.content if hasattr(response, 'message') else str(response))
        else:
            # Fallback: simple concatenation
            return "\n\n".join([f"## {p.perspective}\n{p.response}" for p in paths])
    
    def explore_and_synthesize(
        self,
        query: str,
        sources: List[Dict[str, Any]] = None,
        num_paths: int = 4,
        parallel: bool = True
    ) -> Dict[str, Any]:
        """
        Convenience method: explore paths and synthesize in one call.
        
        Returns:
            Dictionary with paths, scores, and synthesis
        """
        start_time = time.time()
        
        # Explore
        paths = self.explore_paths(query, sources, num_paths, parallel)
        
        # Evaluate
        scored_paths = self.evaluate_paths(paths)
        
        # Synthesize
        synthesis = self.synthesize_paths(paths, query)
        
        elapsed = time.time() - start_time
        
        return {
            "query": query,
            "paths": [
                {
                    "perspective": p.perspective,
                    "response": p.response,
                    "score": sp.combined_score
                }
                for p, sp in zip(paths, scored_paths)
            ],
            "synthesis": synthesis,
            "elapsed_seconds": elapsed,
            "timestamp": datetime.now().isoformat()
        }


# Export for modular imports
__all__ = ['TreeOfThoughts', 'ThoughtPath', 'ScoredPath']
