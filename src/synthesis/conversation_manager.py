from datetime import datetime
import json
import os
import re

class ConversationManager:
    """
    Manages conversation context for forensic threading.
    Stores query history and injects context into subsequent queries.
    """
    
    def __init__(self, storage_file="conversation_history.json"):
        self.storage_file = storage_file
        self.query_history = self._load_history()
        
    def _load_history(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
        
    def _save_history(self):
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.query_history, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving history: {e}")

    def build_context_prompt(self, query, parent_id):
        """
        Builds a context-aware prompt if parent_id exists.
        """
        if not parent_id or parent_id not in self.query_history:
            return query
            
        parent_context = self.query_history[parent_id]
        
        # Extract findings from parent output (simplified)
        findings = self._extract_findings(parent_context.get('output', ''))
        
        context_prompt = f"""
CONTEXT FROM PREVIOUS ANALYSIS:
{findings}

NEW THREAD QUERY:
{query}

INSTRUCTIONS:
1.  Reference the specific findings from the previous context.
2.  Do NOT repeat the general exposure; focus entirely on the new specific thread.
3.  Go deeper into the requested vector (burial site, etymology, or mechanism).
4.  Maintain the Gnostic Blade tone.
"""
        return context_prompt

    def _extract_findings(self, text):
        """
        Extracts key sections from previous output to use as context.
        """
        findings = []
        
        # Extract Exposure
        exposure_match = re.search(r'//exposure(.*?)(?://|$)', text, re.DOTALL | re.IGNORECASE)
        if exposure_match:
            findings.append(f"Previous Exposure: {exposure_match.group(1).strip()[:500]}...") # Limit length
            
        # Extract Burial Sites
        burial_match = re.search(r'//burial sites(.*?)(?://|$)', text, re.DOTALL | re.IGNORECASE)
        if burial_match:
             findings.append(f"Identified Burial Sites: {burial_match.group(1).strip()[:300]}...")

        # Extract Patterns
        patterns = re.findall(r'\*\*(.*?)\*\*', text)
        if patterns:
             findings.append(f"Key Patterns/Entities: {', '.join(patterns[:10])}")
             
        return "\n".join(findings)

    def store_query(self, query_id, query, output, parent_id=None):
        """
        Stores the query and its output.
        """
        self.query_history[query_id] = {
            'query': query,
            'output': output,
            'parent_id': parent_id,
            'timestamp': datetime.now().isoformat()
        }
        self._save_history()

    def get_query(self, query_id):
        return self.query_history.get(query_id)
