#!/usr/bin/env python3
"""
Streaming Processor - Real-time token streaming for better UX
Implements early stopping and quality thresholds
"""

import ollama
from typing import Iterator, Dict, Any, Optional, Callable, List
import time


class StreamingProcessor:
    """
    Streams LLM responses token-by-token
    Implements early stopping based on quality thresholds
    """
    
    def __init__(self, model: str = "clean-mistral:latest"):
        self.model = model
        self.quality_check_interval = 100  # Check quality every N tokens
        self.min_tokens = 50  # Minimum tokens before early stopping
        self.quality_threshold = 0.85  # Quality threshold for early stopping
    
    def stream_response(self, prompt: str, 
                       max_tokens: int = 10000,
                       temperature: float = 0.7,
                       quality_checker: Optional[Callable[[str, str], float]] = None) -> Iterator[Dict[str, Any]]:
        """
        Stream response token-by-token
        Yields: {"token": str, "complete": bool, "quality": float, "should_stop": bool}
        """
        accumulated = ""
        token_count = 0
        last_quality_check = 0
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens
                },
                stream=True  # Enable streaming
            )
            
            for chunk in response:
                if 'message' in chunk and 'content' in chunk['message']:
                    token = chunk['message']['content']
                    accumulated += token
                    token_count += 1
                    
                    # Yield token immediately
                    yield {
                        "token": token,
                        "accumulated": accumulated,
                        "token_count": token_count,
                        "complete": False,
                        "quality": None,
                        "should_stop": False
                    }
                    
                    # Check quality periodically
                    if token_count - last_quality_check >= self.quality_check_interval:
                        if token_count >= self.min_tokens and quality_checker:
                            quality = quality_checker(accumulated, prompt)
                            
                            # Check if we should stop early
                            should_stop = quality >= self.quality_threshold
                            
                            yield {
                                "token": "",
                                "accumulated": accumulated,
                                "token_count": token_count,
                                "complete": False,
                                "quality": quality,
                                "should_stop": should_stop
                            }
                            
                            if should_stop:
                                # Stop generation
                                break
                        
                        last_quality_check = token_count
            
            # Final yield
            yield {
                "token": "",
                "accumulated": accumulated,
                "token_count": token_count,
                "complete": True,
                "quality": None,
                "should_stop": False
            }
            
        except Exception as e:
            yield {
                "token": "",
                "accumulated": accumulated,
                "token_count": token_count,
                "complete": True,
                "error": str(e),
                "quality": None,
                "should_stop": False
            }
    
    def simple_quality_check(self, text: str, query: str) -> float:
        """
        Simple quality assessment
        Returns: 0.0 to 1.0 (higher = better)
        """
        # Basic heuristics
        quality = 0.5  # Base quality
        
        # Length check (too short = low quality)
        if len(text) < 100:
            quality -= 0.2
        elif len(text) > 500:
            quality += 0.1
        
        # Completeness check (has conclusion = better)
        conclusion_indicators = ["conclusion", "in summary", "in conclusion", "therefore", "thus", "overall"]
        if any(indicator in text.lower() for indicator in conclusion_indicators):
            quality += 0.2
        
        # Query relevance (mentions query terms = better)
        query_terms = set(query.lower().split())
        text_lower = text.lower()
        relevant_terms = sum(1 for term in query_terms if term in text_lower)
        if relevant_terms > 0:
            quality += min(0.2, relevant_terms * 0.05)
        
        # Coherence check (repetition = lower quality)
        sentences = text.split('.')
        if len(sentences) > 1:
            unique_sentences = len(set(sentences))
            repetition_ratio = unique_sentences / len(sentences)
            quality += (repetition_ratio - 0.5) * 0.2
        
        return max(0.0, min(1.0, quality))
    
    def stream_to_string(self, prompt: str, max_tokens: int = 10000,
                        temperature: float = 0.7,
                        quality_checker: Optional[Callable[[str, str], float]] = None) -> str:
        """
        Stream response and return complete string
        (For non-streaming use cases)
        """
        accumulated = ""
        for chunk in self.stream_response(prompt, max_tokens, temperature, quality_checker):
            if chunk.get("should_stop"):
                break
            if chunk.get("token"):
                accumulated += chunk["token"]
            if chunk.get("complete"):
                break
        
        return accumulated.strip()


class TreeOfThoughts:
    """
    Tree of Thoughts reasoning - explores multiple reasoning paths
    """
    
    def __init__(self, model: str = "clean-mistral:latest"):
        self.model = model
    
    def explore_paths(self, query: str, sources: List[Dict[str, Any]], 
                     num_paths: int = 4) -> List[Dict[str, Any]]:
        """
        Explore multiple reasoning paths in parallel
        Returns: List of path results with evaluations
        """
        paths = [
            self._historical_path(query, sources),
            self._pattern_path(query, sources),
            self._etymological_path(query, sources),
            self._cross_domain_path(query, sources)
        ]
        
        # Evaluate each path
        evaluated_paths = []
        for i, path_content in enumerate(paths[:num_paths]):
            evaluation = self._evaluate_path(path_content, query)
            evaluated_paths.append({
                "path_id": i,
                "content": path_content,
                "evaluation": evaluation,
                "score": evaluation.get("score", 0.0)
            })
        
        return evaluated_paths
    
    def _historical_path(self, query: str, sources: List[Dict[str, Any]]) -> str:
        """Historical analysis path"""
        prompt = f"""Analyze this query from a historical perspective:

Query: {query}

Sources: {self._format_sources(sources)}

Focus on:
- Historical context and timeline
- Evolution over time
- Historical patterns and cycles
- What changed and why

Historical Analysis:"""
        
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.8, "num_predict": 2000}
        )
        return response['message']['content'].strip()
    
    def _pattern_path(self, query: str, sources: List[Dict[str, Any]]) -> str:
        """Pattern recognition path"""
        prompt = f"""Analyze this query through pattern recognition:

Query: {query}

Sources: {self._format_sources(sources)}

Focus on:
- Recurring patterns across time and cultures
- Pattern recognition and connections
- What patterns emerge
- Cross-domain pattern matching

Pattern Analysis:"""
        
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.8, "num_predict": 2000}
        )
        return response['message']['content'].strip()
    
    def _etymological_path(self, query: str, sources: List[Dict[str, Any]]) -> str:
        """Etymological analysis path"""
        prompt = f"""Analyze this query through etymology and linguistic analysis:

Query: {query}

Sources: {self._format_sources(sources)}

Focus on:
- Word origins and etymology
- Linguistic transformations
- Meaning changes over time
- How language reveals hidden truths

Etymological Analysis:"""
        
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.8, "num_predict": 2000}
        )
        return response['message']['content'].strip()
    
    def _cross_domain_path(self, query: str, sources: List[Dict[str, Any]]) -> str:
        """Cross-domain synthesis path"""
        prompt = f"""Analyze this query through cross-domain synthesis:

Query: {query}

Sources: {self._format_sources(sources)}

Focus on:
- Connections across domains (history, science, culture, etc.)
- Cross-domain pattern recognition
- Synthesis of multiple perspectives
- New frameworks emerging from synthesis

Cross-Domain Analysis:"""
        
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.8, "num_predict": 2000}
        )
        return response['message']['content'].strip()
    
    def _evaluate_path(self, path_content: str, query: str) -> Dict[str, Any]:
        """Evaluate a reasoning path"""
        # Simple evaluation heuristics
        score = 0.5  # Base score
        
        # Length check
        if len(path_content) > 500:
            score += 0.1
        
        # Query relevance
        query_terms = set(query.lower().split())
        content_lower = path_content.lower()
        relevant_terms = sum(1 for term in query_terms if term in content_lower)
        if relevant_terms > 0:
            score += min(0.2, relevant_terms * 0.05)
        
        # Depth indicators
        depth_indicators = ["pattern", "connection", "analysis", "evidence", "synthesis"]
        depth_count = sum(1 for ind in depth_indicators if ind in content_lower)
        score += min(0.2, depth_count * 0.05)
        
        return {
            "score": max(0.0, min(1.0, score)),
            "length": len(path_content),
            "relevance": relevant_terms / max(1, len(query_terms))
        }
    
    def _format_sources(self, sources: List[Dict[str, Any]]) -> str:
        """Format sources for prompt"""
        if not sources:
            return "No sources provided"
        
        formatted = []
        for i, source in enumerate(sources[:5], 1):
            content = source.get("content", "")[:500]
            title = source.get("title", "Untitled")
            formatted.append(f"[Source {i}]: {title}\n{content}")
        
        return "\n\n".join(formatted)
    
    def synthesize_paths(self, paths: List[Dict[str, Any]], query: str) -> str:
        """
        Synthesize multiple paths into final response
        """
        # Sort by score
        sorted_paths = sorted(paths, key=lambda x: x['score'], reverse=True)
        
        # Take top paths
        top_paths = sorted_paths[:2]
        
        synthesis_prompt = f"""Synthesize these reasoning paths into a comprehensive response:

Query: {query}

Path 1 (Score: {top_paths[0]['score']:.2f}):
{top_paths[0]['content'][:1000]}

Path 2 (Score: {top_paths[1]['score']:.2f}):
{top_paths[1]['content'][:1000]}

Synthesize these paths into a comprehensive, flowing response that:
- Combines insights from both paths
- Maintains natural prose
- Provides deep analysis
- Connects patterns and evidence

Synthesis:"""
        
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": synthesis_prompt}],
            options={"temperature": 0.7, "num_predict": 3000}
        )
        return response['message']['content'].strip()

