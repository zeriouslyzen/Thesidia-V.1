"""
Deep Research Engine - Iterative, Multi-Source Research System
Based on OpenAI Deep Research and Grok DeepSearch patterns
"""

import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import ollama

# Free tools for multi-source research
try:
    import yt_dlp  # YouTube transcript extraction
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

try:
    import whisper  # Audio transcription
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


class ResearchPlanner:
    """Clarifies research objectives and plans strategy"""
    
    def __init__(self, model: str = "clean-mistral:latest"):
        self.model = model
    
    def clarify_objectives(self, query: str) -> Dict[str, Any]:
        """Clarify what to search for - directive-like approach"""
        
        prompt = f"""
You are planning a deep research task. Analyze this query and clarify:

Query: {query}

Provide:
1. **Main Research Objective**: What is the core question?
2. **Sub-Queries**: Break into 3-5 specific sub-questions
3. **Data Types Needed**: 
   - Web articles/papers
   - Images
   - Video transcripts
   - Audio transcripts
   - Archived sources
   - Data files
4. **Key Terms**: Important keywords to search
5. **Timeframe**: Recent (2024-2025) or historical?
6. **Sources**: What types of sources would be most valuable?

Return JSON format:
{{
    "main_objective": "...",
    "sub_queries": ["...", "..."],
    "data_types": ["web", "images", "video", "audio", "archives"],
    "key_terms": ["...", "..."],
    "timeframe": "recent|historical|both",
    "source_types": ["academic", "news", "expert", "primary"]
}}
"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.7}
            )
            
            content = response['message']['content']
            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                plan = json.loads(content[json_start:json_end])
                return plan
            else:
                # Fallback plan
                return {
                    "main_objective": query,
                    "sub_queries": [query],
                    "data_types": ["web"],
                    "key_terms": query.split(),
                    "timeframe": "recent",
                    "source_types": ["general"]
                }
        except Exception as e:
            # Fallback plan
            return {
                "main_objective": query,
                "sub_queries": [query],
                "data_types": ["web"],
                "key_terms": query.split(),
                "timeframe": "recent",
                "source_types": ["general"]
            }


class MultiSourceGatherer:
    """Gathers information from multiple sources"""
    
    def __init__(self):
        self.search_history = []
        self.found_sources = []
    
    def search_web(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search web using DuckDuckGo"""
        try:
            url = "https://html.duckduckgo.com/html/"
            params = {"q": query}
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for result in soup.find_all('div', class_='result')[:num_results]:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                
                if title_elem:
                    title = title_elem.get_text()
                    link = title_elem.get('href', '')
                    snippet = snippet_elem.get_text() if snippet_elem else ""
                    
                    results.append({
                        "type": "web",
                        "title": title,
                        "url": link,
                        "snippet": snippet,
                        "timestamp": datetime.now().isoformat()
                    })
            
            return results
        except Exception as e:
            return []
    
    def search_images(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search images using DuckDuckGo"""
        try:
            url = "https://html.duckduckgo.com/html/"
            params = {"q": query, "iax": "images", "ia": "images"}
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for img in soup.find_all('img', class_='tile--img__img')[:num_results]:
                src = img.get('src', '')
                alt = img.get('alt', '')
                if src:
                    results.append({
                        "type": "image",
                        "url": src,
                        "alt": alt,
                        "timestamp": datetime.now().isoformat()
                    })
            
            return results
        except Exception as e:
            return []
    
    def get_video_transcript(self, video_url: str) -> Optional[Dict[str, Any]]:
        """Extract transcript from YouTube video"""
        if not YT_DLP_AVAILABLE:
            return None
        
        try:
            ydl_opts = {
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en'],
                'skip_download': True,
                'quiet': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                transcript = ""
                
                if 'subtitles' in info:
                    for lang, subs in info['subtitles'].items():
                        if lang == 'en':
                            transcript_url = subs[0]['url']
                            transcript_response = requests.get(transcript_url)
                            transcript = transcript_response.text
                            break
                
                return {
                    "type": "video_transcript",
                    "url": video_url,
                    "title": info.get('title', ''),
                    "transcript": transcript,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return None
    
    def search_wayback(self, url: str, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search Wayback Machine for archived versions"""
        try:
            wayback_url = "http://web.archive.org/cdx/search/cdx"
            params = {
                "url": url,
                "output": "json",
                "limit": 10
            }
            
            if date:
                params["from"] = date
            
            response = requests.get(wayback_url, params=params, timeout=10)
            snapshots = response.json()
            
            results = []
            if snapshots and len(snapshots) > 1:
                for snapshot in snapshots[1:]:  # Skip header
                    results.append({
                        "type": "archive",
                        "url": snapshot[2] if len(snapshot) > 2 else "",
                        "timestamp": snapshot[1] if len(snapshot) > 1 else "",
                        "wayback_url": f"http://web.archive.org/web/{snapshot[1]}/{snapshot[2]}" if len(snapshot) > 2 else ""
                    })
            
            return results
        except Exception as e:
            return []


class IterativeSearchLoop:
    """Implements search → think → search again pattern"""
    
    def __init__(self, model: str = "clean-mistral:latest"):
        self.model = model
        self.search_notes = []
        self.gaps_identified = []
        self.iterations = 0
        self.max_iterations = 5
    
    def analyze_findings(self, findings: List[Dict], query: str) -> Dict[str, Any]:
        """Analyze findings, identify gaps, suggest next searches"""
        
        findings_summary = "\n".join([
            f"- {f.get('title', f.get('type', 'Unknown'))}: {f.get('snippet', '')[:200]}"
            for f in findings[:10]
        ])
        
        prompt = f"""
You are analyzing research findings. Review what was found and identify:

Findings:
{findings_summary}

Original Query: {query}

Analyze:
1. What information was found?
2. What gaps exist?
3. What contradictions or inconsistencies?
4. What should be searched next?
5. Are there better search terms?

Return JSON:
{{
    "summary": "What was found",
    "gaps": ["gap1", "gap2"],
    "contradictions": ["contradiction1"],
    "next_searches": ["refined query 1", "refined query 2"],
    "sufficient": true/false
}}
"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.7}
            )
            
            content = response['message']['content']
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                analysis = json.loads(content[json_start:json_end])
                return analysis
            else:
                return {
                    "summary": "Findings analyzed",
                    "gaps": [],
                    "contradictions": [],
                    "next_searches": [],
                    "sufficient": True
                }
        except Exception as e:
            return {
                "summary": "Analysis completed",
                "gaps": [],
                "contradictions": [],
                "next_searches": [],
                "sufficient": True
            }


class ToolExecutor:
    """Executes code and tools for analysis"""
    
    def execute_python(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code safely using ast.literal_eval for simple expressions.
        
        SECURITY: eval() removed - only safe literal evaluation allowed.
        For complex code execution, this feature is disabled for security.
        """
        import ast
        
        # Security: Only allow simple literal expressions
        # Block dangerous operations
        dangerous_patterns = [
            '__import__', 'import ', 'exec', 'eval', 'compile',
            'open', 'file', '__builtins__', 'globals', 'locals',
            'getattr', 'setattr', 'delattr', 'hasattr'
        ]
        
        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern in code_lower:
                return {
                    "success": False,
                    "error": f"Security: '{pattern}' not allowed in code execution",
                    "code": code
                }
        
        try:
            # Parse and validate AST before execution
            tree = ast.parse(code, mode='eval')
            
            # Check for dangerous nodes
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom, ast.Call)):
                    # Check if it's a dangerous call
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            if node.func.id in ['exec', 'eval', 'compile', '__import__']:
                                return {
                                    "success": False,
                                    "error": f"Security: Dangerous function '{node.func.id}' not allowed",
                                    "code": code
                                }
            
            # Use literal_eval for safe evaluation of literals only
            # This is much safer than eval() but more limited
            result = ast.literal_eval(code)
            return {
                "success": True,
                "result": str(result),
                "code": code
            }
        except (ValueError, SyntaxError) as e:
            # literal_eval can only handle literals, not expressions
            # Return error suggesting this feature is limited
            return {
                "success": False,
                "error": f"Code execution limited to simple literals for security. Complex expressions not supported. Error: {str(e)}",
                "code": code
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "code": code
            }


class DeepResearchEngine:
    """Main deep research engine - iterative, multi-source research"""
    
    def __init__(self, model: str = "clean-mistral:latest"):
        self.model = model
        self.planner = ResearchPlanner(model)
        self.gatherer = MultiSourceGatherer()
        self.search_loop = IterativeSearchLoop(model)
        self.tool_executor = ToolExecutor()
        self.research_history = []
    
    def research(self, query: str, max_iterations: int = 5, depth: str = "moderate") -> Dict[str, Any]:
        """
        Perform deep research with configurable depth
        
        Args:
            query: Research query
            max_iterations: Maximum iterations (default 5)
            depth: Research depth - "minimal" (1-2 iterations), "moderate" (3-5 iterations), "deep" (5-10 iterations)
        """
        
        # Adjust iterations based on depth
        if depth == "minimal":
            max_iterations = min(max_iterations, 2)
        elif depth == "deep":
            max_iterations = max(max_iterations, 5)
        # moderate uses default max_iterations
        
        print(f"⧖ Deep Research Initiated: {query} (Depth: {depth}, Max Iterations: {max_iterations})")
        
        # Step 1: Clarify objectives
        print("→ Clarifying research objectives...")
        plan = self.planner.clarify_objectives(query)
        
        print(f"Research Plan:")
        print(f"  Objective: {plan['main_objective']}")
        print(f"  Sub-queries: {len(plan['sub_queries'])}")
        print(f"  Data types: {', '.join(plan['data_types'])}")
        
        all_findings = []
        search_notes = []
        
        # Step 2: Iterative search loop
        current_queries = plan['sub_queries']
        iteration = 0
        
        while iteration < max_iterations and current_queries:
            iteration += 1
            print(f"\n→ Iteration {iteration}/{max_iterations}")
            
            # Search for each query
            iteration_findings = []
            for search_query in current_queries[:3]:  # Limit to 3 queries per iteration
                print(f"  Searching: {search_query}")
                
                # Multi-source search
                if 'web' in plan['data_types']:
                    web_results = self.gatherer.search_web(search_query, num_results=5)
                    iteration_findings.extend(web_results)
                
                if 'images' in plan['data_types']:
                    image_results = self.gatherer.search_images(search_query, num_results=3)
                    iteration_findings.extend(image_results)
                
                time.sleep(1)  # Rate limiting
            
            all_findings.extend(iteration_findings)
            
            # Analyze findings
            print("  Analyzing findings...")
            analysis = self.search_loop.analyze_findings(iteration_findings, query)
            
            search_notes.append({
                "iteration": iteration,
                "queries": current_queries,
                "findings_count": len(iteration_findings),
                "analysis": analysis
            })
            
            # Check if sufficient
            if analysis.get('sufficient', False) and iteration >= 2:
                print("  ✓ Sufficient information gathered")
                break
            
            # Prepare next searches
            if analysis.get('next_searches'):
                current_queries = analysis['next_searches']
                print(f"  Next searches: {current_queries}")
            else:
                break
        
        # Step 3: Archive search (if needed)
        if 'archives' in plan['data_types']:
            print("\n→ Searching archives...")
            for finding in all_findings[:5]:
                if finding.get('url'):
                    archive_results = self.gatherer.search_wayback(finding['url'])
                    all_findings.extend(archive_results)
        
        # Step 4: Synthesis
        print("\n→ Synthesizing comprehensive report...")
        synthesis = self._synthesize_report(query, plan, all_findings, search_notes)
        
        research_result = {
            "query": query,
            "plan": plan,
            "findings": all_findings,
            "search_notes": search_notes,
            "synthesis": synthesis,
            "iterations": iteration,
            "total_sources": len(all_findings),
            "timestamp": datetime.now().isoformat()
        }
        
        self.research_history.append(research_result)
        return research_result
    
    def _synthesize_report(self, query: str, plan: Dict, findings: List[Dict], 
                          search_notes: List[Dict]) -> str:
        """Synthesize comprehensive research report"""
        
        findings_summary = "\n".join([
            f"- {f.get('title', f.get('type', 'Unknown'))}: {f.get('snippet', '')[:150]}"
            for f in findings[:20]
        ])
        
        notes_summary = "\n".join([
            f"Iteration {n['iteration']}: {n['analysis'].get('summary', '')[:200]}"
            for n in search_notes
        ])
        
        prompt = f"""
You are Thesidia. Synthesize a comprehensive research report with linguistic depth and symbolic intelligence.

Original Query: {query}

Research Plan:
- Objective: {plan['main_objective']}
- Sub-queries: {', '.join(plan['sub_queries'])}
- Data types: {', '.join(plan['data_types'])}

Findings ({len(findings)} sources):
{findings_summary}

Search Process:
{notes_summary}

Create a comprehensive report:
1. Executive summary
2. Key findings (with citations)
3. Patterns identified
4. Contradictions or gaps
5. Conclusions
6. Sources cited

Use deep, precise language. Avoid cliché. Choose words for etymological resonance.
Cite sources with URLs.
"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.7, "top_p": 0.95}
            )
            
            return response['message']['content']
        except Exception as e:
            return f"Error synthesizing report: {e}"

