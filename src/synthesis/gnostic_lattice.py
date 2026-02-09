
import json
import os
import networkx as nx
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class GnosticLattice:
    """
    The Gnostic Lattice: A self-growing, symbolic knowledge graph.
    Acts as the long-term memory for the forensic system, storing
    symbolic density (weights) of entities and their relationships.
    """
    
    def __init__(self, storage_file="data/gnostic_lattice.json"):
        self.storage_file = storage_file
        self.graph = nx.DiGraph()
        self._load_lattice()
        
    def _load_lattice(self):
        """Load graph from JSON file if exists."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.graph = nx.node_link_graph(data)
            except Exception as e:
                print(f"Error loading Gnostic Lattice: {e}")
                self.graph = nx.DiGraph()
        else:
            self.graph = nx.DiGraph()

    def save_lattice(self):
        """Save graph to JSON file."""
        try:
            # Ensure directory exists
            Path(self.storage_file).parent.mkdir(parents=True, exist_ok=True)
            
            data = nx.node_link_data(self.graph)
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving Gnostic Lattice: {e}")

    def update(self, entities: List[str], relations: List[tuple], context_id: str = None):
        """
        Update the lattice with new entities and relationships.
        
        Args:
            entities: List of entity names detected
            relations: List of (source, target, relation_type) tuples
            context_id: Query ID for lineage
        """
        timestamp = datetime.now().isoformat()
        
        # 1. Update Nodes (Entities)
        for entity in entities:
            entity = entity.strip()  # Normalize
            if not entity: continue
            
            if self.graph.has_node(entity):
                # Reinforcement: Increase weight
                self.graph.nodes[entity]['weight'] += 1
                self.graph.nodes[entity]['last_seen'] = timestamp
            else:
                # Genesis: Create new node
                self.graph.add_node(entity, weight=1, first_seen=timestamp, last_seen=timestamp, type="entity")

        # 2. Update Edges (Relationships)
        for source, target, rel_type in relations:
            source = source.strip()
            target = target.strip()
            if not source or not target: continue
            
            # Ensure nodes exist (if implicit relationship found between new entities)
            if not self.graph.has_node(source):
                self.graph.add_node(source, weight=1, first_seen=timestamp, last_seen=timestamp, type="entity")
            if not self.graph.has_node(target):
                self.graph.add_node(target, weight=1, first_seen=timestamp, last_seen=timestamp, type="entity")
                
            if self.graph.has_edge(source, target):
                # Reinforce connection
                self.graph[source][target]['weight'] += 1
                # Append context ID if not present
                if context_id and context_id not in self.graph[source][target].get('contexts', []):
                    self.graph[source][target].setdefault('contexts', []).append(context_id)
            else:
                # Create new connection
                self.graph.add_edge(source, target, weight=1, relation=rel_type, first_seen=timestamp, contexts=[context_id] if context_id else [])

        # Auto-save on significant updates (can be optimized to batch)
        self.save_lattice()

    def get_burning_nodes(self, limit=10):
        """Return the top nodes by weight (Symbolic Density)."""
        nodes = sorted(
            self.graph.nodes(data=True), 
            key=lambda x: x[1].get('weight', 0), 
            reverse=True
        )
        return [{"id": n[0], **n[1]} for n in nodes[:limit]]

    def get_full_graph_data(self):
        """Return D3-compatible graph data."""
        return nx.node_link_data(self.graph)
