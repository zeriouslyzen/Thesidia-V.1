#!/usr/bin/env python3
"""
Parallel Processor - Runs web search and LLM thinking in parallel
Optimized for Mac with Neural Engine support exploration
"""

import asyncio
import concurrent.futures
import time
from typing import Dict, List, Optional, Any, Tuple
import ollama


class ParallelProcessor:
    """
    Parallel processing system that runs web search and LLM thinking simultaneously
    Optimized for Mac Neural Engine when available
    """
    
    def __init__(self, model: str = "clean-mistral:latest", web_search_engine=None):
        self.model = model
        self.web_search = web_search_engine
        self.is_mac = self._detect_mac()
        self.neural_engine_available = self._check_neural_engine()
    
    def _detect_mac(self) -> bool:
        """Detect if running on Mac"""
        import platform
        return platform.system() == "Darwin"
    
    def _check_neural_engine(self) -> bool:
        """Check if Neural Engine is available (Mac with Apple Silicon)"""
        if not self.is_mac:
            return False
        
        try:
            import platform
            # Check for Apple Silicon (M1, M2, M3, etc.)
            machine = platform.machine()
            if machine in ["arm64", "arm64e"]:
                return True
        except Exception:
            pass
        
        return False
    
    def process_parallel(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Process query with parallel web search and LLM thinking
        Returns both web results and initial LLM analysis
        """
        start_time = time.time()
        
        # Run web search and LLM thinking in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Submit both tasks
            web_future = executor.submit(self._web_search_task, query, num_results)
            llm_future = executor.submit(self._llm_thinking_task, query)
            
            # Wait for both to complete
            web_results = web_future.result()
            llm_analysis = llm_future.result()
        
        elapsed = time.time() - start_time
        
        return {
            "web_results": web_results,
            "llm_analysis": llm_analysis,
            "processing_time": elapsed,
            "parallel": True,
            "neural_engine": self.neural_engine_available
        }
    
    def _web_search_task(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Web search task (runs in parallel)"""
        if not self.web_search:
            return []
        
        try:
            return self.web_search.search_and_scrape(query, num_results=num_results)
        except Exception as e:
            print(f"Warning: Web search failed: {e}")
            return []
    
    def _llm_thinking_task(self, query: str) -> Dict[str, Any]:
        """
        LLM thinking task (runs in parallel with web search)
        Performs initial analysis, identifies knowledge gaps, suggests research angles
        """
        thinking_prompt = f"""Analyze this query and provide initial thinking:

Query: {query}

Perform initial analysis:
1. What is this query asking about?
2. What knowledge gaps might exist?
3. What research angles should be explored?
4. What domains/fields are relevant?
5. What patterns or connections might be important?

Keep this brief (200-300 words). This is initial thinking, not a full answer.

Initial Analysis:"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": thinking_prompt}],
                options={
                    "temperature": 0.7,
                    "num_predict": 500,  # Brief thinking, not full response
                    "top_p": 0.9
                }
            )
            
            analysis = response['message']['content'].strip()
            
            # Extract key insights
            return {
                "analysis": analysis,
                "knowledge_gaps": self._extract_knowledge_gaps(analysis),
                "research_angles": self._extract_research_angles(analysis),
                "domains": self._extract_domains(analysis)
            }
            
        except Exception as e:
            print(f"Warning: LLM thinking failed: {e}")
            return {
                "analysis": "",
                "knowledge_gaps": [],
                "research_angles": [],
                "domains": []
            }
    
    def _extract_knowledge_gaps(self, text: str) -> List[str]:
        """Extract knowledge gaps from analysis"""
        gaps = []
        text_lower = text.lower()
        
        gap_indicators = [
            "knowledge gap", "don't know", "uncertain", "unclear", "unknown",
            "need to research", "requires investigation", "not available"
        ]
        
        sentences = text.split('.')
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in gap_indicators):
                gaps.append(sentence.strip())
        
        return gaps[:3]  # Top 3 gaps
    
    def _extract_research_angles(self, text: str) -> List[str]:
        """Extract research angles from analysis"""
        angles = []
        text_lower = text.lower()
        
        angle_indicators = [
            "research", "explore", "investigate", "examine", "analyze",
            "should look into", "need to find", "search for"
        ]
        
        sentences = text.split('.')
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in angle_indicators):
                angles.append(sentence.strip())
        
        return angles[:3]  # Top 3 angles
    
    def _extract_domains(self, text: str) -> List[str]:
        """Extract relevant domains from analysis"""
        domains = []
        
        domain_keywords = {
            "history": ["history", "historical", "ancient", "past"],
            "science": ["science", "scientific", "research", "study"],
            "philosophy": ["philosophy", "philosophical", "theory", "concept"],
            "technology": ["technology", "tech", "digital", "computer"],
            "religion": ["religion", "religious", "spiritual", "faith"],
            "politics": ["politics", "political", "government", "power"],
            "culture": ["culture", "cultural", "society", "social"]
        }
        
        text_lower = text.lower()
        for domain, keywords in domain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                domains.append(domain)
        
        return domains[:5]  # Top 5 domains
    
    def optimize_for_neural_engine(self) -> Dict[str, Any]:
        """
        Provide recommendations for Neural Engine optimization
        Returns configuration suggestions for Mac Neural Engine
        """
        if not self.neural_engine_available:
            return {
                "available": False,
                "recommendations": ["Not running on Apple Silicon Mac"]
            }
        
        recommendations = [
            "Use MLX framework for Neural Engine acceleration",
            "Consider using smaller models optimized for Neural Engine",
            "Batch processing for better Neural Engine utilization",
            "Use Core ML for model conversion if available",
            "Consider ANEMLL or Swama for Neural Engine LLM execution"
        ]
        
        return {
            "available": True,
            "recommendations": recommendations,
            "framework_options": [
                "MLX (Apple's framework)",
                "ANEMLL (Neural Engine LLM port)",
                "Swama (macOS optimized)",
                "Core ML (Apple's ML framework)"
            ]
        }


class AsyncParallelProcessor:
    """
    Async version for even better parallelization
    Uses asyncio for non-blocking operations
    """
    
    def __init__(self, model: str = "clean-mistral:latest", web_search_engine=None):
        self.model = model
        self.web_search = web_search_engine
    
    async def process_async(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Process query with async parallel operations"""
        start_time = time.time()
        
        # Run both tasks concurrently
        web_task = asyncio.create_task(self._async_web_search(query, num_results))
        llm_task = asyncio.create_task(self._async_llm_thinking(query))
        
        # Wait for both
        web_results, llm_analysis = await asyncio.gather(web_task, llm_task)
        
        elapsed = time.time() - start_time
        
        return {
            "web_results": web_results,
            "llm_analysis": llm_analysis,
            "processing_time": elapsed,
            "async": True
        }
    
    async def _async_web_search(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Async web search"""
        if not self.web_search:
            return []
        
        # Run in thread pool (web search is I/O bound)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.web_search.search_and_scrape,
            query,
            num_results
        )
    
    async def _async_llm_thinking(self, query: str) -> Dict[str, Any]:
        """Async LLM thinking"""
        thinking_prompt = f"""Analyze this query and provide initial thinking:

Query: {query}

Perform initial analysis:
1. What is this query asking about?
2. What knowledge gaps might exist?
3. What research angles should be explored?

Keep this brief (200-300 words).

Initial Analysis:"""
        
        # Run in thread pool (Ollama is I/O bound)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": thinking_prompt}],
                options={"temperature": 0.7, "num_predict": 500}
            )
        )
        
        analysis = response['message']['content'].strip()
        
        return {
            "analysis": analysis,
            "knowledge_gaps": [],
            "research_angles": [],
            "domains": []
        }

