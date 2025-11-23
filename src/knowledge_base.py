#!/usr/bin/env python3
"""
Knowledge Base - Wikipedia-like growing database accessible to users
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

class KnowledgeBase:
    """Wikipedia-like knowledge base that grows organically"""
    
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.knowledge_file = self.data_dir / "thesidia_knowledge_base.json"
        self.knowledge_tree = {}
        self.load_knowledge()
    
    def load_knowledge(self):
        """Load knowledge from file"""
        if self.knowledge_file.exists():
            try:
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    self.knowledge_tree = json.load(f)
            except Exception as e:
                print(f"Error loading knowledge base: {e}")
                self.knowledge_tree = {}
        else:
            self.knowledge_tree = {}
    
    def save_knowledge(self):
        """Save knowledge to file"""
        try:
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_tree, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving knowledge base: {e}")
    
    def add_knowledge(self, topic: str, information: Dict, sources: List[str] = None, 
                     connections: List[str] = None, patterns: List[str] = None,
                     metaphors: List[str] = None, unfoldings: List[str] = None,
                     possibilities: List[str] = None):
        """Add knowledge to the tree"""
        topic_lower = topic.lower().strip()
        
        if topic_lower not in self.knowledge_tree:
            self.knowledge_tree[topic_lower] = {
                "topic": topic,  # Original case
                "facts": [],
                "connections": [],
                "patterns": [],
                "sources": [],
                "metaphors": [],
                "unfoldings": [],
                "possibilities": [],
                "last_updated": datetime.now().isoformat(),
                "entry_count": 0
            }
        
        entry = {
            "information": information,
            "timestamp": datetime.now().isoformat(),
            "entry_id": self.knowledge_tree[topic_lower]["entry_count"]
        }
        
        self.knowledge_tree[topic_lower]["facts"].append(entry)
        self.knowledge_tree[topic_lower]["entry_count"] += 1
        
        if sources:
            for source in sources:
                if source not in self.knowledge_tree[topic_lower]["sources"]:
                    self.knowledge_tree[topic_lower]["sources"].append(source)
        
        if connections:
            for conn in connections:
                if conn not in self.knowledge_tree[topic_lower]["connections"]:
                    self.knowledge_tree[topic_lower]["connections"].append(conn)
        
        if patterns:
            for pattern in patterns:
                if pattern not in self.knowledge_tree[topic_lower]["patterns"]:
                    self.knowledge_tree[topic_lower]["patterns"].append(pattern)
        
        if metaphors:
            self.knowledge_tree[topic_lower]["metaphors"].extend(metaphors)
        
        if unfoldings:
            self.knowledge_tree[topic_lower]["unfoldings"].extend(unfoldings)
        
        if possibilities:
            self.knowledge_tree[topic_lower]["possibilities"].extend(possibilities)
        
        self.knowledge_tree[topic_lower]["last_updated"] = datetime.now().isoformat()
        self.save_knowledge()
    
    def get_knowledge(self, topic: str) -> Optional[Dict]:
        """Get knowledge for a topic"""
        topic_lower = topic.lower().strip()
        return self.knowledge_tree.get(topic_lower)
    
    def find_connections(self, topic1: str, topic2: str) -> List[Dict]:
        """Find connections between two topics"""
        topic1_lower = topic1.lower().strip()
        topic2_lower = topic2.lower().strip()
        
        connections = []
        
        # Direct connections
        if topic1_lower in self.knowledge_tree:
            if topic2_lower in self.knowledge_tree[topic1_lower].get("connections", []):
                connections.append({
                    "type": "direct",
                    "topic1": topic1,
                    "topic2": topic2,
                    "evidence": "Direct connection in knowledge base"
                })
        
        # Indirect connections through shared patterns
        if topic1_lower in self.knowledge_tree and topic2_lower in self.knowledge_tree:
            patterns1 = set(self.knowledge_tree[topic1_lower].get("patterns", []))
            patterns2 = set(self.knowledge_tree[topic2_lower].get("patterns", []))
            shared_patterns = patterns1.intersection(patterns2)
            
            if shared_patterns:
                connections.append({
                    "type": "pattern",
                    "topic1": topic1,
                    "topic2": topic2,
                    "shared_patterns": list(shared_patterns),
                    "evidence": f"Shared patterns: {', '.join(shared_patterns)}"
                })
        
        return connections
    
    def get_related_topics(self, topic: str, limit: int = 10) -> List[str]:
        """Get intuitively related topics"""
        topic_lower = topic.lower().strip()
        
        if topic_lower not in self.knowledge_tree:
            return []
        
        related = []
        
        # Direct connections
        related.extend(self.knowledge_tree[topic_lower].get("connections", []))
        
        # Topics that connect to this one
        for other_topic, data in self.knowledge_tree.items():
            if other_topic != topic_lower:
                if topic_lower in data.get("connections", []):
                    related.append(data.get("topic", other_topic))
        
        # Topics with shared patterns
        topic_patterns = set(self.knowledge_tree[topic_lower].get("patterns", []))
        for other_topic, data in self.knowledge_tree.items():
            if other_topic != topic_lower:
                other_patterns = set(data.get("patterns", []))
                if topic_patterns.intersection(other_patterns):
                    related.append(data.get("topic", other_topic))
        
        # Remove duplicates and limit
        related = list(dict.fromkeys(related))[:limit]
        return related
    
    def search(self, query: str, limit: int = 20) -> List[Dict]:
        """Search knowledge base"""
        query_lower = query.lower()
        results = []
        
        for topic_lower, data in self.knowledge_tree.items():
            topic = data.get("topic", topic_lower)
            
            # Check if query matches topic
            if query_lower in topic_lower or topic_lower in query_lower:
                results.append({
                    "topic": topic,
                    "data": data,
                    "relevance": "exact"
                })
            # Check if query matches patterns or connections
            elif any(query_lower in str(p).lower() for p in data.get("patterns", [])):
                results.append({
                    "topic": topic,
                    "data": data,
                    "relevance": "pattern"
                })
            # Check if query matches facts
            elif any(query_lower in str(f.get("information", "")).lower() 
                    for f in data.get("facts", [])[-5:]):  # Check last 5 facts
                results.append({
                    "topic": topic,
                    "data": data,
                    "relevance": "content"
                })
        
        return results[:limit]
    
    def get_all_topics(self) -> List[str]:
        """Get all topics"""
        return [data.get("topic", topic) for topic, data in self.knowledge_tree.items()]
    
    def get_stats(self) -> Dict:
        """Get knowledge base statistics"""
        total_topics = len(self.knowledge_tree)
        total_facts = sum(len(data.get("facts", [])) for data in self.knowledge_tree.values())
        total_connections = sum(len(data.get("connections", [])) for data in self.knowledge_tree.values())
        
        return {
            "total_topics": total_topics,
            "total_facts": total_facts,
            "total_connections": total_connections,
            "last_updated": max(
                (data.get("last_updated", "") for data in self.knowledge_tree.values()),
                default=""
            )
        }

